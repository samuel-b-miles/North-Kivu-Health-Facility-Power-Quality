import pandas as pd

from drc_power.quality import conditional_power_quality


def test_quality_is_conditional_on_powered_observations():
    frame = pd.DataFrame(
        {
            "voltage": [0, 220, 260, 500, None],
            "frequency": [50, 50, 50, 50, 50],
        }
    )
    result = conditional_power_quality(frame)
    assert result["powered_voltage_observations"] == 2
    assert result["outage_voltage_observations"] == 1
    assert result["invalid_voltage_observations"] == 1
    assert result["voltage_quality_pct"] == 50.0


def test_invalid_frequency_does_not_remove_voltage_observation():
    frame = pd.DataFrame({"voltage": [230, 230], "frequency": [50, 9000]})
    result = conditional_power_quality(frame)
    assert result["voltage_quality_pct"] == 100.0
    assert result["valid_frequency_observations"] == 1
    assert result["invalid_frequency_observations"] == 1

