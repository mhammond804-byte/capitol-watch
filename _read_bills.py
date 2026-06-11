import json

for num in ['4692', '4673']:
    with open(f'/tmp/bill_119_s_{num}.json') as f:
        data = json.load(f)
    bill = data.get('bill', {})
    print(f"=== 119/s/{num} ===")
    print(f"Title: {bill.get('title', 'N/A')}")
    
    summaries = bill.get('summaries', {})
    if isinstance(summaries, dict):
        count = summaries.get('count', 0)
        items = summaries.get('item', [])
        print(f"Summary count: {count}")
        if items:
            for item in items:
                print(f"  Text: {item.get('text','')[:300]}")
                print(f"  Action: {item.get('actionType','')}")
        else:
            print("  No summary items available")
    
    subjects = bill.get('subjects', {})
    if isinstance(subjects, dict):
        bc = subjects.get('billSubjects', {})
        if isinstance(bc, dict):
            lc = bc.get('legislativeSubjects', [])
            print(f"  Subjects: {[s.get('name','') for s in lc[:5]]}")
    
    pa = bill.get('policyArea', {})
    if isinstance(pa, dict):
        print(f"  Policy area: {pa.get('name', 'N/A')}")
    
    print(f"  Introduced: {bill.get('introducedDate','')}")
    la = bill.get('latestAction', {})
    if la:
        print(f"  Latest action: {la.get('text','')}")
    
    # Also check cboCostEstimates
    cbo = bill.get('cboCostEstimates', [])
    print(f"  CBO estimates: {len(cbo)}")
    
    print()
