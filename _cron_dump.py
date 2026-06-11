import json
import sys

d = json.load(open(sys.argv[1]))
print(json.dumps(d, indent=2)[:3000])
