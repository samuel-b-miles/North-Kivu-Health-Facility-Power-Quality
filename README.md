# North Kivu Health-Facility Power Analysis

Reproducible analysis of electricity reliability, conditional power quality,
and energy use across six anonymized health facilities in North Kivu, DRC.

This is a clean-room workflow scaffold derived from the documented analytical
requirements and approved anonymized release assets. Raw sensor data and the
private facility identity key are intentionally excluded from version control.

## Analytical principles

1. **Reliability and power quality are separate outcomes.** Availability asks
   whether usable power is present. Conditional power quality asks whether
   voltage/frequency are compliant while power is present.
2. **Missing telemetry is not automatically an outage.** Missing intervals are
   reported as unknown unless a named conservative sensitivity analysis says otherwise.
3. **Post-intervention confirmed outages use paired sensors.** A confirmed
   outage requires simultaneous outage evidence from co-located HOP and
   PowerWatch sensors.
4. **Every inclusion and time window is configured, not buried in notebook cells.**
5. **Private identities never enter public artifacts.** Public codes remain the
   stable analysis identifiers.

## Repository structure

```text
config/                 Public sensor map and reviewable analysis periods
src/drc_power/          Reusable ingestion and analysis modules
tests/                  Unit tests for key estimands
docs/                   Decisions, open questions, and audit trail
data/raw/               Local-only release assets (Git-ignored)
data/private/           Local-only identity key (Git-ignored)
outputs/generated/      Reproducible generated tables and figures
```

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
pytest
```

## Current status

- Raw-asset inventory complete.
- Seven PowerWatch original/updated pairs audited; each updated file is an
  exact superset of its original.
- Analysis primitives implemented and tested.
- Facility periods and exclusions remain provisional pending study-team review.
- Full outcome regeneration is the next milestone.

