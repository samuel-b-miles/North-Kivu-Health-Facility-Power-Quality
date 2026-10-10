"""Regression checks for missingness, pairing, and excluded denominators."""

import unittest

import pandas as pd

from drc_power.monitoring_audit import monitoring_summary


def frame(values):
    return pd.DataFrame({"time": pd.date_range("2024-01-01", periods=len(values), freq="2min", tz="UTC"),
                         "voltage": values})


class MonitoringAuditTests(unittest.TestCase):
    def test_pair_distinguishes_one_sensor_evidence_and_confirmed_low(self):
        result = monitoring_summary({"hop": frame([230, None, 0, None, 230]),
                                     "pw": frame([230, 230, 0, None, 0])})
        self.assertEqual(result["two_sensors_low_intervals"], 1)
        self.assertEqual(result["one_sensor_observed_intervals"], 1)
        self.assertEqual(result["unknown_intervals"], 1)
        self.assertEqual(result["discordant_intervals"], 1)
        self.assertEqual(result["observed_uptime_pct"], 75)
        self.assertEqual(result["expected_window_uptime_pct"], 60)

    def test_exclusion_is_removed_from_expected_denominator(self):
        dates = frame([230, None, None, 230]).time
        result = monitoring_summary({"hop": frame([230, None, None, 230]),
                                     "pw": frame([230, None, None, 230])},
                                    exclusions=[(dates.iloc[1], dates.iloc[3])])
        self.assertEqual(result["expected_intervals"], 2)
        self.assertEqual(result["expected_window_uptime_pct"], 100)

    def test_empty_calendar_window_is_unknown_not_zero_observed_uptime(self):
        start = pd.Timestamp("2024-01-01", tz="UTC")
        result = monitoring_summary({"sensor": frame([None, None])}, start=start,
                                    end=start + pd.Timedelta(minutes=4))
        self.assertEqual(result["unknown_intervals"], 2)
        self.assertTrue(pd.isna(result["observed_uptime_pct"]))
        self.assertEqual(result["coverage_pct"], 0)

    def test_duplicate_rows_cannot_inflate_uptime(self):
        data = frame([230, 0])
        result = monitoring_summary({"sensor": pd.concat([data, data.iloc[[0]]])})
        self.assertEqual(result["expected_intervals"], 2)
        self.assertEqual(result["observed_uptime_pct"], 50)

    def test_post_pair_uses_shared_window(self):
        result = monitoring_summary({"hop": frame([230, 230, 230]),
                                     "pw": frame([None, 0, 230])})
        self.assertEqual(result["expected_intervals"], 2)
        self.assertEqual(result["discordant_intervals"], 1)


if __name__ == "__main__":
    unittest.main()
