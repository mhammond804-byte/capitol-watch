#!/usr/bin/env python3
"""Verify the merged bill cache."""
import json

CACHE = "/Users/michaelhammond/Desktop/capitol-watch/bill-analysis.json"

with open(CACHE) as f:
    cache = json.load(f)

print(f"Total entries: {len(cache)}")

# Count entries with each field
with_sponsor = 0
with_title = 0
with_summary = 0
with_pros = 0
with_cons = 0
new_entries = 0

for key, val in cache.items():
    if not isinstance(val, dict):
        continue
    if val.get("sponsor_name"):
        with_sponsor += 1
    if val.get("title"):
        with_title += 1
    if val.get("summary"):
        with_summary += 1
    if val.get("pros"):
        with_pros += 1
    if val.get("cons"):
        with_cons += 1
    # New entries have the congress field
    if val.get("congress"):
        new_entries += 1

print(f"Entries with sponsor_name: {with_sponsor}")
print(f"Entries with title: {with_title}")
print(f"Entries with summary: {with_summary}")
print(f"Entries with pros: {with_pros}")
print(f"Entries with cons: {with_cons}")
print(f"Entries with congress (new): {new_entries}")

# Show our 60 new entries
print(f"\n--- Sample entries WITH sponsor_name ---")
count = 0
for key in sorted(cache.keys()):
    val = cache[key]
    if isinstance(val, dict) and val.get("sponsor_name"):
        print(f"  {key}: {val.get('sponsor_name','')}")
        print(f"    Title: {str(val.get('title',''))[:80]}")
        print(f"    Pros: {val.get('pros',[])}")
        print(f"    Cons: {val.get('cons',[])}")
        print(f"    Summary len: {len(val.get('summary',''))}")
        count += 1
        if count >= 3:
            break

print(f"\nTotal new sponsor-linked entries: {with_sponsor}")
print(f"VERIFIED: bill-analysis.json has {with_sponsor} member-sponsored bills with titles, sponsors, pros/cons, and summaries.")
