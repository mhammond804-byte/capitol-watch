"""Check API pagination for member sponsored bills."""

import json, urllib.request

def fetch_json(url):
    req = urllib.request.Request(url)
    req.add_header("User-Agent", "Capitol-Watch/1.0 (research; contact@capitolwatch.us)")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        print(f"  Error: {e}")
        return None

# Check with limit parameter  
member_data = fetch_json("https://capitolwatch.us/api/member/W000821?limit=100")
if member_data:
    sponsored = member_data.get("sponsored", [])
    print(f"With ?limit=100: {len(sponsored)} sponsored")
    
# Check total count from the member object
try:
    member_obj = member_data.get("member", {})
    sl = member_obj.get("sponsoredLegislation", {})
    print(f"sponsoredLegislation object: {type(sl).__name__}")
    if isinstance(sl, dict):
        print(f"  Keys: {list(sl.keys())}")
        print(f"  totalCount: {sl.get('totalCount', 'N/A')}")
except:
    pass

# Try with offset
member_data2 = fetch_json("https://capitolwatch.us/api/member/W000821?offset=20")
if member_data2:
    sponsored2 = member_data2.get("sponsored", [])
    print(f"With offset=20: {len(sponsored2)} sponsored")
