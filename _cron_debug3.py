"""Debug why _cron_pros_cons.py finds 0 uncached."""

import json, urllib.request, time

cache = json.load(open('bill-analysis.json'))

def fetch_json(url):
    req = urllib.request.Request(url)
    req.add_header("User-Agent", "Capitol-Watch/1.0 (research; contact@capitolwatch.us)")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        print(f"  Error: {e}")
        return None

# Simulate exactly what _cron_pros_cons does
state_code = "AR"
state_url = f"https://capitolwatch.us/api/state/{state_code}"
state_data = fetch_json(state_url)
if state_data:
    members = []
    for chamber in ["house", "senate"]:
        members.extend(state_data.get(chamber, []))
    print(f"Total members: {len(members)}")
    
    for member in members[:3]:
        bioguide = member.get("bioguideId", "")
        print(f"\nMember bioguideId: {bioguide}")
        print(f"Member keys: {list(member.keys())}")
        
        member_url = f"https://capitolwatch.us/api/member/{bioguide}"
        member_data = fetch_json(member_url)
        if member_data:
            print(f"Member data keys: {list(member_data.keys())}")
            sponsored = member_data.get("sponsored", [])
            # Try alternates
            sponsored2 = member_data.get("bills", []) or member_data.get("legislation", []) or []
            print(f"  sponsored: {len(sponsored)}")
            print(f"  bills: {len(member_data.get('bills', []))}")
            print(f"  legislation: {len(member_data.get('legislation', []))}")
            print(f"  sponsored (alt): {len(sponsored2)}")
            
            # Check bill object structure
            if sponsored:
                bill = sponsored[0]
                print(f"  First bill keys: {list(bill.keys())}")
                print(f"  congress: '{bill.get('congress', '')}'")
                print(f"  type: '{bill.get('type', '')}'")
                print(f"  number: '{bill.get('number', '')}'")
        time.sleep(0.2)
