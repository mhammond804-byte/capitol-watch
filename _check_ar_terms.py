import json

with open('/tmp/ar_state.json') as f:
    data = json.load(f)

print("=== AR House ===")
for m in data.get('house', []):
    name = m.get('name','')
    bid = m.get('bioguideId','')
    terms = m.get('terms',{}).get('item',[])
    for t in terms:
        sy = t.get('startYear','')
        ey = t.get('endYear','') or ''
        chamber = t.get('chamber','')
        is_current = (ey == '' or ey is None)
        marker = ' <<<' if is_current else ''
        print(f'  {name} ({bid}): {chamber} {sy}-{ey}{marker}')

print("\n=== AR Senate ===")
for m in data.get('senate', []):
    name = m.get('name','')
    bid = m.get('bioguideId','')
    terms = m.get('terms',{}).get('item',[])
    for t in terms:
        sy = t.get('startYear','')
        ey = t.get('endYear','') or ''
        chamber = t.get('chamber','')
        is_current = (ey == '' or ey is None)
        marker = ' <<<' if is_current else ''
        print(f'  {name} ({bid}): {chamber} {sy}-{ey}{marker}')
