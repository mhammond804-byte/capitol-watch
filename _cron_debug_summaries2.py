#!/usr/bin/env python3
"""Check if summaries are available for older bills (118th Congress)"""
import json, subprocess

API_KEY = "xH3oHkvJab5BzhnVvJ5zXk3bHK5fPqHZ263Asebc"

bill_ids = [
    ("118", "hr", "9919"),
    ("118", "hr", "8352"),
    ("118", "hr", "8305"),
]

for congress, bill_type, number in bill_ids:
    url = "https://api.congress.gov/v3/bill/{}/{}/{}?format=json".format(congress, bill_type, number)
    result = subprocess.run(
        ["curl", "-s", "-H", "X-Api-Key: " + API_KEY, url],
        capture_output=True, text=True, timeout=15
    )
    data = json.loads(result.stdout)
    bill = data.get('bill', {})
    title = bill.get('title', 'N/A')
    print("{}: '{}'".format(bill_ids, title[:100]))
    # Check if there's any text content
    keys = list(bill.keys())
    for k in keys[:15]:
        v = bill[k]
        if isinstance(v, str) and len(v) > 20:
            print("  {} ({} chars): {}".format(k, len(v), v[:150]))
