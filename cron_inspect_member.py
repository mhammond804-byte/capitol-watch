#!/usr/bin/env python3
import json

with open('/tmp/cw_member_R000606.json') as f:
    data = json.load(f)

m = data['member']
sl = m['sponsoredLegislation']
print(f"sponsoredLegislation keys: {list(sl.keys())}")
print(f"Count: {sl.get('count')}")
print(f"URL: {sl.get('url')}")

# Check if there's a 'bill' key or 'item'
for key in sl:
    val = sl[key]
    if isinstance(val, list):
        print(f"\n'{key}' is a list with {len(val)} items")
        if val:
            print(f"  First item: {json.dumps(val[0], indent=2)[:300]}")
