#!/usr/bin/env python3
import json

with open('/tmp/or_members.json') as f:
    d = json.load(f)
print(type(d))
print(list(d.keys()) if isinstance(d, dict) else 'list')
# Show top-level keys and sample value
if isinstance(d, dict):
    for k, v in d.items():
        if isinstance(v, list):
            print(f'{k}: list of {len(v)}')
            if v:
                print(f'  sample: {json.dumps(v[0], indent=2)[:300]}')
        elif isinstance(v, dict):
            print(f'{k}: dict with keys {list(v.keys())[:5]}')
        else:
            print(f'{k}: {v}')
