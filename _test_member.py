#!/usr/bin/env python3
import json

with open('/tmp/test_member_D000635.json') as f:
    d = json.load(f)
print('Keys:', list(d.keys()))
# Show sample sponsored bill
sponsored = d.get('sponsored', d.get('sponsoredLegislation', d.get('bills', [])))
print(f'sponsored count: {len(sponsored) if isinstance(sponsored, list) else "not a list"}')
if isinstance(sponsored, list) and sponsored:
    print('Sample bill keys:', list(sponsored[0].keys()))
    print('Sample bill:', json.dumps(sponsored[0], indent=2)[:500])
