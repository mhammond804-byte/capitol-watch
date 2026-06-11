"""Check if offset=20 bills are uncached."""

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

# Check offset=20 for W000821
member_data = fetch_json("https://capitolwatch.us/api/member/W000821?offset=20")
sponsored = member_data.get("sponsored", [])
print(f"W000821 offset=20: {len(sponsored)} bills")
uncached = 0
for bill in sponsored:
    congress = bill.get("congress", "")
    bill_type = bill.get("type", "")
    number = bill.get("number", "")
    has_number = number and number.strip()
    has_type = bill_type and bill_type.strip() and bill_type != "None"
    if congress and has_type and has_number:
        key = f"{congress}/{bill_type}/{number}".lower()
        if key not in cached_keys:
            print(f"  UNCACHED: {key} - {bill.get('title','')[:80]}")
            uncached += 1
    else:
        if not has_number:
            pass
print(f"  Uncached: {uncached}")

# Now check offset=40
member_data2 = fetch_json("https://capitolwatch.us/api/member/W000821?offset=40")
sponsored2 = member_data2.get("sponsored", [])
print(f"\nW000821 offset=40: {len(sponsored2)} bills")
uncached2 = 0
for bill in sponsored2:
    congress = bill.get("congress", "")
    bill_type = bill.get("type", "")
    number = bill.get("number", "")
    has_number = number and number.strip()
    has_type = bill_type and bill_type.strip() and bill_type != "None"
    if congress and has_type and has_number:
        key = f"{congress}/{bill_type}/{number}".lower()
        if key not in cached_keys:
            print(f"  UNCACHED: {key} - {bill.get('title','')[:80]}")
            uncached2 += 1
time.sleep(0.2)

# Check offset=60
member_data3 = fetch_json("https://capitolwatch.us/api/member/W000821?offset=60")
sponsored3 = member_data3.get("sponsored", [])
print(f"\nW000821 offset=60: {len(sponsored3)} bills")
uncached3 = 0
for bill in sponsored3:
    congress = bill.get("congress", "")
    bill_type = bill.get("type", "")
    number = bill.get("number", "")
    has_number = number and number.strip()
    has_type = bill_type and bill_type.strip() and bill_type != "None"
    if congress and has_type and has_number:
        key = f"{congress}/{bill_type}/{number}".lower()
        if key not in cached_keys:
            print(f"  UNCACHED: {key} - {bill.get('title','')[:80]}")
            uncached3 += 1
