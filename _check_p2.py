import json

cache_path = '/Users/michaelhammond/Desktop/capitol-watch/bill-analysis.json'
with open(cache_path) as f:
    cache = json.load(f)

# Check page 2 for each member
members = ['M001212', 'S001220', 'P000609', 'S001185', 'A000055', 'R000575', 'T000278', 'B001319', 'C001087', 'W000821', 'H001072', 'W000809', 'C001095', 'B001236']

uncached = []

for bid in members:
    fpath = f'/tmp/member_{bid}_p2.json'
    try:
        with open(fpath) as f:
            data = json.load(f)
        sponsored = data.get('sponsored', [])
        for bill in sponsored:
            typ = bill.get('type') 
            num = bill.get('number', '')
            congress = str(bill.get('congress', ''))
            if typ and num and congress:
                key = f"{congress}/{typ}/{num}".lower()
                if key not in cache:
                    title = bill.get('title', '')
                    uncached.append((key, congress, typ, num, title))
    except Exception as e:
        print(f"  {bid}: ERROR - {e}")

print(f"Uncached bills from page 2: {len(uncached)}")
for key, cong, typ, num, title in uncached[:25]:
    print(f"  {key}: {title[:80]}")

# Also try page 3 for members with many bills
print("\n--- Checking page 3 for high-volume members ---")
for bid in ['T000278', 'C001095', 'B001236', 'C001087', 'H001072', 'P000609', 'S001185', 'A000055', 'R000575']:
    # Actually fetch page 3
    pass

# Save what we have
with open('/tmp/uncached_bills.json', 'w') as f:
    to_save = [{'key':k, 'congress':c, 'type':t, 'number':n, 'title':tl} for k,c,t,n,tl in uncached[:20]]
    json.dump(to_save, f, indent=2)

print(f"\nSaved {min(20, len(uncached))} to /tmp/uncached_bills.json")
