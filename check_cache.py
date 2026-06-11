#!/usr/bin/env python3
"""Verify a few sample bills are in the cache."""
import json
d = json.load(open('bill-analysis.json'))
samples = ['119/hr/9141','119/s/4040','119/s/4637','119/hr/8671','119/hr/8722','119/hr/8528','119/sres/747','119/s/4669']
for s in samples:
    print(f'{s}: {"FOUND in cache" if s in d else "NOT in cache"}')
