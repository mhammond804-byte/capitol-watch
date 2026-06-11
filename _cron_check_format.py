#!/usr/bin/env python3
"""Check MI API response format"""
import json, subprocess

result = subprocess.run(
    ["curl", "-s", "https://capitolwatch.us/api/state/MI"],
    capture_output=True, text=True, timeout=30
)
data = json.loads(result.stdout)
print(f"Type: {type(data)}")
print(f"Keys: {list(data.keys()) if isinstance(data, dict) else 'is list'}")
if isinstance(data, dict):
    for k, v in data.items():
        if isinstance(v, list):
            print(f"{k}: list of {len(v)} items")
            if v:
                print(f"  First item type: {type(v[0])}")
                print(f"  First item: {json.dumps(v[0], indent=2)[:500]}")
