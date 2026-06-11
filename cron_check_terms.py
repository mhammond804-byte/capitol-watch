#!/usr/bin/env python3
import json

with open('/tmp/cw_md.json') as f:
    data = json.load(f)

for bid in ['T000483', 'S001168', 'R000576', 'H000874', 'M001232', 'O000176', 'E000301', 'I000058', 'M000687', 'R000606', 'H001052']:
    found = None
    for ch in ['house', 'senate']:
        for m in data.get(ch, []):
            if m['bioguideId'] == bid:
                found = m
                break
    if found:
        terms = found['terms']['item']
        last = terms[-1]
        print(f"{bid} ({found['name']}): start={last.get('startYear')}, end={last.get('endYear')}, chamber={last.get('chamber')}")
    else:
        print(f"{bid}: NOT FOUND")
