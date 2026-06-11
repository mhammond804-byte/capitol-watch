#!/usr/bin/env python3
"""Peek at bill structure"""
import json

with open('/tmp/bill_fetch/all_members.json') as f:
    all_bills = json.load(f)

# Get first bill from any member
for mid, bills in all_bills.items():
    if bills:
        print(f"Member {mid} first bill:")
        print(json.dumps(bills[0], indent=2))
        print("\nKeys:", list(bills[0].keys()))
        break
else:
    print("No bills found")
