#!/usr/bin/env python3
"""Check if capitolwatch.us has any member endpoint that returns FL senators."""
import json, subprocess

# Let me check if there's a list all members endpoint
urls = [
    "https://capitolwatch.us/api/members",
    "https://capitolwatch.us/api/members?state=FL",
    "https://capitolwatch.us/api/state/FL/senate",
]

for url in urls:
    out = subprocess.run(["curl", "-s", url], capture_output=True, text=True, timeout=10)
    try:
        d = json.loads(out.stdout)
        if isinstance(d, dict):
            print(f"{url}: {list(d.keys())[:5]}")
        elif isinstance(d, list):
            print(f"{url}: list of {len(d)} items")
            if d:
                print(f"  First: {json.dumps(d[0])[:200]}")
        else:
            print(f"{url}: {str(d)[:200]}")
    except:
        print(f"{url}: parse error: {out.stdout[:200]}")
