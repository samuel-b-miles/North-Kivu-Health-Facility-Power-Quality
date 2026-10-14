# Complete data package reproduction

The local release candidate is assembled with:

```bash
python scripts/build_public_data_package.py --telemetry-candidate outputs/release_candidate/telemetry-v2-six-baselines --output-dir outputs/release_candidate/complete-v2-six-baselines
cd outputs/release_candidate/complete-v2-six-baselines
pip install -e '.[dev]'
python scripts/run_public_package.py
pytest
```

Use Python 3.11 or newer. The public runner verifies the manifest, imports the full-resolution coded electricity archives, and runs all implemented workflows using public DHIS2 panels. It also runs the independent-denominator Figure 3 sensitivity. It never requires identified DHIS2 exports or a private crosswalk. The normal `run_all.py` path still supports restricted-source health cleaning.

From the original repository, freeze the generated reference tables and figures:

```bash
python scripts/finalize_public_data_package.py --package-root outputs/release_candidate/complete-v2-six-baselines
```

The resulting ZIP excludes working raw extraction directories, caches and private approval correspondence. Its manifest includes each packaged file's hash and, for CSVs, row counts and fields; a sidecar records the ZIP hash. The health and payment panels, telemetry archives, code/config, dictionaries, public publication figures and generated CSV/SVG reference outputs are included. Payment IDs/free-text notes are stripped without changing calculations.

## Earlier v1 verification completed on 10 October 2026

An empty candidate snapshot ran all ten workflows and eight annex tables using only included inputs. Twenty-eight tests passed. Seventeen Figure 3, health, payment and energy output tables exactly matched original-input/publication references. The final ZIP's 158 manifested file hashes passed readback verification. Bundled pandas/numpy/pytest libraries were used; installation into a new downloaded environment has not been tested. The candidate's VALIDATION.md records runtime versions.

## Remaining limits

This is a reproducible candidate for the implemented analyses, not certification of every manuscript claim. All six Figure 3 comparisons are reconstructed; different source windows and variable coverage remain explicit. Energy topology and active windows remain provisional. DHIS2 source-cleaning audits are restricted and not rebuilt from panels. Some timeline dates/labels still require manuscript reconciliation. Code/data licences remain proposed pending rights-holder confirmation; the archives have not been publicly deposited. See DATA_SHARING_HANDOFF.md and TELEMETRY_PUBLIC_RELEASE.md.

## Six-baseline revision

The v2 candidate contains four telemetry archives including the DRC1 supplement. Eleven workflows regenerate the six-facility Figure 3 and annex; complete ±1/5/10% tables, inherited-value audit and window sensitivities are included. See the candidate's `VALIDATION.md` for isolated-run results. Current tests: 29 passing.
