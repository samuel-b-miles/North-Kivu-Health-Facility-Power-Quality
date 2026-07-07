import pandas as pd

from drc_power.annex import build_power_quality_table


def test_power_quality_table_uses_primary_facility_window():
    summary = pd.DataFrame({
        "facility_code": ["CH1"], "uptime_pre_pct": [69.2], "uptime_post_pct": [99.09],
        "voltage_pre_pct": [2.93], "voltage_post_pct": [99.97],
        "frequency_5_pre_pct": [0.09], "frequency_5_post_pct": [100.0],
        "pre_status": ["manuscript_reported_pending_reproduction"],
    })
    reliability = pd.DataFrame({
        "facility_code": ["CH1", "CH1"], "primary_facility_result": [True, False],
        "shared_window_start": ["2024-05-25", "2024-06-01"],
        "shared_window_end": ["2025-11-03", "2025-10-01"],
    })
    result = build_power_quality_table(summary, reliability).iloc[0]
    assert result["uptime_post_pct"] == 99.1
    assert result["shared_window_start"] == "2024-05-25"
    assert result["post_status"] == "repository_reproduced_provisional"
