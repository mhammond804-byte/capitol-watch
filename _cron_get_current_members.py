#!/usr/bin/env python3
"""Get current members for MI and MN from capitolwatch.us"""
import json, subprocess

def get_state_members(state):
    result = subprocess.run(
        ["curl", "-s", f"https://capitolwatch.us/api/state/{state}"],
        capture_output=True, text=True, timeout=30
    )
    data = json.loads(result.stdout)
    
    # Get members from both house and senate
    members = []
    for chamber in ['house', 'senate']:
        for m in data.get(chamber, []):
            terms = m.get('terms', {}).get('item', [])
            if terms:
                latest_term = terms[-1]
                if 'endYear' not in latest_term:
                    members.append(m['bioguideId'])
    return members

mi_members = get_state_members("MI")
mn_members = get_state_members("MN")
print(f"MI current members ({len(mi_members)}): {json.dumps(mi_members)}")
print(f"MN current members ({len(mn_members)}): {json.dumps(mn_members)}")
