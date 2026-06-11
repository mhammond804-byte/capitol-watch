#!/usr/bin/env python3
import json
with open('/Users/michaelhammond/Desktop/capitol-watch/bill-analysis.json') as f:
    data = json.load(f)
print(f'Total cache entries: {len(data)}')
