import json

with open('/Users/michaelhammond/Desktop/capitol-watch/bill-analysis.json') as f:
    cache = json.load(f)

print(f"119/s/4692 in cache: {'119/s/4692' in cache}")
print(f"119/s/4673 in cache: {'119/s/4673' in cache}")

# Which members sponsored these?
members = ['T000278', 'B001319', 'C001095', 'B001236']
for bid in members:
    # page 1
    with open(f'/tmp/member_{bid}.json') as f:
        data = json.load(f)
    for b in data.get('sponsored', []):
        typ = b.get('type', '') or ''
        num = b.get('number', '') or ''
        cong = str(b.get('congress', ''))
        key = f"{cong}/{typ}/{num}".lower()
        if key in ['119/s/4692', '119/s/4673']:
            print(f"{key} by {bid}: {b.get('title','')[:100]}")
    # page 2
    try:
        with open(f'/tmp/member_{bid}_p2.json') as f:
            data2 = json.load(f)
        for b in data2.get('sponsored', []):
            typ = b.get('type', '') or ''
            num = b.get('number', '') or ''
            cong = str(b.get('congress', ''))
            key = f"{cong}/{typ}/{num}".lower()
            if key in ['119/s/4692', '119/s/4673']:
                print(f"{key} (p2) by {bid}: {b.get('title','')[:100]}")
    except:
        pass

# Also check if these are in member_cache for these members
# Let's look up who the bills actually belong to
print("\n--- Checking all members ---")
for bid in ['T000278', 'B001319', 'C001095', 'B001236']:
    total_count = 0
    for fname in [f'/tmp/member_{bid}.json', f'/tmp/member_{bid}_p2.json']:
        try:
            with open(fname) as f:
                data = json.load(f)
            total_count += len(data.get('sponsored', []))
        except:
            pass
    print(f"  {bid}: {total_count} total bills examined")
