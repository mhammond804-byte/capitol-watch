import json, sys, urllib.request, urllib.error

def fetch_json(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'CapitolWatch/1.0'})
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read())
    except Exception as e:
        print(f"  ERROR fetching {url}: {e}", file=sys.stderr)
        return None

# Load existing cache
with open('/Users/michaelhammond/Desktop/capitol-watch/bill-analysis.json') as f:
    cache = json.load(f)

def cache_key(congress, bill_type, number):
    return f"{congress}/{bill_type}/{number}".lower()

# Get uncached bills
all_bills = []
seen_keys = set()

for state, txtfile in [('MI', '/tmp/mi_bioguides.txt'), ('MN', '/tmp/mn_bioguides.txt')]:
    bioguides = [l.strip() for l in open(txtfile).readlines() if l.strip()]
    print(f"\n=== FETCHING {state} MEMBER BILLS ===")
    for bid in bioguides:
        print(f"  Member: {bid}")
        data = fetch_json(f"https://capitolwatch.us/api/member/{bid}")
        if not data:
            continue
        # sponsored is a top-level array in the response
        sponsored = data.get('sponsored', [])
        print(f"    Sponsored bills: {len(sponsored)}")
        for bill in sponsored:
            congress = bill.get('congress')
            bill_type = bill.get('type')
            number = bill.get('number')
            title = bill.get('title', '')
            if congress and bill_type and number:
                key = cache_key(congress, bill_type, number)
                if key not in cache and key not in seen_keys:
                    seen_keys.add(key)
                    all_bills.append({
                        'congress': congress,
                        'type': bill_type,
                        'number': number,
                        'title': title,
                        'state': state,
                        'key': key
                    })
                    if len(all_bills) >= 200:
                        break
        if len(all_bills) >= 200:
            break
    if len(all_bills) >= 200:
        break

print(f"\n=== TOTAL UNIQUE UNCACHED BILLS: {len(all_bills)} ===")
with open('/tmp/uncached_bills.json', 'w') as f:
    json.dump(all_bills[:100], f, indent=2)
