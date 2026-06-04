#!/usr/bin/env python3
"""Fetch states, pick 2-3 to process, list their members and sponsored bills."""
import json, sys, os, time, urllib.request, urllib.error
from urllib.request import urlopen

STATES_FILE = "/tmp/states.json"
BILL_CACHE_FILE = os.path.expanduser("~/Desktop/capitol-watch/bill-analysis.json")
OUTPUT_DIR = "/tmp/cw_members"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 1. Load states
with open(STATES_FILE) as f:
    states_data = json.load(f)

# The API returns a list of state codes
if isinstance(states_data, list):
    state_codes = [s.upper() if isinstance(s, str) else s.get('code','') for s in states_data if isinstance(s, str)]
elif isinstance(states_data, dict):
    # Could be {code: name} or {code: {...}}
    state_codes = [k for k in states_data.keys() if len(k) == 2]
else:
    state_codes = []

state_codes = [s for s in state_codes if s and len(s) == 2]
print(f"Found {len(state_codes)} states: {', '.join(sorted(state_codes)[:10])}...")

# 2. Read existing bill cache
with open(BILL_CACHE_FILE) as f:
    bill_cache = json.load(f)
print(f"Existing bills in cache: {len(bill_cache)}")

# 3. Load existing member state tracking so we don't re-process states
MEMBER_TRACK_FILE = "/tmp/cw_processed_states.json"
processed_states = set()
if os.path.exists(MEMBER_TRACK_FILE):
    with open(MEMBER_TRACK_FILE) as f:
        processed_states = set(json.load(f))
print(f"Already processed states: {processed_states}")

# Pick 2-3 unprocessed states
available = [s for s in sorted(state_codes) if s not in processed_states]
if not available:
    print("ALL STATES PROCESSED. Resetting.")
    available = sorted(state_codes)
    processed_states = set()

target_states = available[:3]
print(f"Targeting states: {target_states}")

results = {}
for state in target_states:
    try:
        url = f"https://capitolwatch.us/api/state/{state}"
        print(f"\n=== Fetching {url} ===")
        r = urlopen(url, timeout=30)
        members = json.loads(r.read())
        results[state] = members
        print(f"Got data for {state}: {type(members).__name__}")
        if isinstance(members, dict):
            for k, v in list(members.items())[:5]:
                print(f"  {k}: {str(v)[:200]}")
        elif isinstance(members, list):
            for m in members[:5]:
                print(f"  {str(m)[:200]}")
    except Exception as e:
        print(f"ERROR fetching {state}: {e}")

# Save state data for next step
with open(os.path.join(OUTPUT_DIR, "target_states.json"), "w") as f:
    json.dump({"states": target_states, "results": {k: str(type(v)).__name__ for k, v in results.items()}}, f)

# Save which members have bills to process
all_members = []
member_details = {}
for state, members in results.items():
    if isinstance(members, list):
        all_members.extend(members)
        for m in members:
            if isinstance(m, dict):
                bid = m.get("id", "")
                if bid:
                    member_details[bid] = {"state": state, **m}
    elif isinstance(members, dict):
        for bid, minfo in members.items():
            all_members.append(bid)
            minfo_dict = minfo if isinstance(minfo, dict) else {"name": str(minfo)}
            minfo_dict["state"] = state
            member_details[bid] = minfo_dict

with open(os.path.join(OUTPUT_DIR, "member_details.json"), "w") as f:
    json.dump(member_details, f, indent=2, default=str)

with open(os.path.join(OUTPUT_DIR, "member_ids.json"), "w") as f:
    json.dump([{"id": mid, "info": member_details.get(mid, {})} for mid in all_members], f, indent=2, default=str)

print(f"\nTotal members found: {len(all_members)}")
print(f"Member IDs: {all_members[:10]}")
print(json.dumps({"states": target_states, "member_count": len(all_members), "members": all_members[:20]}))
