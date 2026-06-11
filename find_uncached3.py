import json
import subprocess

cache = json.load(open('/Users/michaelhammond/Desktop/capitol-watch/bill-analysis.json'))
cache_keys = set(cache.keys())

# Check all members for uncached bills
members = [
    ("AK", "S001198", "Sullivan, Dan"),
    ("AK", "M001153", "Murkowski, Lisa"),
    ("AL", "F000481", "Figures, Shomari"),
    ("AL", "M001212", "Moore, Barry"),
    ("AL", "S001220", "Strong, Dale W."),
    ("AL", "P000609", "Palmer, Gary J."),
    ("AL", "S001185", "Sewell, Terri A."),
    ("AL", "R000575", "Rogers, Mike D."),
    ("AL", "A000055", "Aderholt, Robert B."),
    ("AL", "T000278", "Tuberville, Tommy"),
    ("AL", "B001319", "Britt, Katie Boyd"),
]

total_uncached = []
for state, bid, name in members:
    result = subprocess.run(['curl', '-s', f'https://capitolwatch.us/api/member/{bid}'], capture_output=True, text=True, timeout=15)
    d = json.loads(result.stdout)
    sponsored = d.get('sponsored', [])
    
    uncached = []
    for b in sponsored:
        congress = b.get('congress', '')
        bill_type = b.get('type', '')
        number = b.get('number', '')
        
        if not all([congress, bill_type, number]):
            continue
        if bill_type is None:
            continue
        
        try:
            c = int(congress)
            if c < 118 or c > 120:
                continue
        except ValueError:
            continue
        
        key = f"{congress}/{bill_type.lower()}/{number}".lower()
        if key not in cache_keys:
            title = b.get('title', 'No title') or 'No title'
            uncached.append({
                'key': key,
                'congress': congress,
                'type': bill_type.lower(),
                'number': number,
                'title': title,
                'member': name,
                'state': state,
            })
    
    total_uncached.extend(uncached)
    print(f"{state} {name} ({bid}): {len(sponsored)} total, {len(uncached)} uncached")
    for b in uncached[:3]:
        print(f"  {b['key']} - {b['title'][:80]}")

print(f"\n\nTotal uncached bills across all members: {len(total_uncached)}")

# Save
with open('/tmp/uncached_bills.json', 'w') as f:
    json.dump(total_uncached, f, indent=2)
print(f"Saved to /tmp/uncached_bills.json")
