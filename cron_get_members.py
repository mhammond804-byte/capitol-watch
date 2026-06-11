#!/usr/bin/env python3
import json, urllib.request, sys

state = sys.argv[1]
url = f"https://capitolwatch.us/api/state/{state}"
try:
    data = json.loads(urllib.request.urlopen(url, timeout=30).read())
    # Get bioguide IDs
    members = []
    if isinstance(data, list):
        members = data
    elif isinstance(data, dict):
        members = data.get('members', data.get('data', []))
    bioguides = []
    for m in members:
        if isinstance(m, dict):
            bg = m.get('bioguide', m.get('bioguideId', m.get('id', '')))
            if bg:
                bioguides.append(bg)
        elif isinstance(m, str):
            bioguides.append(m)
    print(json.dumps(bioguides))
except Exception as e:
    print(f"ERROR: {e}", file=sys.stderr)
    print("[]")
