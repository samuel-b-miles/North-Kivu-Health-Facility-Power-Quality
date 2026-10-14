#!/usr/bin/env python3
"""Reconstruct longitudinal baseline inputs and explicit window sensitivities.

Paired results are sensitivity estimates pending source/topology verification.
Quality uses equal sensor weighting within the SAME shared window, matching the
inherited site-summary aggregation rather than pooling differently sized files.
"""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

import pandas as pd

from drc_power.io import read_powerwatch
from drc_power.monitoring_audit import monitoring_summary
from drc_power.quality import conditional_power_quality
from pipeline_common import DEFAULT_OUTPUT_ROOT, DEFAULT_RAW_ROOT, find_powerwatch, read_config
from run_baseline_audit import legacy_quality, legacy_uptime


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--raw-root', type=Path, default=DEFAULT_RAW_ROOT)
    parser.add_argument('--output-root', type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument('--supplement-root', type=Path,
                        help='Optional directory containing the deidentified DRC1 baseline supplement')
    args = parser.parse_args()
    output = args.output_root / 'baseline_audit'
    output.mkdir(parents=True, exist_ok=True)
    rows, inventory, groups = [], [], {}
    specs = read_config('longitudinal_pre_windows.csv')
    for spec in specs:
        sensor = spec['sensor_id']
        source_root = args.supplement_root if sensor == 'CSR1-PW-01' and args.supplement_root else args.raw_root
        path = find_powerwatch(source_root, sensor, spec['preferred_version'])
        data = read_powerwatch(path)
        end = pd.Timestamp(spec['end_exclusive'], tz='UTC')
        selected = data[data.time < end]
        groups.setdefault(spec['facility_code'], {})[sensor] = selected
        inventory.append({**spec, 'source_basis': 'DRC1_supplement' if sensor == 'CSR1-PW-01' else 'pilot_release',
                          'file': str(path.relative_to(source_root)),
                          'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                          'rows': len(data), 'selected_rows': len(selected),
                          'first_reading': data.time.min(), 'last_reading': data.time.max()})
        for basis, frame in [('full_existing_source_record_not_pure_pre', data),
                             (spec['window_basis'], selected)]:
            rows.append({'facility_code': spec['facility_code'], 'sensor_basis': sensor,
                         'window_basis': basis, 'quality_aggregation': 'single_sensor',
                         **monitoring_summary({sensor: frame}),
                         **legacy_quality(frame), **conditional_power_quality(frame), **legacy_uptime(frame, 2)})
        print(f'Audited {sensor}: {len(selected):,} pre-window rows', flush=True)
    for facility, frames in groups.items():
        if len(frames) != 2:
            continue
        first = min(d.dropna(subset=['voltage']).time.min() for d in frames.values())
        last = max(d.dropna(subset=['voltage']).time.max() for d in frames.values())
        union = monitoring_summary(frames, start=first,
                                   end=last.floor('2min') + pd.Timedelta(minutes=2))
        def mean_quality(selected):
            joint = pd.DataFrame([legacy_quality(d) for d in selected.values()]).mean().to_dict()
            joint.pop('legacy_joint_valid_n', None)
            independent = pd.DataFrame([conditional_power_quality(d) for d in selected.values()]).mean().to_dict()
            return {**joint, **{k: v for k, v in independent.items() if k.endswith('_pct')}}
        rows.append({'facility_code': facility, 'sensor_basis': 'two_sensor_union_window',
                     'window_basis': 'all_available_pre_with_variable_sensor_coverage',
                     'quality_aggregation': 'equal_sensor_mean_of_available_pre_readings',
                     **union, **mean_quality(frames)})
        paired = monitoring_summary(frames)
        start = pd.Timestamp(paired['window_start'])
        end = pd.Timestamp(paired['window_end_inclusive']) + pd.Timedelta(minutes=2)
        same_window = {sensor: data[(data.time >= start) & (data.time < end)]
                       for sensor, data in frames.items()}
        quality = mean_quality(same_window)
        rows.append({'facility_code': facility, 'sensor_basis': 'two_sensor_sensitivity',
                     'window_basis': 'shared_overlap_before_intervention_source_start',
                     'quality_aggregation': 'equal_sensor_mean_in_shared_window',
                     **paired, **quality})
        for sensor, data in same_window.items():
            rows.append({'facility_code': facility, 'sensor_basis': sensor,
                         'window_basis': 'same_window_as_two_sensor_sensitivity',
                         'quality_aggregation': 'single_sensor',
                         **monitoring_summary({sensor: data}, start=start, end=end),
                         **legacy_quality(data), **conditional_power_quality(data), **legacy_uptime(data, 2)})
    comparisons = pd.DataFrame(rows)
    comparisons.to_csv(output / 'longitudinal_pre_comparisons.csv', index=False)
    selected_rows = []
    for selection in read_config('figure3_baseline_selections.csv'):
        chosen = comparisons[(comparisons.facility_code == selection['facility_code']) &
                             (comparisons.sensor_basis == selection['sensor_basis'])]
        if len(chosen) != 1:
            raise ValueError('Missing unique longitudinal baseline: ' + selection['facility_code'])
        row = chosen.iloc[0].to_dict()
        row['selection_rationale'] = selection['selection_rationale']
        row['sensor_ids'] = ';'.join(sorted(groups[selection['facility_code']]))
        selected_rows.append(row)
    pd.DataFrame(selected_rows).to_csv(output / 'selected_longitudinal_baselines.csv', index=False)
    pd.DataFrame(inventory).to_csv(output / 'longitudinal_pre_inventory.csv', index=False)
    print(f'Audit outputs: {output}')


if __name__ == '__main__':
    main()
