# Telemetry Coverage Audit: CSR4 and CSR1 Exclusions

Facility codes are used here to preserve the public/private separation.

## CSR4: 2024-12-06 through 2025-10-02

Primary analyses exclude this interval from FLEX sensor-based uptime and power
quality. Operational use and payment status are separate evidence streams and
will be audited when payment data are incorporated.

### HOP evidence

- `CSR4-HOP-01` voltage remains available from 2024-12-06 through
  2025-02-28, covering 46 calendar days and 49,904 valid readings.
- Every retained HOP voltage reading in this interval is above 23 V.
- The daily-energy export reports only 0.48 kWh on 2024-12-06 and 0.01 kWh on
  2025-03-01; otherwise it is zero despite extensive voltage telemetry.
- There is no HOP voltage after 2025-02-28 and no positive HOP daily energy
  after 2025-03-01.

### PowerWatch evidence

`CSR4-PW-01` has only four isolated reporting dates during the exclusion:

- 2024-12-06: 711 readings, 360 above 23 V.
- 2024-12-07: 72 readings, none above 23 V.
- 2025-03-01: one low-voltage reading.
- 2025-10-02: 321 readings, all above 23 V.

Continuous PowerWatch reporting resumes on 2025-10-03. `CSR4-PW-02` continues
intermittently only through 2025-01-28 and does not resolve the FLEX source
identity during the exclusion.

### Interpretation

Telemetry presence does not establish continuous clinical use. HOP voltage
suggests the system or monitored circuit was energized through February, while
daily-energy data suggest almost no measured load. Payment and operational logs
should be analyzed separately as evidence of service availability or use.

## CSR1: open-ended from 2024-12-21

- Core `CSR1-HOP-01` voltage ends 2024-12-20 at 20:15 UTC.
- Morgue `CSR1-HOP-02` voltage ends 2024-12-18 at 20:45 UTC.
- Both daily-energy series contain no positive values from 2024-12-21 onward.
- `CSR1-PW-03` has 172 readings during the first 5 hours 42 minutes of
  2024-12-21, then stops permanently in the released data.

### Interpretation

There is no HOP data stream that can recover post-2024-12-21 uptime at CSR1.
The primary telemetry analysis must end at connectivity loss; absence of later
telemetry must not be presented as evidence that the electrical system failed.

