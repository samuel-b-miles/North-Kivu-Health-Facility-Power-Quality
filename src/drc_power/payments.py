"""Payment-ledger validation and manuscript summary estimands."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

FACILITY_CODES = ("CH1", "CSR1", "CSR2", "CSR3", "CSR4", "HGR1")
ALLOWED_CODES = set(FACILITY_CODES) | {"ADMIN"}
CAPEX_CATEGORIES = {"Installation & deployment", "Additional Requested Upgrade"}


def read_payment_ledger(path: Path) -> pd.DataFrame:
    data = pd.read_csv(path)
    data["date"] = pd.to_datetime(data["date"], errors="raise")
    unknown = set(data["facility"].dropna()) - ALLOWED_CODES
    if unknown:
        raise ValueError(f"Unexpected public facility codes: {sorted(unknown)}")
    if set(data["transaction_direction"].dropna()) - {"inflow", "outflow"}:
        raise ValueError("transaction_direction must be inflow or outflow")
    return data


def facility_payment_summary(data: pd.DataFrame) -> pd.DataFrame:
    payments = data[data["transaction_direction"] == "inflow"].copy()
    payments["on_time"] = pd.to_numeric(payments["days_late"], errors="coerce").fillna(0).le(0)
    rows = []
    for code in FACILITY_CODES:
        group = payments[payments["facility"] == code]
        rows.append({
            "facility_code": code,
            "remittances_n": len(group),
            "received_usd": group["amount_received_usd"].sum(),
            "on_time_n": int(group["on_time"].sum()),
            "delayed_n": int((~group["on_time"]).sum()),
            "on_time_pct": group["on_time"].mean() * 100,
            "maximum_delay_days": group["days_late"].max(),
        })
    return pd.DataFrame(rows)


def overall_payment_summary(data: pd.DataFrame) -> pd.DataFrame:
    payments = data[data["transaction_direction"] == "inflow"].copy()
    delays = pd.to_numeric(payments["days_late"], errors="coerce").fillna(0)
    delayed = delays[delays > 0]
    outflows = data[data["transaction_direction"] == "outflow"]
    installation = outflows["transaction_category"].eq("Installation & deployment")
    expansion = outflows["transaction_category"].eq("Additional Requested Upgrade")
    values = {
        "payment_revenue_usd": payments["amount_received_usd"].sum(),
        "remittances_n": len(payments),
        "on_time_n": int(delays.le(0).sum()),
        "on_time_pct": delays.le(0).mean() * 100,
        "within_30_days_pct": delays.le(30).mean() * 100,
        "within_60_days_pct": delays.le(60).mean() * 100,
        "median_delay_among_delayed_days": delayed.median(),
        "mean_delay_among_delayed_days": delayed.mean(),
        "installation_deployment_usd": outflows.loc[installation, "amount_paid_usd"].sum(),
        "additional_system_capex_usd": outflows.loc[expansion, "amount_paid_usd"].sum(),
        "recurring_om_and_other_usd": outflows.loc[~installation & ~expansion, "amount_paid_usd"].sum(),
        "total_outflows_usd": outflows["amount_paid_usd"].sum(),
    }
    values["ledger_cash_balance_usd"] = values["payment_revenue_usd"] - values["total_outflows_usd"]
    return pd.DataFrame([values])


def monthly_cash_flow(data: pd.DataFrame) -> pd.DataFrame:
    working = data.copy()
    working["month"] = working["date"].dt.to_period("M").dt.to_timestamp()
    inflows = working[working["transaction_direction"] == "inflow"].pivot_table(
        index="month", columns="facility", values="amount_received_usd", aggfunc="sum", fill_value=0
    )
    for code in FACILITY_CODES:
        if code not in inflows:
            inflows[code] = 0.0
    outflow_rows = working[working["transaction_direction"] == "outflow"].copy()
    outflow_rows["cost_class"] = outflow_rows["transaction_category"].map(
        lambda value: "CAPEX" if value in CAPEX_CATEGORIES else "OPEX"
    )
    outflows = outflow_rows.groupby("month")["amount_paid_usd"].sum()
    capex = outflow_rows[outflow_rows["cost_class"] == "CAPEX"].groupby("month")["amount_paid_usd"].sum()
    opex = outflow_rows[outflow_rows["cost_class"] == "OPEX"].groupby("month")["amount_paid_usd"].sum()
    start, end = working["month"].min(), working["month"].max()
    result = inflows.reindex(pd.date_range(start, end, freq="MS"), fill_value=0)[list(FACILITY_CODES)]
    result.index.name = "month"
    result["facility_payments_usd"] = result.sum(axis=1)
    result["capex_outflows_usd"] = capex.reindex(result.index, fill_value=0)
    result["opex_outflows_usd"] = opex.reindex(result.index, fill_value=0)
    result["recorded_outflows_usd"] = outflows.reindex(result.index, fill_value=0)
    result["net_cash_flow_usd"] = result["facility_payments_usd"] - result["recorded_outflows_usd"]
    result["cumulative_ledger_balance_usd"] = result["net_cash_flow_usd"].cumsum()
    return result


def outflows_by_facility_category(data: pd.DataFrame) -> pd.DataFrame:
    outflows = data[data["transaction_direction"] == "outflow"]
    return outflows.pivot_table(
        index="facility", columns="transaction_category", values="amount_paid_usd", aggfunc="sum", fill_value=0
    ).sort_index()
