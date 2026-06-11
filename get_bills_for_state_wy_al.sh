#!/bin/bash
# Get members for Wyoming (WY) - check members endpoint first
curl -s "https://capitolwatch.us/api/state/WY" | python3 -c "
import json, sys
data = json.load(sys.stdin)
print('Members found:', len(data) if isinstance(data, list) else 'not a list')
print(json.dumps(data, indent=2)[:2000])
"
