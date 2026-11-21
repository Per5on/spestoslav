#!/usr/bin/env python3
"""Set candidate metadata and regenerate derived package/registry fields, without building."""
import argparse
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]


def synchronize(sequence,version,check=False):
    if not re.fullmatch(r'[0-9]{3}',sequence) or int(sequence)<1:raise ValueError('Use a positive three-digit sequence')
    if not re.fullmatch(r'\d+\.\d+\.\d+',version):raise ValueError('Use a semantic app version')
    source_path=ROOT/'mobile/preview.json'
    registry_path=ROOT/'docs/references/preview-sequence.json'
    registry=json.loads(registry_path.read_text())
    next_number=max(int(sequence),*(int(v['version'])+1 for v in registry['versions']))
    values={source_path:{'sequence':sequence,'version':version}}
    registry['next_version']=f'{next_number:03d}'
    registry['metadata_source']='../../mobile/preview.json'
    values[registry_path]=registry
    for name in ['package.json','package-lock.json']:
        path=ROOT/'mobile'/name;data=json.loads(path.read_text());data['version']=version
        if 'packages' in data:data['packages']['']['version']=version
        values[path]=data
    for path,data in values.items():
        if check:
            if json.loads(path.read_text())!=data:raise ValueError(f'Metadata drift: {path.relative_to(ROOT)}')
        else:path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')


if __name__=='__main__':
    source=json.loads((ROOT/'mobile/preview.json').read_text())
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sequence',default=source['sequence']);parser.add_argument('--version',default=source['version']);parser.add_argument('--check',action='store_true');args=parser.parse_args()
    synchronize(args.sequence,args.version,args.check)
    print('Preview metadata checked' if args.check else 'Preview metadata synchronized; no build performed')
