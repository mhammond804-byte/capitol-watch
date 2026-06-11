#!/usr/bin/env python3
"""Check sponsored bill structure more carefully"""
import json, subprocess

result = subprocess.run(
    ["curl", "-s", "https://capitolwatch.us/api/member/M001237"],
    capture_output=True, text=True, timeout=30
)
d = json.loads(result.stdout)
spon = d.get('sponsored', [])
print(f'Total: {len(spon)}')
for bill in spon[:3]:
    print(json.dumps(bill, indent=2)[:400])
    print('---')
