#!/usr/bin/env python3
"""Check member API response format for M001237"""
import json, subprocess

result = subprocess.run(
    ["curl", "-s", "https://capitolwatch.us/api/member/M001237"],
    capture_output=True, text=True, timeout=30
)
d = json.loads(result.stdout)
print('Keys:', list(d.keys()))
spon = d.get('sponsoredLegislation', [])
print(f'Sponsored: {len(spon)} bills')
if spon:
    for i, bill in enumerate(spon[:3]):
        print(f'Bill {i}: {json.dumps(bill)[:300]}')
