#!/usr/bin/env python3
"""Analyze current bill cache: count bills, find which ones have pros/cons, and check gaps."""
import json, os

CACHE_FILE = os.path.expanduser("~/Desktop/capitol-watch/bill-analysis.json")

with open(CACHE_FILE) as f:
    cache = json.load(f)

print(f"Total bills in cache: {len(cache)}")

# Count bills WITH and WITHOUT pros/cons
with_pros = 0
without_pros = 0
for key, val in cache.items():
    if isinstance(val, dict) and val.get("pros") and val.get("cons"):
        with_pros += 1
    else:
        without_pros += 1

print(f"Bills WITH pros/cons: {with_pros}")
print(f"Bills WITHOUT pros/cons: {without_pros}")

# Show a few keys from each category
print("\n--- Sample keys WITH pros/cons ---")
count = 0
for key, val in cache.items():
    if isinstance(val, dict) and val.get("pros") and val.get("cons"):
        print(f"  {key}: {str(val.get('title',''))[:80]}")
        count += 1
        if count >= 3:
            break

print("\n--- Sample keys WITHOUT pros/cons ---")
count = 0
for key, val in cache.items():
    if not (isinstance(val, dict) and val.get("pros") and val.get("cons")):
        print(f"  {key}: {str(val.get('title',''))[:80]}")
        count += 1
        if count >= 3:
            break

# Also show bill BI (Congress.gov) vs non-BI analysis
# Check if there's a sponsor_name field
has_sponsor = 0
no_sponsor = 0
for key, val in cache.items():
    if isinstance(val, dict) and val.get("sponsor_name"):
        has_sponsor += 1
    else:
        no_sponsor += 1

print(f"\nWith sponsor_name: {has_sponsor}")
print(f"Without sponsor_name: {no_sponsor}")
