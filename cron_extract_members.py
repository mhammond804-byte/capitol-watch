#!/usr/bin/env python3
"""Extract current member bioguide IDs from state API data."""
import json

for state in ['MD', 'ME']:
    with open(f'/tmp/cw_{state.lower()}.json') as f:
        data = json.load(f)
    
    current = []
    for chamber in ['house', 'senate']:
        for m in data.get(chamber, []):
            terms = m.get('terms', {}).get('item', [])
            if terms:
                last = terms[-1]
                end = last.get('endYear')
                if end is None:
                    current.append({
                        'bioguideId': m['bioguideId'],
                        'name': m['name'],
                        'chamber': last.get('chamber', '?'),
                        'party': m.get('partyName', '?'),
                        'state': state,
                        'district': m.get('district', '')
                    })
    
    print(f"\n=== {state} ===")
    for c in current:
        dst = f" (D{c['district']})" if c.get('district') else ""
        print(f"  {c['chamber']:25s} {c['bioguideId']:12s} {c['name']:30s} {c['party']:12s}{dst}")
    print(f"  Total: {len(current)}")
    
    # Save bioguide list
    ids = [c['bioguideId'] for c in current]
    with open(f'/tmp/cw_{state.lower()}_bioguides.json', 'w') as f:
        json.dump(ids, f)
