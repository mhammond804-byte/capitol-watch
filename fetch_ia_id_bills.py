#!/usr/bin/env python3
"""Fetch bills for IA and ID current members, find uncached ones."""
import json
import os
import sys
import urllib.request
import urllib.error

API_BASE = "https://capitolwatch.us/api/member"
CACHE_PATH = "/Users/michaelhammond/Desktop/capitol-watch/bill-analysis.json"

# Current members of IA and ID
members = {
    "IA": ["N000193", "M001215", "H001091", "F000446", "G000386", "E000295"],
    "ID": ["F000469", "S001148", "R000584", "C000880"]
}

def fetch_json(url):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "CapitolWatch/1.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        print(f"  ERROR fetching {url}: {e}", file=sys.stderr)
        return None

# Load cache
if os.path.exists(CACHE_PATH):
    with open(CACHE_PATH) as f:
        cache = json.load(f)
else:
    cache = {}
print(f"Cache loaded: {len(cache)} entries", file=sys.stderr)

def make_cache_key(congress, bill_type, number):
    return f"{congress}/{bill_type}/{number}".lower()

# Collect all bills from current members
all_bills = []  # list of (state, name, congress, bill_type, number)
for state, bioguides in members.items():
    for bid in bioguides:
        print(f"Fetching {state}: {bid}...", file=sys.stderr)
        data = fetch_json(f"{API_BASE}/{bid}")
        if not data:
            continue
        name = data.get("member", {}).get("name", bid)
        sponsored = data.get("sponsored", [])
        print(f"  {name}: {len(sponsored)} sponsored items", file=sys.stderr)
        for item in sponsored:
            congress = item.get("congress")
            bill_type = item.get("type")
            number = item.get("number")
            # Skip amendments (no type)
            if not bill_type or not number:
                continue
            all_bills.append((state, name, congress, bill_type, number))

# Find uncached
uncached = []
seen_keys = set()
for state, name, congress, bill_type, number in all_bills:
    key = make_cache_key(congress, bill_type, number)
    if key in seen_keys:
        continue
    seen_keys.add(key)
    if key not in cache:
        uncached.append((state, name, congress, bill_type, number))

print(f"\nTotal uncached bills for IA, ID: {len(uncached)}", file=sys.stderr)
for state, name, congress, bill_type, number in uncached[:20]:
    print(f"  {state}: {congress}/{bill_type}/{number} ({name})")

# Write list to file
with open("/tmp/uncached_bills.json", "w") as f:
    json.dump(uncached[:20], f)

print(f"\nWrote {min(len(uncached), 20)} uncached bills to /tmp/uncached_bills.json", file=sys.stderr)
