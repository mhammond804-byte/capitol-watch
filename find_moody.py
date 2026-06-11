#!/usr/bin/env python3
"""Find Ashley Moody's bioguide ID by checking potential IDs."""
import json, subprocess

# Try various bioguide patterns for Ashley Moody
candidates = ['M001226', 'M001227', 'M001228', 'M001229', 'M001230', 'M001231', 'M001232', 'M001233', 'M001234', 'M001235']

for bid in candidates:
    out = subprocess.run(["curl", "-s", f"https://api.congress.gov/v3/member/{bid}?format=json"], 
                         capture_output=True, text=True, timeout=10)
    try:
        d = json.loads(out.stdout)
        m = d.get('member', {})
        name = m.get('name', 'N/A')
        state = m.get('state', 'N/A')
        if state == 'Florida' or name != 'N/A':
            print(f"{bid}: {name} - {state} - current={m.get('currentMember')}")
    except:
        pass

print("---")
# Also try: search for senators with state=FL and currentMember=true
out = subprocess.run(["curl", "-s", "https://capitolwatch.us/api/state/FL"], capture_output=True, text=True, timeout=10)
d = json.loads(out.stdout)
print(f"FL house: {len(d.get('house',[]))}, senate: {len(d.get('senate',[]))}")

# Maybe the senators are hidden differently. Let me check
# Actually, let me try known bioguide patterns
# Ashley Moody - she was FL AG, let me look her up
# Senator Moody... let me try M000XXX patterns
bid = "M001215"  # Random guess
out = subprocess.run(["curl", "-s", f"https://api.congress.gov/v3/member/{bid}?format=json"], 
                     capture_output=True, text=True, timeout=10)
try:
    d = json.loads(out.stdout)
    m = d.get('member', {})
    print(f"M001215: {m.get('name','N/A')} - {m.get('state','N/A')}")
except:
    print(f"M001215: parse error")
