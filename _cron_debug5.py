"""Find actual uncached bills by checking the response from the earlier working approach."""

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

# Let me check: the debug2 script looked at member individually with curl
# Let me look at the raw response for W000821 more carefully
member_data = fetch_json("https://capitolwatch.us/api/member/W000821")
sponsored = member_data.get("sponsored", [])
print(f"W000821 sponsored count: {len(sponsored)}")
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
            print(f"  Uncached: {key} - {bill.get('title','')[:80]}")
            uncached += 1
    else:
        if not has_number:
            print(f"  No number: congress={congress}, type='{bill_type}', amendmentNumber={bill.get('amendmentNumber','')}")
print(f"Total uncached (real bills): {uncached}")

# Check the /api/member endpoint response structure
print(f"\nMember data top keys: {list(member_data.keys())}")
print(f"'sponsored' is {type(sponsored).__name__}")

# Check what the full bill list contains - is there a limit?
# Check if the "member" object has more bills
member_obj = member_data.get("member", {})
print(f"member object keys: {list(member_obj.keys())}")
