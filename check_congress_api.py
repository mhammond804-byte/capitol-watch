import json
import subprocess

cache = json.load(open('/Users/michaelhammond/Desktop/capitol-watch/bill-analysis.json'))
cache_keys = set(cache.keys())

# Check the congress.gov API results for uncached bills from Sullivan
result = subprocess.run(['curl', '-s', 'https://api.congress.gov/v3/member/S001198/sponsored-legislation?limit=50&format=json', '-H', 'X-Api-Key: xH3oHkvJab5BzhnVvJ5zXk3bHK5fPqHZ263Asebc'], capture_output=True, text=True, timeout=15)
d = json.loads(result.stdout)
bills = d.get('sponsoredLegislation', [])
uncached = []
for item in bills:
    congress = item.get('congress')
    bill_type = item.get('type')
    number = item.get('number')
    if not all([congress, bill_type, number]):
        continue
    key = "{}/{}".format(congress, bill_type.lower()) + "/" + str(number).lower()
    if key not in cache_keys:
        uncached.append(key)
        print("  UNCACHED: {} - {}".format(key, item.get('title','')[:80]))
        
print("\nSullivan: {} items from congress.gov, {} uncached (first 50)".format(len(bills), len(uncached)))

# Try to get more pages to find 20 uncached
for offset in [50, 100]:
    url = 'https://api.congress.gov/v3/member/S001198/sponsored-legislation?offset={}&limit=50&format=json'.format(offset)
    result = subprocess.run(['curl', '-s', url, '-H', 'X-Api-Key: xH3oHkvJab5BzhnVvJ5zXk3bHK5fPqHZ263Asebc'], capture_output=True, text=True, timeout=15)
    d = json.loads(result.stdout)
    bills = d.get('sponsoredLegislation', [])
    c = 0
    for item in bills:
        congress = item.get('congress')
        bill_type = item.get('type')
        number = item.get('number')
        if not all([congress, bill_type, number]):
            continue
        key = "{}/{}".format(congress, bill_type.lower()) + "/" + str(number).lower()
        if key not in cache_keys:
            c += 1
            uncached.append(key)
            print("  UNCACHED offset={}: {} - {}".format(offset, key, item.get('title','')[:80]))
    print("  Offset {}: {} items, {} uncached".format(offset, len(bills), c))

print("\nTotal uncached for Sullivan: {}".format(len(uncached)))
