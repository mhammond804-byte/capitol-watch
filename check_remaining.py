import json
import subprocess

API_KEY = "xH3oHkvJab5BzhnVvJ5zXk3bHK5fPqHZ263Asebc"

members = [
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

cache = json.load(open('/Users/michaelhammond/Desktop/capitol-watch/bill-analysis.json'))
cache_keys = set(cache.keys())

for state, bid, name in members:
    offset = 0
    uncounted = 0
    while offset < 200 and uncounted < 20:
        url = "https://api.congress.gov/v3/member/{}/sponsored-legislation?offset={}&limit=50&format=json".format(bid, offset)
        result = subprocess.run(['curl', '-s', url, '-H', 'X-Api-Key: {}'.format(API_KEY)], capture_output=True, text=True, timeout=15)
        try:
            d = json.loads(result.stdout)
        except:
            print("  {}: JSON parse error offset {}".format(name, offset))
            break
        
        bills = d.get('sponsoredLegislation', [])
        if not bills:
            break
        
        for item in bills:
            congress = item.get('congress')
            bill_type = item.get('type')
            number = item.get('number')
            if not bill_type or not number:
                continue
            try:
                c = int(congress) if congress else 0
                if c < 118:
                    continue
            except (ValueError, TypeError):
                continue
            
            key = "{}/{}".format(congress, bill_type.lower()) + "/" + str(number).lower()
            if key not in cache_keys:
                uncounted += 1
        
        pagination = d.get('pagination', {})
        next_url = pagination.get('next', '')
        if not next_url:
            break
        offset += 50
    
    print("{} ({}) - {} uncached found in first 200".format(name, bid, uncounted))
