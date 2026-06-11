import json

for state, fpath in [('AL', '/tmp/al_state.json'), ('AR', '/tmp/ar_state.json')]:
    with open(fpath) as f:
        data = json.load(f)
    
    members = data.get('house', []) + data.get('senate', [])
    current = []
    for member in members:
        name = member.get('name', '')
        terms = member.get('terms', {}).get('item', [])
        for t in terms:
            sy = t.get('startYear', '')
            chamber = t.get('chamber', '')
            if isinstance(sy, str) and sy:
                sy_int = int(sy)
                if chamber == 'Senate' and sy_int >= 2020:
                    current.append({'bioguideId': member['bioguideId'], 'name': name})
                    break
                elif chamber == 'House of Representatives' and sy_int >= 2023:
                    current.append({'bioguideId': member['bioguideId'], 'name': name})
                    break
    
    print(f'{state} current members ({len(current)}):')
    for m in current:
        print(f'  {m["bioguideId"]} - {m["name"]}')
