#!/usr/bin/env python3
"""Verify a complete candidate package and regenerate its analyses locally."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
from bootstrap_data import digest

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--package-root', type=Path, default=ROOT)
    args = parser.parse_args()
    package = args.package_root.resolve()
    manifest = json.loads((package / 'manifest.json').read_text())
    for entry in manifest['files']:
        path = (package / entry['path']).resolve()
        if not path.is_relative_to(package) or digest(path) != entry['sha256']:
            raise ValueError('Package checksum mismatch: ' + entry['path'])
    print(f"Verified {len(manifest['files'])} package files", flush=True)
    env = os.environ.copy()
    env['PYTHONPATH'] = str(ROOT / 'src') + os.pathsep + env.get('PYTHONPATH', '')
    subprocess.run([sys.executable, str(ROOT/'scripts/bootstrap_data.py'), '--source-dir', str(package/'data/telemetry'), '--config', str(package/'data/telemetry/data_sources.toml')], check=True, env=env)
    subprocess.run([sys.executable, str(ROOT/'scripts/run_all.py'), '--from-public'], check=True, env=env, cwd=ROOT)

if __name__ == '__main__':
    main()
