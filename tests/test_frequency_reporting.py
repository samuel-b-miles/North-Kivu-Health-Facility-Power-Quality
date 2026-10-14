"""Four-threshold reporting retains validity, windows, and pooled weighting."""
import sys

import pandas as pd
import pytest

from drc_power.quality import conditional_power_quality, joint_valid_power_quality
from pipeline_common import apply_primary_telemetry_window
import run_power_quality
import run_figure3_summary


@pytest.mark.parametrize('calculate', [conditional_power_quality, joint_valid_power_quality])
def test_four_thresholds_share_valid_readings_including_physical_bounds(calculate):
    frame = pd.DataFrame({'voltage': [23, 400, 230, 230, 230, 230, 22, 401, 230, 230],
                          'frequency': [30, 70, 50, 50.4, 52, 54, 50, 50, 29, 71]})
    result = calculate(frame)
    assert result['valid_frequency_observations'] == 6
    for label, count in [('0_1', 1), ('1', 2), ('5', 3), ('10', 4)]:
        assert result[f'frequency_quality_{label}_pct'] == pytest.approx(count / 6 * 100)


def test_empty_frequency_denominator_remains_unknown():
    result = conditional_power_quality(pd.DataFrame({'voltage': [0], 'frequency': [50]}))
    assert all(pd.isna(result[f'frequency_quality_{label}_pct']) for label in ['0_1', '1', '5', '10'])


def test_csr4_frequency_window_retains_late_records_and_inclusive_exclusion():
    frame = pd.DataFrame({'time': ['2024-08-12', '2024-12-05', '2024-12-06',
                                  '2025-10-02 23:59', '2025-10-03', '2026-01-12']})
    result = apply_primary_telemetry_window(frame, 'CSR4')
    assert result.index.tolist() == [0, 1, 4, 5]


@pytest.mark.parametrize('policy', ['joint', 'independent'])
def test_pooled_four_threshold_export_uses_counts_and_numeric_tolerance(tmp_path, monkeypatch, policy):
    pairs = [{'facility_code': 'CSR3', 'powerwatch_sensor': sensor, 'shared_source': sensor}
             for sensor in ['A', 'B']]
    monkeypatch.setattr(run_power_quality, 'read_config', lambda name: [] if name == 'canonical_powerwatch.csv' else pairs)
    monkeypatch.setattr(run_power_quality, 'find_powerwatch', lambda root, sensor, preference: sensor)
    frames = {'A': pd.DataFrame({'time': pd.to_datetime(['2024-06-01'], utc=True), 'voltage': [230], 'frequency': [50]}),
              'B': pd.DataFrame({'time': pd.to_datetime(['2024-06-01'] * 3, utc=True), 'voltage': [230] * 3, 'frequency': [54] * 3})}
    monkeypatch.setattr(run_power_quality, 'read_powerwatch', lambda sensor: frames[sensor])
    monkeypatch.setattr(sys, 'argv', ['run_power_quality', '--output-root', str(tmp_path)])
    run_power_quality.main()
    quality = pd.read_csv(tmp_path / 'power_quality/post_flex_conditional_quality_by_facility.csv')
    for label, expected in [('0_1', 25), ('1', 25), ('5', 25), ('10', 100)]:
        assert quality.iloc[0][f'frequency_quality_{label}_pct_pooled'] == expected
        assert quality.iloc[0][f'frequency_quality_{label}_pct_joint_pooled'] == expected
    assert quality.iloc[0].frequency_quality_0_1_pct_mean_sensor == 50
    pre = pd.DataFrame([{'facility_code': 'CSR3', 'uptime_pct': 90, 'voltage_quality_pct': 90,
                         'frequency_quality_0_1_pct': 1, 'frequency_quality_1_pct': 2,
                         'frequency_quality_5_pct': 3, 'frequency_quality_10_pct': 4, 'status': 'reconstructed'}])
    reliability = pd.DataFrame([{'facility_code': 'CSR3', 'shared_source': 'A',
        'manuscript_uptime_expected_window_pct': 90, 'observed_uptime_pct': 90, 'coverage_pct': 100,
        'two_sensor_coverage_pct': 100, 'window_start': '2024-06-01', 'window_end_inclusive': '2024-06-01'}])
    (tmp_path / 'reliability').mkdir(); reliability.to_csv(tmp_path / 'reliability/manuscript_uptime_sensitivity.csv', index=False)
    (tmp_path / 'baseline_audit').mkdir()
    for name in ['single_sensor_comparisons', 'selected_longitudinal_baselines']:
        pre.to_csv(tmp_path / f'baseline_audit/{name}.csv', index=False)
    primary = [{'facility_code': 'CSR3', 'shared_source': 'A', 'primary_facility_result': 'true'}]
    monkeypatch.setattr(run_figure3_summary, 'read_config', lambda name: primary if name == 'paired_sensors.csv' else pre.to_dict('records'))
    monkeypatch.setattr(run_figure3_summary, 'reconstructed_comparisons', lambda *args: pre)
    monkeypatch.setattr(sys, 'argv', ['run_figure3_summary', '--output-root', str(tmp_path), '--pqr-policy', policy])
    run_figure3_summary.main()
    result = pd.read_csv(tmp_path / f'figure3/frequency_thresholds_{policy}.csv')
    assert result.frequency_tolerance_pct.tolist() == [0.1, 1, 5, 10]
    assert result.existing_source_frequency_pct.tolist() == [1, 2, 3, 4]
    assert result.protected_circuit_frequency_pct.tolist() == [25, 25, 25, 100]
