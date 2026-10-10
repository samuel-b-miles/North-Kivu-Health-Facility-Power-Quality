#!/usr/bin/env python3
"""Freeze generated reference outputs, refresh manifest and archive a tested candidate."""
import argparse
import csv
import json
import shutil
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED, ZIP_STORED
from bootstrap_data import digest


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--package-root',type=Path,required=True);args=parser.parse_args()
    package=args.package_root.resolve()
    references=package/'reference_outputs'
    for source in (package/'outputs/generated').rglob('*'):
        if source.is_file() and source.suffix in {'.csv','.svg'}:
            if source.name in {'facility_mapping_audit.csv','duplicate_columns_audit.csv'}:
                raise ValueError('Private source audits must not be packaged')
            dest=references/source.relative_to(package/'outputs/generated');dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,dest)
    manifest=json.loads((package/'manifest.json').read_text())
    files=[]
    for p in sorted(package.rglob('*')):
        rel=p.relative_to(package)
        if not p.is_file() or rel.parts[0] in {'outputs','.pytest_cache'} or '__pycache__' in rel.parts or rel.parts[:2]==('data','raw') or p.name=='manifest.json':continue
        entry={'path':rel.as_posix(),'bytes':p.stat().st_size,'sha256':digest(p)}
        if p.suffix=='.csv':
            with p.open(newline='') as f:
                reader=csv.reader(f);entry['columns']=next(reader);entry['rows']=sum(1 for _ in reader)
        files.append(entry)
    manifest['files']=files
    (package/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    archive=package.parent/(package.name+'.zip')
    with ZipFile(archive,'w') as z:
        for entry in files:
            p=package/entry['path'];z.write(p,entry['path'],compress_type=ZIP_STORED if p.suffix in {'.zip','.png','.pdf'} else ZIP_DEFLATED)
        z.write(package/'manifest.json','manifest.json',compress_type=ZIP_DEFLATED)
    (archive.parent/(archive.name+'.sha256')).write_text(digest(archive)+'  '+archive.name+'\n')
    print(f'Archived {len(files)} manifested files; {archive.stat().st_size:,} bytes; {archive}')

if __name__=='__main__':main()
