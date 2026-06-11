import json
with open('/tmp/member_F000481.json') as f:
    data = json.load(f)
print("Top-level keys:", list(data.keys()))
for k, v in data.items():
    if isinstance(v, dict):
        print(f"  {k}: dict with keys {list(v.keys())}")
    elif isinstance(v, list):
        print(f"  {k}: list of {len(v)} items")
        if v:
            print(f"    first item keys: {list(v[0].keys()) if isinstance(v[0], dict) else type(v[0])}")
    else:
        print(f"  {k}: {type(v).__name__} = {str(v)[:100]}")
