"""Find exactly which bills are uncached for AR members using the member API."""

import json, urllib.request, time

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

state_data = fetch_json("https://capitolwatch.us/api/state/AR")
members = state_data.get("house", []) + state_data.get("senate", [])
total_uncached = 0
uncached_bills = []

for member in members:
    bid = member.get("bioguideId", "")
    member_data = fetch_json(f"https://capitolwatch.us/api/member/{bid}")
    if member_data:
        sponsored = member_data.get("sponsored", [])
        for bill in sponsored:
            congress = bill.get("congress", "")
            bill_type = bill.get("type", "")
            number = bill.get("number", "")
            if congress and bill_type and number:
                key = f"{congress}/{bill_type}/{number}".lower()
                if key not in cached_keys:
                    print(f"UNCACHED: {key} ({bill.get('title','')[:80]})")
                    total_uncached += 1
                    uncached_bills.append((key, bill.get('title','')))
            elif congress and not bill_type:
                # Missing type - problematic
                print(f"  SKIP: congress={congress}, type='{bill_type}', number='{number}' - {bill.get('title','')[:60]}")
            else:
                print(f"  SKIP: congress='{congress}', type='{bill_type}', number='{number}' - {bill.get('title','')[:60]}")
        time.sleep(0.2)

print(f"\nTotal uncached: {total_uncached}")

# Now check W000821 specifically with the raw curl API to verify
print("\n--- Checking with different field name mappings ---")
member_data2 = fetch_json("https://capitolwatch.us/api/member/W000821")
for bill in member_data2.get("sponsored", []):
    # Try all possible field name variants
    congress = bill.get("congress", "")
    bill_type = bill.get("type", "")
    number = bill.get("number", "")
    key = f"{congress}/{bill_type}/{number}".lower()
    if key not in cached_keys:
        print(f"  bill keys: {list(bill.keys())}")
        print(f"  congress='{congress}', type='{bill_type}', number='{number}'")
        print(f"  key='{key}' in cache? {key in cached_keys}")
        break
