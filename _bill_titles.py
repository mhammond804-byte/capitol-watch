import json

# Try getting bill details endpoint instead
for fname, label, bill in [
    ('/tmp/member_T000278.json', '119/s/4692', '4692'),
    ('/tmp/member_B001319.json', '119/s/4673', '4673')
]:
    # Find the bill in the member data
    with open(fname) as f:
        data = json.load(f)
    for b in data.get('sponsored', []):
        if b.get('number') == bill and b.get('type', '').lower() == 's':
            print(f"=== {label} ===")
            print(f"Title: {b.get('title', 'N/A')}")
            print(f"Congress: {b.get('congress', 'N/A')}")
            print(f"Introduced: {b.get('introducedDate', 'N/A')}")
            la = b.get('latestAction', {})
            if la:
                print(f"Latest action: {la.get('text', 'N/A')} ({la.get('actionDate', 'N/A')})")
            pa = b.get('policyArea', {})
            if pa:
                print(f"Policy area: {pa.get('name', 'N/A')}")
            print()
