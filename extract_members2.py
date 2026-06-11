import json

def is_current_member(member):
    """A member is current if their most recent term has no endYear."""
    terms = member.get('terms', {}).get('item', [])
    if not terms:
        return False
    latest = max(terms, key=lambda t: t.get('startYear', 0))
    # Current if no endYear (still serving) OR endYear >= current year and startYear >= 2025
    if 'endYear' not in latest:
        return True
    # Allow recently ended terms that are still in the current congress
    # Actually for house, terms are 2 years. 119th Congress started Jan 2025.
    # If startYear >= 2025 and no endYear, they're current.
    if latest.get('startYear', 0) >= 2025:
        return 'endYear' not in latest
    return False

for state_code in ['AK', 'AL']:
    data = json.load(open(f'/tmp/state_{state_code.lower()}.json'))
    current = []
    for chamber in ['house', 'senate']:
        for m in data.get(chamber, []):
            bid = m['bioguideId']
            name = m['name']
            terms = m.get('terms', {}).get('item', [])
            latest = max(terms, key=lambda t: t.get('startYear', 0))
            if 'endYear' not in latest:
                current.append((chamber, bid, name))
    
    print(f"\n=== {state_code} current members ===")
    for chamber, bid, name in current:
        print(f"  {chamber}: {bid} - {name}")
