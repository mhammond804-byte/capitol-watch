#!/usr/bin/env python3
"""Get all active FL members (any start year, no end year) and also try to get FL senators via member API."""
import json, subprocess

# All active FL House members
out = subprocess.run(["curl", "-s", "https://capitolwatch.us/api/state/FL"], capture_output=True, text=True)
d = json.loads(out.stdout)

print("=== FL ACTIVE HOUSE ===")
active_house = []
for m in d.get('house', []):
    for t in m.get('terms', {}).get('item', []):
        if t.get('endYear') is None and t.get('chamber') == 'House of Representatives':
            active_house.append({'name': m['name'], 'bioguide': m['bioguideId'], 'start': t.get('startYear')})
            break

print(f"Count: {len(active_house)}")
for m in sorted(active_house, key=lambda x: x['name']):
    print(f"  {m['bioguide']} - {m['name']} (start={m['start']})")

# Also fetch both FL senators by known bioguide IDs
# Rick Scott = S001217, Marco Rubio = R000595 (let me verify with a search)
senators_to_check = ['S001217', 'R000595']
print("\n=== FL SENATORS (direct fetch) ===")
for bid in senators_to_check:
    out = subprocess.run(["curl", "-s", f"https://capitolwatch.us/api/member/{bid}"], capture_output=True, text=True)
    try:
        data = json.loads(out.stdout)
        name = data.get('name', 'N/A')
        print(f"  {bid} - {name}")
    except:
        print(f"  {bid} - failed to fetch")
