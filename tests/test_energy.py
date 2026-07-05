import math

import pandas as pd

from drc_power.energy import aggregate_daily_energy, parse_energy_wh


def test_parse_energy_units():
    assert parse_energy_wh("1.5 kWh") == 1500
    assert parse_energy_wh("250 Wh") == 250
    assert math.isnan(parse_energy_wh("missing"))


def test_missing_day_is_not_silently_zero():
    first = pd.DataFrame({"Time": ["2025-01-01"], "Energy per Day": ["1 kWh"]})
    second = pd.DataFrame({"Time": ["2025-01-02"], "Energy per Day": ["2 kWh"]})
    result = aggregate_daily_energy({"A": first, "B": second})
    assert result.loc[pd.Timestamp("2025-01-01").date(), "facility_total_kwh"] == 1
    assert result.loc[pd.Timestamp("2025-01-02").date(), "facility_total_kwh"] == 2
    assert result["reporting_sensors"].tolist() == [1, 1]

