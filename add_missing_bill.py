#!/usr/bin/env python3
import json
from datetime import datetime

# Load current cache
with open('/Users/michaelhammond/Desktop/capitol-watch/bill-analysis.json', 'r') as f:
    cache = json.load(f)

# Add HR 9232 - Van Epps bill about counter-drone authority for critical infrastructure
bill_key = "119/hr/9232"
title = "To grant authority to use counter-unmanned aircraft system technologies to private owners of critical infrastructure facilities"

pros = [
    "Enhances security at critical infrastructure sites", 
    "Provides tools to counter growing drone threats"
]

cons = [
    "Could raise privacy and civil liberties concerns",
    "May create conflicts with aviation regulations"
]

cache[bill_key] = {
    'pros': pros,
    'cons': cons,
    'generated': datetime.now().isoformat(),
    'congress': '119',
    'type': 'hr',
    'number': '9232',
    'title': title
}

# Save updated cache
with open('/Users/michaelhammond/Desktop/capitol-watch/bill-analysis.json', 'w') as f:
    json.dump(cache, f, indent=2)

print(f"Added bill {bill_key}")
print(f"New cache size: {len(cache)}")