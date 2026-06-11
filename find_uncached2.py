import json
import subprocess
import os

API_KEY = "xH3oHkvJab5BzhnVvJ5zXk3bHK5fPqHZ263Asebc"

members = {
    "AK": [
        ("senate", "S001198", "Sullivan, Dan"),
        ("senate", "M001153", "Murkowski, Lisa"),
    ],
    "AL": [
        ("house", "F000481", "Figures, Shomari"),
        ("house", "M001212", "Moore, Barry"),
        ("house", "S001220", "Strong, Dale W."),
        ("house", "P000609", "Palmer, Gary J."),
        ("house", "S001185", "Sewell, Terri A."),
        ("house", "R000575", "Rogers, Mike D."),
        ("house", "A000055", "Aderholt, Robert B."),
        ("senate", "T000278", "Tuberville, Tommy"),
        ("senate", "B001319", "Britt, Katie Boyd"),
    ]
}

# Load existing cache
cache = json.load(open('/Users/michaelhammond/Desktop/capitol-watch/bill-analysis.json'))
existing_keys = set(cache.keys())
print(f"Existing cache: {len(existing_keys)} entries")

uncached = []

for state, member_list in members.items():
    for chamber, bioguide_id, name in member_list:
        url = f"https://capitolwatch.us/api/member/{bioguide_id}"
        result = subprocess.run(['curl', '-s', url], capture_output=True, text=True, timeout=30)
        if result.returncode != 0 or not result.stdout:
            print(f"  Failed: {bioguide_id} ({name})")
            continue
        
        try:
            data = json.loads(result.stdout)
        except json.JSONDecodeError:
            print(f"  Invalid JSON: {bioguide_id}")
            continue
        
        sponsored = data.get('sponsored', [])
        print(f"\n{state} {chamber} {name} ({bioguide_id}): {len(sponsored)} sponsored bills")
        
        for bill in sponsored:
            congress = bill.get('congress', '')
            bill_type = bill.get('type', '')
            number = bill.get('number', '')
            
            if not all([congress, bill_type, number]):
                continue
            
            try:
                c = int(congress)
                if c < 118 or c > 120:
                    continue
            except ValueError:
                continue
            
            key = f"{congress}/{bill_type.lower()}/{number}".lower()
            if key in existing_keys:
                continue
            
            title = bill.get('title', 'No title')
            uncached.append({
                'key': key,
                'congress': congress,
                'type': bill_type.lower(),
                'number': number,
                'title': title,
                'member': name,
                'state': state,
            })
            print(f"  NEW: {key} - {title[:80]}")

print(f"\n\nTotal uncached bills: {len(uncached)}")

# Save for next step
with open('/tmp/uncached_bills.json', 'w') as f:
    json.dump(uncached, f, indent=2)

if uncached:
    print(f"\nSaving {len(uncached)} uncached bills to /tmp/uncached_bills.json")
    for b in uncached[:5]:
        print(f"  {b['key']} - {b['title'][:60]}")
