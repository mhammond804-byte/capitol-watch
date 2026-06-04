#!/usr/bin/env python3
"""Quick test: fetch a member to see their sponsored bills format."""
import json, urllib.request
from urllib.request import urlopen

# 1. First check the FL state data for a member ID
data = json.load(open("/tmp/state_FL.json"))
print("FL state keys:", list(data.keys()))
house = data.get("house", [])
senate = data.get("senate", [])
print(f"House: {len(house)} reps, Senate: {len(senate)} senators")
first_rep = house[0] if house else None
if first_rep:
    print(f"First rep: {first_rep.get('name')} - bioguide: {first_rep.get('bioguideId')}")
    bid = first_rep.get("bioguideId", "P000599")
    
    # Now fetch that member's bills
    url = f"https://capitolwatch.us/api/member/{bid}"
    print(f"\nFetching member data: {url}")
    r = urlopen(url, timeout=30)
    member_data = json.loads(r.read())
    print(f"Type: {type(member_data).__name__}")
    if isinstance(member_data, dict):
        print(f"Keys: {list(member_data.keys())}")
        for k, v in member_data.items():
            if isinstance(v, list):
                print(f"  {k}: list of {len(v)} items")
                if v and isinstance(v[0], dict):
                    print(f"  First item keys: {list(v[0].keys())}")
                    print(f"  Sample: {json.dumps(v[0], indent=2)[:400]}")
            elif isinstance(v, dict):
                print(f"  {k}: dict with keys {list(v.keys())[:10]}")
            else:
                print(f"  {k}: {str(v)[:200]}")
    elif isinstance(member_data, list):
        print(f"List of {len(member_data)}")
        if member_data and isinstance(member_data[0], dict):
            print(f"First item keys: {list(member_data[0].keys())}")
    else:
        print(f"Value: {str(member_data)[:500]}")
