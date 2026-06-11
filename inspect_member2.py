#!/usr/bin/env python3
import json, subprocess

bioguide = "R000622"
tmp = "/tmp/member_R000622.json"
subprocess.run(["curl", "-s", f"https://capitolwatch.us/api/member/{bioguide}", "-o", tmp], capture_output=True)

with open(tmp) as f:
    data = json.load(f)

sp = data["sponsored"]
print("sponsored type:", type(sp).__name__)
if isinstance(sp, dict):
    print("sponsored keys:", list(sp.keys()))
    for k in sp:
        v = sp[k]
        if isinstance(v, list):
            print(f"  {k}: list of {len(v)}")
            if v:
                item = v[0]
                if isinstance(item, dict):
                    print(f"  First item keys: {list(item.keys())}")
                    print(f"  First item: {json.dumps(item, indent=2)[:800]}")
        elif isinstance(v, dict):
            print(f"  {k}: dict with keys {list(v.keys())}")
            if "item" in v:
                items = v["item"]
                print(f"    items count: {len(items)}")
                if items:
                    print(f"    item keys: {list(items[0].keys())}")
                    print(f"    item: {json.dumps(items[0], indent=2)[:800]}")
elif isinstance(sp, list):
    print(f"  sponsored is a list of {len(sp)}")
    if sp:
        print(f"  First: {json.dumps(sp[0], indent=2)[:500]}")
