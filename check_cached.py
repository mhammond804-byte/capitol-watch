import json
import subprocess

cache = json.load(open('/Users/michaelhammond/Desktop/capitol-watch/bill-analysis.json'))
cache_keys = set(cache.keys())

# Check Moore's bills
result = subprocess.run(['curl', '-s', 'https://capitolwatch.us/api/member/M001212'], capture_output=True, text=True, timeout=15)
d = json.loads(result.stdout)

found = 0
for b in d.get('sponsored', []):
    key = f"{b.get('congress')}/{b.get('type','').lower()}/{b.get('number')}".lower()
    if key in cache_keys:
        found += 1
        print(f"  CACHED: {key} - {b.get('title','')[:60]}")
    else:
        print(f"  UNCACHED: {key} - {b.get('title','')[:60]}")

print(f"\nTotal bills: {len(d.get('sponsored',[]))}")
print(f"Already cached: {found}")
print(f"New: {len(d.get('sponsored',[])) - found}")

# Also check a few from other members
for bid, name in [('S001198','Sullivan'), ('M001153','Murkowski'), ('F000481','Figures'), ('S001220','Strong')]:
    r2 = subprocess.run(['curl', '-s', f'https://capitolwatch.us/api/member/{bid}'], capture_output=True, text=True, timeout=15)
    d2 = json.loads(r2.stdout)
    uncached_count = 0
    for b in d2.get('sponsored', []):
        key = f"{b.get('congress')}/{b.get('type','').lower()}/{b.get('number')}".lower()
        if key not in cache_keys:
            uncached_count += 1
    print(f"{name} ({bid}): {len(d2.get('sponsored',[]))} total, {uncached_count} uncached")
