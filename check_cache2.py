import json
with open('/Users/michaelhammond/Desktop/capitol-watch/bill-analysis.json') as f:
    cache = json.load(f)
ia_keys = [k for k in cache if k.startswith("119/hr/")]
print(f"Total 119/hr/ keys in cache: {len(ia_keys)}")
print(f"Sample 119/hr keys: {sorted(ia_keys)[:15]}")

# Check what specific bills from Nunn would look like
print(f"\nAll 119 keys: {len([k for k in cache if k.startswith('119/')])}")
# Check for a specific bill
print(f"\nHas 119/hr/9072? {'119/hr/9072' in cache}")
print(f"Has 119/hr/8383? {'119/hr/8383' in cache}")
print(f"Has 119/hres/1315? {'119/hres/1315' in cache}")
