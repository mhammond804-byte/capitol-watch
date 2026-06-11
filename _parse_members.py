#!/usr/bin/env python3
import json

for state in ['OR', 'PA']:
    with open(f'/tmp/{state.lower()}_members.json') as f:
        d = json.load(f)
    members = d if isinstance(d, list) else d.get('members', d)
    bioguides = [m['bioguide'] if isinstance(m, dict) else m for m in members]
    print(f'{state} has {len(bioguides)} members')
    print(' '.join(bioguides))
