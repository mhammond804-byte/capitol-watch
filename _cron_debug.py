import urllib.request, json

# Check state endpoint
resp = json.loads(urllib.request.urlopen('https://capitolwatch.us/api/state/IL').read())
print('Type:', type(resp).__name__)
if isinstance(resp, dict):
    print('Keys:', list(resp.keys()))
    for k, v in resp.items():
        if isinstance(v, list):
            print(f'{k}: list of {len(v)}')
            if v:
                print(f'  First item type: {type(v[0]).__name__}, value: {str(v[0])[:200]}')
        elif isinstance(v, dict):
            print(f'{k}: dict with {len(v)} keys')
            print(f'  Keys: {list(v.keys())[:5]}')
        else:
            print(f'{k}: {str(v)[:100]}')
else:
    print('List length:', len(resp))
    if resp:
        print('First item:', str(resp[0])[:200])
