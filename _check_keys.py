import json
with open('/Users/michaelhammond/Desktop/capitol-watch/_bill_keys.json') as f:
    d = json.load(f)
print(f'AL: {len(d["AL"])} AR: {len(d["AR"])}')
print('AL samples:', d['AL'][:10])
print('AR samples:', d['AR'][:10])
