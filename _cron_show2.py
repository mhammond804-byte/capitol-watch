import json
import sys

for fname in sys.argv[1:]:
    print(f"\n=== {fname} ===")
    d = json.load(open(fname))
    print(json.dumps(d, indent=2)[:2000])
