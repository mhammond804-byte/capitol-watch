import json

# Check how many sponsored bills each member actually has
members = ['F000481', 'M001212', 'S001220', 'P000609', 'S001185', 'A000055', 'R000575', 'T000278', 'B001319', 'C001087', 'W000821', 'H001072', 'W000809', 'C001095', 'B001236']

for bid in members:
    with open(f'/tmp/member_{bid}.json') as f:
        data = json.load(f)
    member = data.get('member', {})
    sl = member.get('sponsoredLegislation', {})
    count = sl.get('count', 'N/A')
    url = sl.get('url', 'N/A')
    sponsored = data.get('sponsored', [])
    print(f"{bid}: {len(sponsored)} returned (first page), total count={count}")
    # Check if there's pagination info
    for bill in sponsored:
        if bill.get('type') is None:
            print(f"  Bill w/ None type: {bill}")
