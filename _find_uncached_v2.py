#!/usr/bin/env python3
"""
Fetch sponsored bills for all members of OR and PA.
Finds uncached bill keys.
"""
import json
import urllib.request
import sys
import os

CACHE_PATH = os.path.expanduser("~/Desktop/capitol-watch/bill-analysis.json")

# Load cache
with open(CACHE_PATH) as f:
    cache = json.load(f)

print(f"Cache has {len(cache)} entries")

# Read bioguides from files we already have
all_bioguides = []
for state in ['OR', 'PA']:
    with open(f'/tmp/{state.lower()}_members.json') as f:
        d = json.load(f)
    for chamber in ['house', 'senate']:
        for m in d.get(chamber, []):
            all_bioguides.append((state, m['bioguideId']))

print(f"Total members to check: {len(all_bioguides)}")

uncached_bills = {}
for state, bg in all_bioguides:
    url = f"https://capitolwatch.us/api/member/{bg}"
    try:
        req = urllib.request.Request(url)
        req.add_header("User-Agent", "Capitol-Watch/1.0 (research; contact@capitolwatch.us)")
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
    except Exception as e:
        print(f"  ERROR fetching {bg}: {e}")
        continue
    
    sponsored = data.get('sponsored', [])
    for bill in sponsored:
        congress = bill.get('congress', '')
        bill_type = (bill.get('type') or '').lower()
        bill_number = bill.get('number', '')
        if congress and bill_type and bill_number:
            key = f"{congress}/{bill_type}/{bill_number}".lower()
            if key not in cache and key not in uncached_bills:
                uncached_bills[key] = {
                    'congress': congress,
                    'type': bill_type,
                    'number': bill_number,
                    'title': bill.get('title', ''),
                }
    
    print(f"  {state} {bg}: {len(sponsored)} sponsored, {len(uncached_bills)} uncached so far")

print(f"\nTotal uncached bills found: {len(uncached_bills)}")

# Write out uncached bill keys
with open('/tmp/uncached_bills.txt', 'w') as f:
    for bk in sorted(uncached_bills.keys()):
        f.write(bk + '\n')

# Also write a JSON with details for processing
with open('/tmp/uncached_bills_details.json', 'w') as f:
    json.dump(uncached_bills, f, indent=2)

print("Written to /tmp/uncached_bills.txt and /tmp/uncached_bills_details.json")
