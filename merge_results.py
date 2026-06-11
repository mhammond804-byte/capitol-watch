#!/usr/bin/env python3
"""Merge all batch results into bill-analysis.json and commit."""
import json
import subprocess
import os

BILL_CACHE_PATH = "/Users/michaelhammond/Desktop/capitol-watch/bill-analysis.json"
REPO_PATH = "/Users/michaelhammond/Desktop/capitol-watch"

# Load existing cache
with open(BILL_CACHE_PATH) as f:
    cache = json.load(f)

print(f"Existing cache: {len(cache)} bills")

# Load all batch results
added = 0
for i in range(1, 9):
    path = f"/tmp/batch_{i}_result.json"
    if not os.path.exists(path):
        print(f"  Batch {i}: not found, skipping")
        continue
    with open(path) as f:
        batch = json.load(f)
    for key, data in batch.items():
        if key in cache:
            continue
        # Normalize key to lowercase
        cache[key.lower()] = {
            "pros": data.get("pros", []),
            "cons": data.get("cons", []),
        }
        added += 1
    print(f"  Batch {i}: {len(batch)} bills merged")

print(f"\nTotal added: {added}")
print(f"New cache size: {len(cache)} bills")

# Write back
with open(BILL_CACHE_PATH, "w") as f:
    json.dump(cache, f, indent=2)

print(f"Written to {BILL_CACHE_PATH}")

# Git commit
os.chdir(REPO_PATH)
r = subprocess.run(["git", "add", "bill-analysis.json"], capture_output=True, text=True)
print(f"git add: {r.stdout.strip()}")

r = subprocess.run(["git", "diff", "--cached", "--stat"], capture_output=True, text=True)
print(f"Changes: {r.stdout.strip()}")

r = subprocess.run(
    ["git", "commit", "-m", f"Add pros/cons for {added} member-sponsored bills from AK, DE, ND"],
    capture_output=True, text=True
)
print(f"git commit: {r.stdout.strip()}{r.stderr.strip()}")

# Push
r = subprocess.run(["git", "push"], capture_output=True, text=True)
print(f"git push: {r.stdout.strip()}{r.stderr.strip()}")

print("\nDone!")
