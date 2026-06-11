#!/usr/bin/env python3
"""Fetch members for MI from capitolwatch.us API"""
import json, urllib.request

url = "https://capitolwatch.us/api/state/MI"
req = urllib.request.urlopen(url, timeout=30)
data = json.loads(req.read())
members = [m['bioguide'] for m in data]
print(f"MI has {len(members)} members")
print(json.dumps(members))
