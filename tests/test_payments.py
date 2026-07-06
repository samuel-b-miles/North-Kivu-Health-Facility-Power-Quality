import pandas as pd

from drc_power.payments import facility_payment_summary, monthly_cash_flow, overall_payment_summary


def sample_ledger():
    return pd.DataFrame({
        "date": pd.to_datetime(["2025-01-01", "2025-01-10", "2025-01-15", "2025-01-20"]),
        "facility": ["CH1", "CH1", "CSR1", "CSR1"],
        "transaction_direction": ["inflow", "inflow", "outflow", "outflow"],
        "transaction_category": ["Facility repayments", "Facility repayments", "Installation & deployment", "Additional Requested Upgrade"],
        "amount_received_usd": [50, 50, 0, 0],
        "amount_paid_usd": [0, 0, 20, 30],
        "days_late": [0, 5, pd.NA, pd.NA],
    })


def test_payment_timing_summary():
    result = overall_payment_summary(sample_ledger()).iloc[0]
    assert result["payment_revenue_usd"] == 100
    assert result["on_time_pct"] == 50
    assert result["additional_system_capex_usd"] == 30
    assert result["opex_total_usd"] == 20
    assert result["ledger_cash_balance_usd"] == 50


def test_facility_codes_are_stable():
    result = facility_payment_summary(sample_ledger())
    ch1 = result[result["facility_code"] == "CH1"].iloc[0]
    assert ch1["remittances_n"] == 2
    assert ch1["delayed_n"] == 1


def test_capex_and_opex_cash_flow_are_separate():
    result = monthly_cash_flow(sample_ledger())
    assert result["capex_outflows_usd"].sum() == 30
    assert result["opex_outflows_usd"].sum() == 20
    assert result["recorded_outflows_usd"].sum() == 50
