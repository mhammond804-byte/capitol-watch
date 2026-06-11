#!/usr/bin/env python3
"""Check if some specific TN/TX member bills are in the cache."""
import json, os, subprocess

CACHE_PATH = os.path.expanduser("~/Desktop/capitol-watch/bill-analysis.json")
CONGRESS_API_KEY = "xH3oHkvJab5BzhnVvJ5zXk3bHK5fPqHZ263Asebc"

with open(CACHE_PATH) as f:
    cache = json.load(f)
cached_keys = set(cache.keys())
print(f"Total cache: {len(cached_keys)}")

# TN current members: let's check a few known ones
# Senators: Marsha Blackburn, Bill Hagerty
# Let's check if their bills are cached
test_members = [
    ("TN", "B001243", "Blackburn"),  # Marsha Blackburn
    ("TN", "H000601", "Hagerty"),    # Bill Hagerty
]

for state, bioguide, name in test_members:
    url = f"https://api.congress.gov/v3/member/{bioguide}/sponsored-legislation?format=json&limit=20"
    cmd = ["curl", "-s", "--max-time", "15", "-H", f"X-Api-Key: {CONGRESS_API_KEY}", url]
    r = subprocess.run(cmd, capture_output=True, text=True)
    data = json.loads(r.stdout) if r.stdout else {}
    bills = data.get("sponsoredLegislation", [])
    
    uncached = []
    for b in bills:
        congress = b.get("congress")
        bill_type = b.get("type", "")
        if bill_type:
            bill_type = bill_type.lower()
        number = b.get("number", "")
        if congress and bill_type and number:
            try:
                if int(congress) == 119:
                    key = f"{congress}/{bill_type}/{number}"
                    if key not in cached_keys:
                        uncached.append(key)
            except:
                pass
    
    print(f"{name} ({bioguide}): {len(bills)} bills total, {len(uncached)} uncached in 119th")
    if uncached:
        print(f"  Uncached: {uncached[:5]}")
