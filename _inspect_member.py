#!/usr/bin/env python3
"""Inspect raw member API response to understand sponsoredLegislation structure."""
import json
import urllib.request

def fetch_json(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read().decode())

# Try Fedorchak (ND House) - most likely to have current bills
url = "https://capitolwatch.us/api/member/F000482"
data = fetch_json(url)

# Check top-level keys
print(f"Top-level keys: {list(data.keys())}")

# Check sponsoredLegislation
sl = data.get('sponsoredLegislation', {})
if sl:
    print(f"\nsponsoredLegislation keys: {list(sl.keys())}")
    # Check what's actually in it
    print(f"\nFull sponsoredLegislation:")
    print(json.dumps(sl, indent=2)[:3000])
else:
    print(f"\nNo sponsoredLegislation found")
    # Print entire response structure (first 2000 chars)
    print(json.dumps(data, indent=2)[:3000])
