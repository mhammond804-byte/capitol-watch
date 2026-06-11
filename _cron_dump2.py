import json
d = json.load(open('/tmp/test_member.json'))
print(json.dumps(d, indent=2)[:4000])
