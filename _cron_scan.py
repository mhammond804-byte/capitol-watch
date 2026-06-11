import json

# Load cache
cache = json.load(open('bill-analysis.json'))

# Build set of cached keys (lowercase)
cached_keys = set(k.lower() for k in cache.keys())

# IL members
il_response = json.loads(__import__('urllib.request').request.urlopen('https://capitolwatch.us/api/state/IL').read())
il_members = il_response.get('members', il_response)
print(f'IL members count: {len(il_members)}')
total_uncached = 0

for m in il_members[:15]:  # limit to 15 members to keep it manageable
    bid = m.get('bioguide') if isinstance(m, dict) else m
    if not bid:
        continue
    url = f'https://capitolwatch.us/api/member/{bid}'
    resp = json.loads(__import__('urllib.request').request.urlopen(url).read())
    bills = resp.get('sponsored_legislation', [])
    for bill in bills:
        bill_num = bill.get('number', '')
        parts = bill_num.split('.')
        if len(parts) >= 3:
            congress = parts[0]
            bill_type = parts[1]
            number = parts[2]
            key = f'{congress}/{bill_type}/{number}'.lower()
            if key not in cached_keys and total_uncached < 25:
                print(f'UNcached: {key} (member {bid})')
                total_uncached += 1
            elif key in cached_keys:
                pass  # already cached
    if total_uncached >= 25:
        break

# IN members
in_response = json.loads(__import__('urllib.request').request.urlopen('https://capitolwatch.us/api/state/IN').read())
in_members = in_response.get('members', in_response)
print(f'IN members count: {len(in_members)}')

for m in in_members[:15]:
    bid = m.get('bioguide') if isinstance(m, dict) else m
    if not bid:
        continue
    url = f'https://capitolwatch.us/api/member/{bid}'
    resp = json.loads(__import__('urllib.request').request.urlopen(url).read())
    bills = resp.get('sponsored_legislation', [])
    for bill in bills:
        bill_num = bill.get('number', '')
        parts = bill_num.split('.')
        if len(parts) >= 3:
            congress = parts[0]
            bill_type = parts[1]
            number = parts[2]
            key = f'{congress}/{bill_type}/{number}'.lower()
            if key not in cached_keys and total_uncached < 25:
                print(f'UNcached: {key} (member {bid})')
                total_uncached += 1
            elif key in cached_keys:
                pass
    if total_uncached >= 25:
        break

if total_uncached == 0:
    print('NO_UNCACHED')
else:
    print(f'TOTAL_UNCACHED: {total_uncached}')
