#!/usr/bin/env python3
import json

for state in ['OR', 'PA']:
    with open(f'/tmp/{state.lower()}_members.json') as f:
        d = json.load(f)
    bioguides = []
    for chamber in ['house', 'senate']:
        for m in d.get(chamber, []):
            bioguides.append(m['bioguideId'])
    print(f'{state}: {len(bioguides)} members')
    print(' '.join(bioguides))
    print()
