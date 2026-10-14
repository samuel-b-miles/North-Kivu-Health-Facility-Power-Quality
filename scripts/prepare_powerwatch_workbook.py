#!/usr/bin/env python3
"""Project a verified private PowerWatch workbook into a coded release candidate.

Preserves complete row order and time/voltage/frequency values. Device identity,
site names and coordinates are excluded by a strict column allowlist. The caller
must verify the private device crosswalk before assigning the coded sensor ID.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from pathlib import Path

from build_public_telemetry_release import validate_value


def row_bytes(row):
    return (json.dumps(row, ensure_ascii=False, separators=(',', ':')) + '\n').encode()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--source-sha256', required=True)
    parser.add_argument('--sensor-id', required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    if not re.fullmatch(r'(?:HGR1|CH1|CSR[1-4])-PW-\d{2}', args.sensor_id):
        raise ValueError('Expected a pilot coded PowerWatch sensor ID')
    source_hash = hashlib.sha256(args.source.read_bytes()).hexdigest()
    if source_hash != args.source_sha256:
        raise ValueError('Private source checksum mismatch')
    import openpyxl
    workbook = openpyxl.load_workbook(args.source, read_only=True, data_only=False)
    if len(workbook.worksheets) != 1:
        raise ValueError('Expected one data sheet')
    rows = workbook.worksheets[0].iter_rows(values_only=True)
    header = next(rows)
    fields = ['time', 'voltage', 'frequency']
    if any(header.count(k) != 1 for k in fields):
        raise ValueError('Missing or duplicate measurement columns')
    indexes = [header.index(k) for k in fields]
    args.output_dir.mkdir(parents=True, exist_ok=False)
    facility = args.sensor_id.split('-')[0]
    dest = args.output_dir / f'{args.sensor_id}_{facility}_2min_og.csv'
    expected = hashlib.sha256()
    count = 0
    with dest.open('w', encoding='utf-8', newline='') as handle:
        writer = csv.writer(handle)
        writer.writerow(fields)
        for row in rows:
            selected = ['' if row[i] is None else str(row[i]) for i in indexes]
            for field, value in zip(fields, selected):
                validate_value(field, value)
            writer.writerow(selected)
            expected.update(row_bytes(selected))
            count += 1
            if count % 200000 == 0:
                print(f'Projected {count:,} rows', flush=True)
    workbook.close()
    actual = hashlib.sha256()
    read_count = 0
    with dest.open(encoding='utf-8', newline='') as handle:
        reader = csv.reader(handle)
        if next(reader) != fields:
            raise ValueError('Readback schema mismatch')
        for row in reader:
            actual.update(row_bytes(row))
            read_count += 1
    if count != read_count or expected.digest() != actual.digest():
        raise ValueError('Full projection readback mismatch')
    manifest = {'sensor_id': args.sensor_id, 'source_sha256': source_hash,
                'file': dest.name, 'rows': count, 'retained_columns': fields,
                'sha256': hashlib.sha256(dest.read_bytes()).hexdigest(),
                'projection_readback_verified': True,
                'publication_status': 'local_candidate_pending_release_approval'}
    (args.output_dir / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps(manifest, indent=2))


if __name__ == '__main__':
    main()
