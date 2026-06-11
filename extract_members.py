import json

with open('/tmp/ga_members.json') as f:
    ga = json.load(f)
with open('/tmp/hi_members.json') as f:
    hi = json.load(f)

def current_members(data):
    ids = set()
    for chamber in ['house', 'senate']:
        for m in data.get(chamber, []):
            terms = m.get('terms', {}).get('item', [])
            latest = terms[-1] if terms else {}
            if 'endYear' not in latest or latest.get('endYear') is None:
                ids.add(m['bioguideId'])
    return sorted(ids)

ga_ids = current_members(ga)
hi_ids = current_members(hi)
print('GA current:', ga_ids)
print('HI current:', hi_ids)
