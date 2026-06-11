import json

for state_code in ['AK', 'AL']:
    data = json.load(open(f'/tmp/state_{state_code.lower()}.json'))
    print(f"\n=== {state_code} senate ===")
    for m in data.get('senate', []):
        terms = m.get('terms', {}).get('item', [])
        print(f"  {m['bioguideId']} - {m['name']}")
        for t in terms:
            print(f"    term: {t}")
