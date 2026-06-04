#!/usr/bin/env python3
"""Inspect the ready_for_pros_cons.json file structure."""
import json

with open("/tmp/ready_for_pros_cons.json") as f:
    data = json.load(f)

print(f"Top-level keys: {list(data.keys())}")
summaries = data.get("summaries", {})
print(f"Bills count: {len(summaries)}")

keys = sorted(summaries.keys())[:3]
for k in keys:
    v = summaries[k]
    print(f"\n--- {k} ---")
    print(f"  title: {v.get('title','')[:80]}")
    print(f"  sponsor: {v.get('sponsor_name','')}")
    print(f"  summary len: {len(v.get('summary',''))}")
    print(f"  summary: {v.get('summary','')[:200]}")
    print(f"  congress: {v.get('congress')}")
    print(f"  type: {v.get('type')}")
    print(f"  number: {v.get('number')}")
