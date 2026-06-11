#!/usr/bin/env python3
"""Look at existing entries in cache to understand the pros/cons approach"""
import json

with open("/Users/michaelhammond/Desktop/capitol-watch/bill-analysis.json") as f:
    data = json.load(f)

# Look at recent 118th Congress entries
count = 0
for key, entry in data.items():
    if key.startswith("118/hr/") and count < 3:
        print(f"Key: {key}")
        print(f"  Pros: {entry.get('pros', [])}")
        print(f"  Cons: {entry.get('cons', [])}")
        count += 1

# Check a few more from different types
print("\n--- Other types ---")
for key, entry in data.items():
    if key.startswith("118/s") and count < 6:
        print(f"Key: {key}")
        print(f"  Pros: {entry.get('pros', [])}")
        print(f"  Cons: {entry.get('cons', [])}")
        count += 1
    if count >= 9:
        break

# Check if ALL bills have the same generic pros/cons
print("\n--- Analyzing variety ---")
unique_pros = set()
unique_cons = set()
for key, entry in list(data.items())[:500]:
    for p in entry.get('pros', []):
        unique_pros.add(p)
    for c in entry.get('cons', []):
        unique_cons.add(c)
print(f"Unique pros in first 500: {len(unique_pros)}")
print(f"Unique cons in first 500: {len(unique_cons)}")
print("Sample pros:", list(unique_pros)[:5])
print("Sample cons:", list(unique_cons)[:5])
