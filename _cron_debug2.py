"""Check if AR members' bills are actually all in cache, or if member data is empty."""

import json, urllib.request, time, os

cache = json.load(open('bill-analysis.json'))
cached_keys = set(k.lower() for k in cache.keys())

def fetch_json(url):
    req = urllib.request.Request(url)
    req.add_header("User-Agent", "Capitol-Watch/1.0 (research; contact@capitolwatch.us)")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        print(f"  Error: {e}")
        return None

# Check AR - try first 3 members directly
state_data = fetch_json("https://capitolwatch.us/api/state/AR")
if state_data:
    members = state_data.get("house", []) + state_data.get("senate", [])
    print(f"AR members: {len(members)}")
    
    for m in members[:3]:
        bid = m.get("bioguideId", "")
        print(f"\n  Member {bid}: {m.get('firstName','')} {m.get('lastName','')}")
        member_data = fetch_json(f"https://capitolwatch.us/api/member/{bid}")
        if member_data:
            sponsored = member_data.get("sponsored", [])
            print(f"  Sponsored bills: {len(sponsored)}")
            if sponsored:
                # Check first 5
                for bill in sponsored[:5]:
                    congress = bill.get("congress", "")
                    bill_type = bill.get("type", "")
                    number = bill.get("number", "")
                    key = f"{congress}/{bill_type}/{number}".lower()
                    in_cache = "IN CACHE" if key in cached_keys else "NOT cached"
                    print(f"    {key} - {in_cache}")
                    # Count all uncached
                uncached = 0
                for bill in sponsored:
                    congress = bill.get("congress", "")
                    bill_type = bill.get("type", "")
                    number = bill.get("number", "")
                    key = f"{congress}/{bill_type}/{number}".lower()
                    if key not in cached_keys:
                        uncached += 1
                print(f"  Total uncached: {uncached}")
        time.sleep(0.2)
else:
    print("Could not fetch AR state data")
