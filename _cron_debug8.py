"""Comprehensive check of uncached bills with pagination for AR + CA."""

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
        return None

def get_members(state_code):
    data = fetch_json(f"https://capitolwatch.us/api/state/{state_code}")
    if not data:
        return []
    members = []
    for chamber in ["house", "senate"]:
        members.extend(data.get(chamber, []))
    return members

def count_uncached(bioguide, max_offsets=3):
    total = 0
    uncached_keys = []
    for offset in [0, 20, 40]:
        member_data = fetch_json(f"https://capitolwatch.us/api/member/{bioguide}?offset={offset}")
        if not member_data:
            break
        sponsored = member_data.get("sponsored", [])
        if not sponsored:
            break
        for bill in sponsored:
            congress = bill.get("congress", "")
            bill_type = bill.get("type", "")
            number = bill.get("number", "")
            has_number = number and number.strip()
            has_type = bill_type and bill_type.strip() and bill_type != "None"
            if congress and has_type and has_number:
                key = f"{congress}/{bill_type}/{number}".lower()
                if key not in cached_keys:
                    total += 1
                    uncached_keys.append(key)
        time.sleep(0.1)
    return total, uncached_keys

# Check AR
members = get_members("AR")
print(f"AR: {len(members)} members")
ar_total = 0
for m in members:
    if isinstance(m, dict):
        bid = m.get("bioguideId", "")
        label = m.get("name", {}).get("last", bid) if isinstance(m.get("name"), dict) else bid
    else:
        bid = m
        label = m
    cnt, keys = count_uncached(bid)
    if cnt:
        print(f"  {label}: {cnt} uncached - {keys}")
    else:
        print(f"  {label}: 0 uncached")
    ar_total += cnt
print(f"AR total uncached: {ar_total}")

# Check CA first 5
if ar_total == 0:
    members2 = get_members("CA")
    print(f"\nCA: checking first 5 members")
    ca_total = 0
    for m in members2[:5]:
        if isinstance(m, dict):
            bid = m.get("bioguideId", "")
            label = m.get("name", {}).get("last", bid) if isinstance(m.get("name"), dict) else bid
        else:
            bid = m
            label = m
        cnt, keys = count_uncached(bid)
        if cnt:
            print(f"  {label}: {cnt} uncached - {keys}")
        else:
            print(f"  {label}: 0 uncached")
        ca_total += cnt
    print(f"CA first 5 total uncached: {ca_total}")
