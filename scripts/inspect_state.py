#!/usr/bin/env python3
import json

with open("/tmp/state_FL.json") as f:
    data = json.load(f)

print(f"Type: {type(data).__name__}")
if isinstance(data, list):
    print(f"Length: {len(data)}")
    for d in data[:3]:
        print(json.dumps(d, indent=2, default=str)[:600])
        print("---")
elif isinstance(data, dict):
    print(f"Keys: {list(data.keys())}")
    for k, v in list(data.items())[:3]:
        print(f"\n{k}: {json.dumps(v, indent=2, default=str)[:400]}")
