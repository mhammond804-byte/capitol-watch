import json
d = json.load(open('bill-analysis.json'))
print(f'Total entries: {len(d)}')
# Show first 3 keys
keys = list(d.keys())[:3]
for k in keys:
    print(f'  {k}: {d[k]}')
