import json, sys, subprocess, urllib.request

def get_state_members(state_code):
    url = f"https://capitolwatch.us/api/state/{state_code}"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read())
    
    members = []
    
    # House members
    for m in data.get('house', []):
        terms = m['terms']['item']
        # Current member = most recent term doesn't have endYear
        # or has startYear >= 2025 and no endYear
        latest_term = max(terms, key=lambda t: t.get('startYear', 0))
        if not latest_term.get('endYear'):
            members.append(m['bioguideId'])
    
    # Senate members
    for m in data.get('senate', []):
        terms = m['terms']['item']
        latest_term = max(terms, key=lambda t: t.get('startYear', 0))
        if not latest_term.get('endYear'):
            members.append(m['bioguideId'])
    
    return sorted(set(members))

if len(sys.argv) > 1:
    state = sys.argv[1]
    members = get_state_members(state)
    print(json.dumps(members))
else:
    # Get both NY and OH
    for s in ['NY', 'OH']:
        print(f"{s}: {json.dumps(get_state_members(s))}")
