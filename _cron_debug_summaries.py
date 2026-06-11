#!/usr/bin/env python3
"""Debug: check what the congress.gov API returns for summaries"""
import json, subprocess

API_KEY = "xH3oHkvJab5BzhnVvJ5zXk3bHK5fPqHZ263Asebc"

# Let's try a few known bills from MI members to see if summaries are available
test_bills = [
    ("119", "hr", "8698"),   # Lower Prices at... - M001237
    ("119", "hr", "8056"),   # Military Financial Literacy Act - M001237
    ("119", "hr", "8305"),   # Working Parents Tax Relief Act - M001237
]

for congress, bill_type, number in test_bills:
    url = f"https://api.congress.gov/v3/bill/{congress}/{bill_type}/{number}/summaries?format=json"
    result = subprocess.run(
        ["curl", "-s", "-H", f"X-Api-Key: {API_KEY}", url],
        capture_output=True, text=True, timeout=15
    )
    data = json.loads(result.stdout)
    summaries = data.get('summaries', [])
    print(f"{congress}/{bill_type}/{number}: {len(summaries)} summaries")
    if summaries:
        print(f"  Text: {summaries[0].get('text', '')[:200]}")
        print(f"  Keys: {list(summaries[0].keys())}")
    else:
        print(f"  Full response: {json.dumps(data)[:300]}")
