#!/usr/bin/env python3
"""Build a local, deidentified full-resolution telemetry release candidate.

Uses a strict filename/schema/value allowlist; preserves measurement strings,
row order, timestamps and blanks. Publication is a separate action.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import io
import json
import re
import tomllib
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo
from bootstrap_data import digest

ROOT = Path(__file__).resolve().parents[1]
SENSOR = re.compile(r"(?:HGR1|CH1|CSR[1-4])-(?:PW|HOP)-\d{2}")
TIME = re.compile(r"\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?")
NUMBER = re.compile(r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?")
SCHEMAS = {
    "PowerWatch_voltage_frequency_2min": ["time", "voltage", "frequency"],
    "DRC1_baseline_supplement": ["time", "voltage", "frequency"],
    "HOP_voltage_power_1min": ["time", "total", "phase_1", "phase_2", "phase_3"],
    "HOP_daily_energy": ["Time", "Energy per Day"],
}


def selected_schema(domain: str, filename: str):
    match = SENSOR.search(filename)
    if not match:
        return None
    if domain in ("PowerWatch_voltage_frequency_2min", "DRC1_baseline_supplement"):
        if not re.fullmatch(r"(?:HGR1|CH1|CSR[1-4])-PW-\d{2}_(?:HGR1|CH1|CSR[1-4])?_(?:2min_og|2min_omitted|voltage_frequency_updated)\.csv", filename):
            return None
    elif domain == "HOP_voltage_power_1min":
        if not re.fullmatch(r"(?:HGR1|CH1|CSR[1-4])_(?:HGR1|CH1|CSR[1-4])-HOP-\d{2}_Voltage_1\.1\.csv", filename):
            return None
    elif domain == "HOP_daily_energy":
        if not re.fullmatch(r"(?:ch|csr|hgr)_(?:HGR1|CH1|CSR[1-4])_(?:HGR1|CH1|CSR[1-4])-HOP-\d{2}_energy_per_day\.csv(?:\.csv)?", filename):
            return None
    else:
        return None
    return match.group(), SCHEMAS[domain]


def validate_value(column: str, value: str):
    if value == "":
        return
    if column.lower() == "time":
        if not TIME.fullmatch(value):
            raise ValueError("Unexpected timestamp format")
    elif column == "Energy per Day":
        if not re.fullmatch(NUMBER.pattern + r"\s*(?:Wh|kWh|MWh)?", value):
            raise ValueError("Unexpected energy value")
    elif value.lower() not in {"nan", "inf", "-inf", "+inf"} and not re.fullmatch(NUMBER.pattern + r"\s*(?:V|W|kW)?", value):
        raise ValueError("Unexpected non-numeric measurement")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-dir", type=Path, default=ROOT / "data/raw/downloads")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "outputs/release_candidate/telemetry-v1")
    args = parser.parse_args()
    assets = tomllib.loads((ROOT / "config/data_sources.toml").read_text())["release"]["assets"]
    for asset in assets:
        if digest(args.source_dir / asset["filename"]) != asset["sha256"]:
            raise ValueError("Source archive checksum mismatch: " + asset["filename"])
    args.output_dir.mkdir(parents=True, exist_ok=False)
    inventory, exclusions, released_assets = [], [], []
    for asset in assets:
        domain = Path(asset["filename"]).stem
        destination = args.output_dir / asset["filename"]
        with ZipFile(args.source_dir / asset["filename"]) as source, ZipFile(destination, "w", compression=ZIP_DEFLATED, compresslevel=6) as output:
            seen = set()
            for member in source.infolist():
                filename = member.filename.replace("\\", "/").rsplit("/", 1)[-1]
                if member.is_dir() or not filename.endswith(".csv") or filename.startswith("._"):
                    continue
                selection = selected_schema(domain, filename)
                if selection is None:
                    exclusions.append({"domain": domain, "reason": "not_allowlisted_measurement_file", "source_member_sha256": hashlib.sha256(member.filename.encode()).hexdigest()})
                    continue
                sensor, columns = selection
                # Preserve discovery-compatible coded filenames; never copy ZIP metadata.
                if filename in seen:
                    raise ValueError("Duplicate output filename")
                seen.add(filename)
                info = ZipInfo(filename, date_time=(2026, 10, 10, 0, 0, 0)); info.compress_type = ZIP_DEFLATED
                rows = 0; selected_hash = hashlib.sha256(); first = last = None
                with source.open(member) as raw, output.open(info, "w") as target:
                    reader = csv.DictReader(io.TextIOWrapper(raw, encoding="utf-8-sig", newline=""))
                    if not set(columns).issubset(reader.fieldnames or []):
                        raise ValueError("Required columns missing")
                    handle = io.TextIOWrapper(target, encoding="utf-8", newline="")
                    writer = csv.writer(handle, lineterminator="\n"); writer.writerow(columns)
                    for row in reader:
                        values = [row[c] for c in columns]
                        for col, value in zip(columns, values):
                            validate_value(col, value)
                        writer.writerow(values)
                        selected_hash.update(json.dumps(values, separators=(",", ":")).encode() + b"\n")
                        first = values[0] if first is None else first; last = values[0]; rows += 1
                    handle.flush(); handle.detach()
                inventory.append({"archive": destination.name, "file": filename, "sensor_code": sensor, "rows": rows, "first_row_time": first, "last_row_time": last, "selected_values_sha256": selected_hash.hexdigest(), "columns": columns, "baseline_only": "omitted" in filename or domain == "DRC1_baseline_supplement"})
        # Independently read output and verify every retained cell and row against source projection.
        with ZipFile(destination) as check:
            for item in [r for r in inventory if r["archive"] == destination.name]:
                h = hashlib.sha256(); count = 0
                with check.open(item["file"]) as f:
                    reader = csv.reader(io.TextIOWrapper(f, encoding="utf-8", newline=""))
                    if next(reader) != item["columns"]:
                        raise ValueError("Output schema mismatch")
                    for row in reader:
                        h.update(json.dumps(row, separators=(",", ":")).encode() + b"\n"); count += 1
                if count != item["rows"] or h.hexdigest() != item["selected_values_sha256"]:
                    raise ValueError("Output measurements differ from source projection")
        released_assets.append({"filename": destination.name, "sha256": digest(destination), "bytes": destination.stat().st_size})
        print(f"Verified {domain}: {len(seen)} files", flush=True)
    manifest = {"status": "local_candidate_pending_partner_disclosure_review", "licence_proposed": "CC-BY-4.0", "source_archives": assets, "release_archives": released_assets, "files": inventory, "excluded_members": exclusions, "transformation": "Column projection only; complete retained files, unchanged timestamps, measurement strings, row order, duplicates and blanks. No resampling, filtering or imputation."}
    (args.output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    config = '[release]\nname = "public-telemetry-v1-candidate"\n'
    for asset in released_assets:
        config += f'\n[[release.assets]]\nfilename = "{asset["filename"]}"\nsha256 = "{asset["sha256"]}"\n'
    (args.output_dir / "data_sources.toml").write_text(config)
    (args.output_dir / "README.md").write_text('''# Full-resolution coded telemetry release candidate

Proposed licence: CC BY 4.0, subject to confirmation by rights holders.
This candidate is not yet approved for public redistribution.

Four ZIPs retain all allowlisted measurement files, including original and updated
PowerWatch exports and explicitly omitted series. Original and updated files overlap;
use repository canonical selection, never concatenate them blindly. Omitted series
are retained for transparency, not automatically included in estimates.

Respondent/site fields, free text, derived time differences, summary files, ZIP
comments and source directory paths are removed. Coded sensor filenames remain.
All timestamps and measurement strings are unchanged. Empty cells remain empty;
missing measurements are not zero. HOP total/phase columns retain source labels;
consult pipeline loaders for the voltage field used. Energy values retain units.
Naive HOP timestamps retain their source form and the existing pipeline's UTC
interpretation; this is not independent confirmation of device clock timezone.

This is deidentified/coded data, not a guarantee of anonymity: calendar dates,
facility type and distinctive patterns may reveal identity. Facility codes correspond
to public study configuration. Obtain partner/authority review of calendar dates,
source permissions and disclosure risk before public deposit.

The manifest lists every retained file, row count and hashes. A noncoded legacy
energy export and summary/notes files are not released. The DRC1 supplement adds
the verified second CSR1 baseline sensor. All six Figure 3 comparisons are
reconstructed using explicit windows and coverage diagnostics.

To reproduce electricity analyses, use the repository bootstrap script with the
included data_sources.toml, then the existing energy/reliability/quality/Figure 3
scripts. The package contains electricity inputs only; health/payment public inputs
remain in the code repository. Raw identified DHIS2 and crosswalks remain restricted.
''')
    print(f"Complete: {len(inventory)} files; {sum(r['rows'] for r in inventory):,} rows; {sum(a['bytes'] for a in released_assets):,} compressed bytes")

if __name__ == "__main__":
    main()
