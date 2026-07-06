# Payment and Cost Analysis

## Public data

`data/public/payments/payment_ledger_anonymized.csv` is the tracked,
manuscript-ready ledger. It uses the same stable public facility codes as the
energy analyses: `HGR1`, `CH1`, and `CSR1`–`CSR4`. The private identity key and
original transaction descriptions are not included.

The later facility-requested system is classified as an outflow under
`Additional Requested Upgrade`. It is capital expenditure, not payment revenue
or recurring maintenance.

## Reproduced estimands

`python scripts/run_payments.py` writes:

- facility and overall payment-timing summaries;
- monthly payments, outflows, and cumulative ledger balance;
- outflows by public facility code and category; and
- a three-panel provisional Figure 6 separating monthly cash flow, CAPEX, and
  OPEX.

For Figure 6, `Installation & deployment` and `Additional Requested Upgrade`
are treated as CAPEX. All other outflow categories are treated as OPEX. The
facility-requested additional system therefore appears only in the CAPEX panel,
not in maintenance or operating expenditure.

On time means `days_late <= 0`. The share paid within 30 or 60 days includes
on-time remittances. Payment completion against expected facility-months is not
estimated until a versioned billing schedule documents each contractual amount,
effective date, approved pause, and conflict-related exclusion.

## CAPEX reference

The internal budget model estimated an installed cost of $11,949 per
standardized deployment package, comprising $7,450 in equipment and $4,499 in
freight, importation, taxes, delivery, and installation. Under a 5%
declining-balance financing assumption over ten years, the corresponding capital
requirement was $15,224 per package.

These are standardized reference values, not observed site-specific invoices.
Portfolio multiplication requires a reconciled count of complete deployment
packages because additional FLEX units did not necessarily duplicate the water
and biomedical-equipment bundle.
