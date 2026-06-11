#!/usr/bin/env python3
"""Extract bill keys from saved member data files."""
import json

files = {
    'ND_Fedorchak': '/tmp/nd_fedorchak.json',
    'ND_Hoeven': '/tmp/nd_hoeven.json',
    'ND_Cramer': '/tmp/nd_cramer.json',
    'NE_Flood': '/tmp/ne_flood.json',
    'NE_Bacon': '/tmp/ne_bacon.json',
    'NE_Smith': '/tmp/ne_smith.json',
    'NE_Ricketts': '/tmp/ne_ricketts.json',
    'NE_Fischer': '/tmp/ne_fischer.json',
}

all_bills = []
for name, path in files.items():
    with open(path) as f:
        d = json.load(f)
    bills = d.get('sponsored', [])
    for b in bills:
        congress = str(b.get('congress', ''))
        btype = str(b.get('type', b.get('billType', ''))).lower()
        number = str(b.get('number', ''))
        number = number.replace('.0', '') if number.endswith('.0') else number
        if number.endswith('.0'):
            number = str(int(float(number)))
        key = f"{congress}/{btype}/{number}"
        title = b.get('title', b.get('number', ''))
        all_bills.append((name, key, title, congress, btype, number))

current_member = None
for name, key, title, congress, btype, number in all_bills:
    if name != current_member:
        print(f"\n=== {name} ({len([x for x in all_bills if x[0]==name])} bills) ===")
        current_member = name
    print(f"  {key} | {title[:80]}")

# Also check structure
with open('/tmp/nd_fedorchak.json') as f:
    d = json.load(f)
print(f"\n\nTop-level keys: {list(d.keys())}")
if 'sponsored' in d:
    print(f"Sponsored is a list of {len(d['sponsored'])} items")
    if d['sponsored']:
        print(f"Sample keys in sponsored[0]: {list(d['sponsored'][0].keys())}")
