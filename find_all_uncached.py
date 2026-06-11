import json
import subprocess
import sys

API_KEY = "xH3oHkvJab5BzhnVvJ5zXk3bHK5fPqHZ263Asebc"

# Current members for AK and AL
members = [
    ("AK", "senate", "S001198", "Sullivan, Dan"),
    ("AK", "senate", "M001153", "Murkowski, Lisa"),
    ("AL", "house", "F000481", "Figures, Shomari"),
    ("AL", "house", "M001212", "Moore, Barry"),
    ("AL", "house", "S001220", "Strong, Dale W."),
    ("AL", "house", "P000609", "Palmer, Gary J."),
    ("AL", "house", "S001185", "Sewell, Terri A."),
    ("AL", "house", "R000575", "Rogers, Mike D."),
    ("AL", "house", "A000055", "Aderholt, Robert B."),
    ("AL", "senate", "T000278", "Tuberville, Tommy"),
    ("AL", "senate", "B001319", "Britt, Katie Boyd"),
]

# Load existing cache
cache = json.load(open('/Users/michaelhammond/Desktop/capitol-watch/bill-analysis.json'))
cache_keys = set(cache.keys())
print("Existing cache entries: {}".format(len(cache_keys)))

all_uncached = []

for state, chamber, bioguide_id, name in members:
    offset = 0
    member_uncached = []
    
    # Fetch up to 200 bills per member (enough to find uncached ones)
    while offset < 200 and len(all_uncached) < 30:
        url = "https://api.congress.gov/v3/member/{}/sponsored-legislation?offset={}&limit=50&format=json".format(bioguide_id, offset)
        result = subprocess.run(['curl', '-s', url, '-H', 'X-Api-Key: {}'.format(API_KEY)], capture_output=True, text=True, timeout=15)
        
        try:
            d = json.loads(result.stdout)
        except:
            print("  Error parsing JSON for {} offset {}".format(bioguide_id, offset))
            break
        
        bills = d.get('sponsoredLegislation', [])
        if not bills:
            break
        
        for item in bills:
            congress = item.get('congress')
            bill_type = item.get('type')
            number = item.get('number')
            
            # Skip amendments (no type)
            if not bill_type or not number:
                continue
            
            try:
                c = int(congress)
                if c < 118:
                    continue
            except (ValueError, TypeError):
                continue
            
            key = "{}/{}".format(congress, bill_type.lower()) + "/" + str(number).lower()
            
            if key not in cache_keys:
                title = item.get('title', 'No title') or 'No title'
                all_uncached.append({
                    'key': key,
                    'congress': str(congress),
                    'type': bill_type.lower(),
                    'number': str(number),
                    'title': title,
                    'member': name,
                    'state': state,
                })
                member_uncached.append(key)
        
        # Check if we need more pages
        pagination = d.get('pagination', {})
        count = pagination.get('count', 0)
        next_url = pagination.get('next', '')
        
        print("  {} {} offset={}: {} bills fetched, {} new uncached (total so far: {})".format(
            state, name, offset, len(bills), len(member_uncached), len(all_uncached)))
        
        if not next_url:
            break
        
        offset += 50
    
    print("{} {}: {} total uncached found".format(state, name, len(member_uncached)))

print("\n\nTotal uncached bills found: {}".format(len(all_uncached)))
with open('/tmp/uncached_bills.json', 'w') as f:
    json.dump(all_uncached, f, indent=2)
print("Saved to /tmp/uncached_bills.json")
