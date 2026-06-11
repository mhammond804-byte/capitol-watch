import json, subprocess

r = subprocess.run(["curl", "-s", "--max-time", "15", "https://capitolwatch.us/api/member/W000821"],
                   capture_output=True, text=True)
d = json.loads(r.stdout)
print("Top-level keys:")
for k in d.keys():
    print(f"  {k}")
# Check if there's a sponsoredLegislation key
if "sponsoredLegislation" in d:
    print(f"\nsponsoredLegislation has {len(d['sponsoredLegislation'])} items")
elif "bills" in d:
    print(f"\nbills has {len(d['bills'])} items")
else:
    # Look for any array
    for k, v in d.items():
        if isinstance(v, list):
            print(f"\n  '{k}' is a list with {len(v)} items")
            if v:
                print(f"    Sample item: {json.dumps(v[0], indent=2)[:300]}")
