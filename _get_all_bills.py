#!/usr/bin/env python3
"""Get all sponsored bills for AR and AL members."""
import json, subprocess, sys

members = {
    "AL": ["F000481","M001212","S001220","P000609","S001185","R000575","A000055","T000278","B001319"],
    "AR": ["W000821","H001072","W000809","C001087","C001095","B001236"]
}

all_bills = {}
all_keys = set()

for state, ids in members.items():
    state_bills = []
    for mid in ids:
        r = subprocess.run(["curl", "-s", "--max-time", "15", f"https://capitolwatch.us/api/member/{mid}"],
                           capture_output=True, text=True)
        d = json.loads(r.stdout)
        sponsored = d.get("sponsored", [])
        state_bills.extend(sponsored)
    
    # Deduplicate by key
    seen = set()
    unique = []
    for b in state_bills:
        c = b.get("congress")
        t_raw = b.get("type")
        n = b.get("number")
        if c is None or t_raw is None or n is None:
            continue
        t = str(t_raw).lower()
        n_str = str(n).lower()
        key = f"{c}/{t}/{n_str}".lower()
        if key not in seen:
            seen.add(key)
            unique.append(b)
    
    all_bills[state] = unique
    all_keys.update(seen)
    print(f"{state}: {len(sponsored)} raw -> {len(unique)} unique bills")

# Write keys to file for next step
with open("/Users/michaelhammond/Desktop/capitol-watch/_bill_keys.json", "w") as f:
    json.dump({"AR": [f"{b['congress']}/{str(b['type']).lower()}/{str(b['number']).lower()}" for b in all_bills["AR"]],
               "AL": [f"{b['congress']}/{str(b['type']).lower()}/{str(b['number']).lower()}" for b in all_bills["AL"]]}, f)

print(f"\nTotal unique keys: {len(all_keys)}")
