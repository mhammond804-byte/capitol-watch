#!/usr/bin/env python3
import json

# Load the cache for lookup
with open('/Users/michaelhammond/Desktop/capitol-watch/bill-analysis.json') as f:
    cache = json.load(f)

# All state codes in alphabetical order
all_states = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"]

# IL and IN already done last run. Pick the next 2: KS and KY
state1 = "KS"
state2 = "KY"

print(f"Target states this run: {state1}, {state2}")

# Quick check: what bills are cached by parsing key prefixes? 
# Cache keys are like "congress/type/number"
# We need to know which members to skip. Let's first get members for these states.
