import json, urllib.request

api_key = "xH3oHkvJab5BzhnVvJ5zXk3bHK5fPqHZ263Asebc"

for num in ['4692', '4673']:
    url = f"https://api.congress.gov/v3/bill/119/s/{num}?format=json&api_key={api_key}"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode())
    
    bill = data.get('bill', {})
    print(f"=== 119/s/{num} ===")
    print(f"Keys: {list(bill.keys())}")
    
    for k in ['title', 'shortTitle', 'popularTitle', 'summaries', 'policyArea', 'subjects']:
        v = bill.get(k)
        if isinstance(v, dict):
            print(f"  {k}: keys={list(v.keys())}")
            if k == 'summaries':
                items = v.get('item', [])
                print(f"    count={v.get('count')}, items={len(items)}")
                for item in items:
                    print(f"    text: {item.get('text','')[:200]}")
            elif k == 'policyArea':
                print(f"    name: {v.get('name','')}")
        else:
            print(f"  {k}: {v}")
    print()
