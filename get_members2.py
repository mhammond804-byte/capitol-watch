#!/usr/bin/env python3
import json, sys, subprocess

def curl_get(url, outpath):
    result = subprocess.run(["curl", "-s", url, "-o", outpath], capture_output=True, text=True)
    return result.returncode

state = sys.argv[1]
tmp_path = f"/tmp/{state}_state.json"

curl_get(f"https://capitolwatch.us/api/state/{state}", tmp_path)

with open(tmp_path) as f:
    data = json.load(f)

members = []
for m in data.get('house', []):
    terms = m['terms']['item']
    latest = max(terms, key=lambda t: t.get('startYear', 0))
    if not latest.get('endYear'):
        members.append(m['bioguideId'])

for m in data.get('senate', []):
    terms = m['terms']['item']
    latest = max(terms, key=lambda t: t.get('startYear', 0))
    if not latest.get('endYear'):
        members.append(m['bioguideId'])

print(','.join(sorted(set(members))))
