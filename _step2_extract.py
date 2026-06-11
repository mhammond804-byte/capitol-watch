import json

cache_path = '/Users/michaelhammond/Desktop/capitol-watch/bill-analysis.json'
with open(cache_path) as f:
    cache = json.load(f)

print(f"Existing cache: {len(cache)} entries")

# All members
members = {
    'F000481': 'Figures, Shomari (AL)',
    'M001212': 'Moore, Barry (AL)',
    'S001220': 'Strong, Dale W. (AL)',
    'P000609': 'Palmer, Gary J. (AL)',
    'S001185': 'Sewell, Terri A. (AL)',
    'A000055': 'Aderholt, Robert B. (AL)',
    'R000575': 'Rogers, Mike D. (AL)',
    'T000278': 'Tuberville, Tommy (AL Senate)',
    'B001319': 'Britt, Katie Boyd (AL Senate)',
    'C001087': 'Crawford, Rick (AR)',
    'W000821': 'Westerman, Bruce (AR)',
    'H001072': 'Hill, French (AR)',
    'W000809': 'Womack, Steve (AR)',
    'C001095': 'Cotton, Tom (AR Senate)',
    'B001236': 'Boozman, John (AR Senate)',
}

bills_to_check = []

for bid, name in members.items():
    fpath = f'/tmp/member_{bid}.json'
    try:
        with open(fpath) as f:
            data = json.load(f)
        sponsored = data.get('sponsoredLegislation', {}).get('item', [])
        print(f"  {name} ({bid}): {len(sponsored)} sponsored bills")
        for bill in sponsored:
            typ = bill.get('type', '').lower()
            num = bill.get('number', '')
            congress = str(bill.get('congress', ''))
            if typ and num and congress:
                key = f"{congress}/{typ}/{num}".lower()
                bills_to_check.append((key, congress, typ, num))
    except Exception as e:
        print(f"  {name} ({bid}): ERROR - {e}")

print(f"\nTotal bills found: {len(bills_to_check)}")

# Find uncached bills
uncached = []
for key, cong, typ, num in bills_to_check:
    if key not in cache:
        uncached.append((key, cong, typ, num))

print(f"Uncached bills: {len(uncached)}")
for key, cong, typ, num in uncached[:25]:
    print(f"  {key}")

# Save for next step
with open('/tmp/uncached_bills.json', 'w') as f:
    json.dump(uncached[:20], f)

print(f"\nSaved top {min(20, len(uncached))} uncached bills to /tmp/uncached_bills.json")
