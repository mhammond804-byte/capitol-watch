import json, sys, urllib.request

def get_current_members(state_code):
    url = f"https://capitolwatch.us/api/state/{state_code}"
    with urllib.request.urlopen(url) as resp:
        data = json.loads(resp.read().decode())
    
    current = []
    for member in data.get('house', []) + data.get('senate', []):
        name = member.get('name', '')
        terms = member.get('terms', {}).get('item', [])
        for t in terms:
            sy = t.get('startYear', '')
            chamber = t.get('chamber', '')
            if isinstance(sy, str) and sy and int(sy) >= 2020:
                if chamber == 'Senate' or (chamber == 'House of Representatives' and int(sy) >= 2023):
                    current.append({'bioguideId': member['bioguideId'], 'name': name, 'chamber': chamber})
                    break
    return current

for state in sys.argv[1:]:
    members = get_current_members(state)
    print(f"\n{state} current members ({len(members)}):")
    for m in members:
        print(f"  {m['bioguideId']} - {m['name']} ({m['chamber']})")
