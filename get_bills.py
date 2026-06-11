#!/usr/bin/env python3
"""Get sponsored bills for a member"""
import json, sys, subprocess

bioguide = sys.argv[1]
tmp = f"/tmp/member_{bioguide}.json"

subprocess.run(["curl", "-s", f"https://capitolwatch.us/api/member/{bioguide}", "-o", tmp], capture_output=True)

with open(tmp) as f:
    data = json.load(f)

# Extract sponsored legislation
bills = []
for item in data.get("sponsoredLegislation", {}).get("item", []):
    c = item.get("congress", "")
    t = item.get("type", "").lower()
    n = item.get("number", "")
    if c and t and n:
        bills.append(f"{c}/{t}/{n}")
    # Also try nested structure
    for ref in item.get("references", []):
        pass  # bill number/type may be in different location

# Also try alternative structure
for item in data.get("sponsoredLegislation", []):
    if isinstance(item, dict):
        c = item.get("congress", "")
        t = item.get("type", "").lower()
        n = item.get("number", "")
        key = f"{c}/{t}/{n}"
        if c and t and n and key not in bills:
            bills.append(key)

print(json.dumps(list(set(bills))))
