import json

with open('/tmp/al_state.json') as f:
    data = json.load(f)

print("=== AL House ===")
for m in data.get('house', []):
    name = m.get('name','')
    bid = m.get('bioguideId','')
    terms = m.get('terms',{}).get('item',[])
    for t in terms:
        sy = t.get('startYear','')
        ey = t.get('endYear','')
        chamber = t.get('chamber','')
        print(f'  {name} ({bid}): {chamber} {sy}-{ey}')

print("\n=== AL Senate ===")
for m in data.get('senate', []):
    name = m.get('name','')
    bid = m.get('bioguideId','')
    terms = m.get('terms',{}).get('item',[])
    for t in terms:
        sy = t.get('startYear','')
        ey = t.get('endYear','')
        chamber = t.get('chamber','')
        print(f'  {name} ({bid}): {chamber} {sy}-{ey}')
