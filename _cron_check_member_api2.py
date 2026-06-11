#!/usr/bin/env python3
"""Check member API response format more carefully"""
import json, subprocess

result = subprocess.run(
    ["curl", "-s", "https://capitolwatch.us/api/member/M001237"],
    capture_output=True, text=True, timeout=30
)
d = json.loads(result.stdout)
print('Keys:', list(d.keys()))
spon = d.get('sponsored', [])
print(f'sponsored: {len(spon)}')
if spon:
    print('First:', json.dumps(spon[0], indent=2)[:500])
else:
    # Show some structure
    for k in d.keys():
        v = d[k]
        if isinstance(v, dict):
            print(f'{k} keys: {list(v.keys())[:5]}')
            if 'sponsoredLegislation' in v:
                print(f'{k}.sponsoredLegislation: {len(v["sponsoredLegislation"])}')
        elif isinstance(v, list):
            print(f'{k}: list of {len(v)}')
            if v:
                print(f'  first: {json.dumps(v[0])[:200]}')
