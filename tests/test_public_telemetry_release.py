import pytest
from build_public_telemetry_release import selected_schema, validate_value


def test_release_excludes_uncoded_names_and_summary_files():
    assert selected_schema('HOP_daily_energy', 'ch_CH1_613_energy_per_day.csv') is None
    assert selected_schema('HOP_voltage_power_1min', 'ActualFacility_CH1-HOP-01_Voltage_1.1.csv') is None
    assert selected_schema('PowerWatch_voltage_frequency_2min', 'PRE_power_quality_by_sensor.csv') is None


def test_release_allowlist_removes_identifying_powerwatch_columns():
    sensor, columns = selected_schema('PowerWatch_voltage_frequency_2min', 'CH1-PW-01_CH1_2min_og.csv')
    assert sensor == 'CH1-PW-01'
    assert columns == ['time', 'voltage', 'frequency']


def test_source_values_with_units_and_missingness_are_preserved():
    for column, value in [('total', '230 V'), ('Energy per Day', '1.25 kWh'), ('voltage', ''), ('frequency', 'NaN'), ('time', '2024-01-01 05:33:00')]:
        validate_value(column, value)
    with pytest.raises(ValueError):
        validate_value('total', 'identifying free text')
