import json
d = json.load(open('/tmp/uncached_bills.json'))
print(json.dumps(d, indent=2))
