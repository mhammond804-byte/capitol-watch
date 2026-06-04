#!/usr/bin/env python3
"""Deep inspect the bill cache structure."""
import json, os

CACHE_FILE = os.path.expanduser("~/Desktop/capitol-watch/bill-analysis.json")

with open(CACHE_FILE) as f:
    cache = json.load(f)

print(f"Total entries: {len(cache)}")

# Show first 10 entries
count = 0
for key, val in list(cache.items())[:10]:
    print(f"\n--- Key: {key!r} ---")
    if isinstance(val, dict):
        for k, v in val.items():
            sv = str(v)
            if len(sv) > 200:
                sv = sv[:197] + "..."
            print(f"  {k}: {sv}")
    else:
        print(f"  Value: {str(val)[:300]}")

# Show last 5 entries
print("\n\n--- LAST 5 ENTRIES ---")
for key, val in list(cache.items())[-5:]:
    print(f"\n  Key: {key!r}")
    if isinstance(val, dict):
        print(f"    Keys: {list(val.keys())}")
        print(f"    Title: {str(val.get('title',''))[:80]}")
        print(f"    Has pros: {bool(val.get('pros'))}")
        print(f"    Has cons: {bool(val.get('cons'))}")
    else:
        print(f"    Value: {str(val)[:200]}")

# Count entries with specific keys
has_pros = sum(1 for v in cache.values() if isinstance(v, dict) and v.get("pros"))
has_cons = sum(1 for v in cache.values() if isinstance(v, dict) and v.get("cons"))
has_title = sum(1 for v in cache.values() if isinstance(v, dict) and v.get("title"))
has_sponsor = sum(1 for v in cache.values() if isinstance(v, dict) and v.get("sponsor_name"))
is_dict = sum(1 for v in cache.values() if isinstance(v, dict))

print(f"\n\nDict entries: {is_dict}")
print(f"Entries with 'pros': {has_pros}")
print(f"Entries with 'cons': {has_cons}")
print(f"Entries with 'title': {has_title}")
print(f"Entries with 'sponsor_name': {has_sponsor}")
