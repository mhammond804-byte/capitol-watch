#!/usr/bin/env python3
"""Find FL senators by scanning API for Florida senators."""
import json, subprocess

# Rick Scott is S001217, confirmed current FL senator
# Florida's other senator currently is Ashley Moody (appointed Jan 2025)

# Let me try searching the capitolwatch.us member search or try known patterns
# Let's try: A000000 pattern - Ashley might start with A
for prefix in ['M000', 'A000']:
    for num in range(300, 400):
        bid = f"{prefix}{num}"
        url = f"https://api.congress.gov/v3/member/{bid}?format=json"
        out = subprocess.run(["curl", "-s", url], capture_output=True, text=True, timeout=5)
        try:
            d = json.loads(out.stdout)
            m = d.get('member', {})
            if m.get('state') == 'Florida' and m.get('currentMember') == True:
                print(f"FOUND: {bid} - {m.get('name','N/A')} - {m.get('state','N/A')} - chamber={m.get('terms',[{}])[0].get('chamber')}")
        except:
            pass

print("Done scanning")
