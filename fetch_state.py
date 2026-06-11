import json, urllib.request, sys

state = sys.argv[1]
url = f'https://capitolwatch.us/api/state/{state}'
req = urllib.request.Request(url)
try:
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read())
        print(json.dumps(data, indent=2))
except Exception as e:
    print(f'Error: {e}')
    sys.exit(1)
