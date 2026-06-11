#!/usr/bin/env python3
"""Get all sponsored bills for a list of bioguide IDs and check which are uncached"""
import json, subprocess, sys

all_bills = set()

def get_member_bills(bioguide):
    tmp = f"/tmp/member_{bioguide}.json"
    subprocess.run(["curl", "-s", f"https://capitolwatch.us/api/member/{bioguide}", "-o", tmp], capture_output=True)
    with open(tmp) as f:
        data = json.load(f)
    
    bills = []
    for item in data.get("sponsored", []):
        c = item.get("congress") or ""
        t = (item.get("type") or "").lower()
        n = item.get("number") or ""
        if c and t and n:
            key = f"{c}/{t}/{n}"
            bills.append(key)
    return bills

# Load existing cache
with open("/Users/michaelhammond/Desktop/capitol-watch/bill-analysis.json") as f:
    cache = json.load(f)

# Get bills from all members
state = sys.argv[1]
members = sys.argv[2].split(",")
total_new = 0

for m in members:
    member_bills = get_member_bills(m)
    for bill_key in member_bills:
        all_bills.add(bill_key)

# Find uncached ones
uncached = []
for key in sorted(all_bills):
    if key not in cache:
        uncached.append(key)
        if len(uncached) >= 20:
            break

print(json.dumps({
    "state": state,
    "total_bills_found": len(all_bills),
    "uncached_count": len(uncached),
    "uncached_bills": uncached[:20]
}))
