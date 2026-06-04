#!/usr/bin/env python3
"""
Main pipeline: Fetch member-sponsored bills for 2 states, check cache, fetch summaries, 
and generate pros/cons. Processes 2 states per run.
"""
import json, os, subprocess, time, sys
from datetime import datetime

# === CONFIG ===
CONGRESS_API_KEY = "xH3oHkvJab5BzhnVvJ5zXk3bHK5fPqHZ263Asebc"
CACHE_FILE = os.path.expanduser("~/Desktop/capitol-watch/bill-analysis.json")
PROGRESS_FILE = os.path.expanduser("~/Desktop/capitol-watch/.bill-fill-progress.json")
TRACKING_FILE = os.path.expanduser("~/Desktop/capitol-watch/.state-tracking.json")
BILL_LIST_PATH = "/tmp/new_bills_to_process.json"
SUMMARY_PATH = "/tmp/bill_summaries.json"
PROS_CONS_DIR = "/tmp/pros_cons_batches"

os.makedirs(PROS_CONS_DIR, exist_ok=True)

def fetch_json(url, headers=None, timeout=20):
    cmd = ["curl", "-s", "--max-time", str(timeout)]
    if headers:
        for k, v in headers.items():
            cmd.extend(["-H", f"{k}: {v}"])
    cmd.append(url)
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout+5)
    if r.returncode != 0:
        return None
    try:
        return json.loads(r.stdout)
    except:
        return None

def get_us_states():
    """Get list of US state codes from the Capitol Watch API."""
    data = fetch_json("https://capitolwatch.us/api/states")
    if isinstance(data, list):
        return [s["code"] for s in data if isinstance(s, dict) and s.get("code")]
    return []

def fetch_state_members(state):
    """Get all House and Senate members for a state via Capitol Watch API."""
    data = fetch_json(f"https://capitolwatch.us/api/state/{state}")
    if not isinstance(data, dict):
        return [], []
    house = data.get("house", [])
    senate = data.get("senate", [])
    return house, senate

def fetch_sponsored_bills(bioguide, max_congress=119, min_congress=118):
    """Fetch all sponsored legislation for a member, paginating through results."""
    all_bills = []
    url = f"https://api.congress.gov/v3/member/{bioguide}/sponsored-legislation?format=json&limit=20"
    page_num = 0
    while url:
        page_num += 1
        if page_num > 50:
            break
        data = fetch_json(url, headers={"X-Api-Key": CONGRESS_API_KEY})
        if not data:
            break
        items = data.get("sponsoredLegislation", [])
        if not items:
            break
        for item in items:
            c = item.get("congress")
            if c and isinstance(c, (int, str)):
                c = int(c)
                if min_congress <= c <= max_congress:
                    all_bills.append(item)
        last_congress = items[-1].get("congress", max_congress)
        if isinstance(last_congress, (int, str)):
            try:
                if int(last_congress) < min_congress:
                    break
            except:
                pass
        pagination = data.get("pagination", {})
        url = pagination.get("next")
        if url:
            time.sleep(0.2)
    return all_bills

def load_cache():
    with open(CACHE_FILE) as f:
        return json.load(f)

def save_cache(cache):
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=2)

def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE) as f:
            return json.load(f)
    return {"states_completed": [], "members_processed": 0, "bills_added": 0}

def save_progress(p):
    with open(PROGRESS_FILE, "w") as f:
        json.dump(p, f, indent=2)

def load_tracking():
    if os.path.exists(TRACKING_FILE):
        with open(TRACKING_FILE) as f:
            return json.load(f)
    return {"states_done": [], "last_run": "", "bills_added": 0, "total_cache": 0}

def save_tracking(t):
    with open(TRACKING_FILE, "w") as f:
        json.dump(t, f, indent=2)

# === STEP 1: Determine which states to process ===
print("=" * 60)
print("CAPITOL WATCH - Member Sponsored Bill Analysis")
print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
print("=" * 60)

progress = load_progress()
tracking = load_tracking()
cache = load_cache()
cached_keys = set(cache.keys())

print(f"Current cache: {len(cache)} entries")
print(f"Previously processed states: {progress['states_completed']}")

all_states = get_us_states()
if not all_states:
    print("ERROR: Could not fetch states list!")
    sys.exit(1)

# States already processed through the sponsored bill pipeline
done_states = progress["states_completed"]
unprocessed = sorted([s for s in all_states if s not in done_states])

print(f"All US states: {len(all_states)}")
print(f"Still unprocessed: {unprocessed}")

if not unprocessed:
    print("ALL STATES PROCESSED! Pipeline complete. Resetting for new cycle.")
    unprocessed = all_states
    done_states = []

# Pick first 2 unprocessed states
target_states = unprocessed[:2]
print(f"\nTargeting states: {target_states}")

# === STEP 2: For each state, get members and their sponsored bills ===
all_new_bills = {}  # cache_key -> bill info
members_processed = 0
total_new = 0

for state in target_states:
    print(f"\n--- {state} ---")
    house, senate = fetch_state_members(state)
    
    # House members
    for member in house:
        bid = member.get("bioguideId", "")
        name = member.get("name", "Unknown")
        district = member.get("district", "At-Large")
        print(f"  Rep. {name} ({state}-{district}) [{bid}]")
        
        bills = fetch_sponsored_bills(bid)
        print(f"    Sponsored bills (118-119th Congress): {len(bills)}")
        members_processed += 1
        
        member_new = 0
        for b in bills:
            congress = b.get("congress")
            bill_type = b.get("type", "")
            number = b.get("number", "")
            if not (congress and bill_type and number):
                continue
            bill_type = bill_type.lower()
            key = f"{congress}/{bill_type}/{number}".lower()
            
            if key in cached_keys or key in all_new_bills:
                continue
            
            all_new_bills[key] = {
                "title": b.get("title", ""),
                "congress": congress,
                "type": bill_type,
                "number": number,
                "bill_url": b.get("url", ""),
                "sponsor_name": f"Rep. {name} ({state}-{district})",
                "sponsor_bioguide": bid,
                "sponsor_chamber": "House",
                "sponsor_state": state,
                "introduced_date": b.get("introducedDate", ""),
                "policy_area": b.get("policyArea", {}).get("name") if isinstance(b.get("policyArea"), dict) else "",
            }
            member_new += 1
            total_new += 1
        
        print(f"    New uncached: {member_new}")
        time.sleep(0.5)  # Rate limit
    
    # Senate members
    for member in senate:
        bid = member.get("bioguideId", "")
        name = member.get("name", "Unknown")
        print(f"  Sen. {name} ({state}) [{bid}]")
        
        bills = fetch_sponsored_bills(bid)
        print(f"    Sponsored bills (118-119th Congress): {len(bills)}")
        members_processed += 1
        
        member_new = 0
        for b in bills:
            congress = b.get("congress")
            bill_type = b.get("type", "")
            number = b.get("number", "")
            if not (congress and bill_type and number):
                continue
            bill_type = bill_type.lower()
            key = f"{congress}/{bill_type}/{number}".lower()
            
            if key in cached_keys or key in all_new_bills:
                continue
            
            all_new_bills[key] = {
                "title": b.get("title", ""),
                "congress": congress,
                "type": bill_type,
                "number": number,
                "bill_url": b.get("url", ""),
                "sponsor_name": f"Sen. {name} ({state})",
                "sponsor_bioguide": bid,
                "sponsor_chamber": "Senate",
                "sponsor_state": state,
                "introduced_date": b.get("introducedDate", ""),
                "policy_area": b.get("policyArea", {}).get("name") if isinstance(b.get("policyArea"), dict) else "",
            }
            member_new += 1
            total_new += 1
        
        print(f"    New uncached: {member_new}")
        time.sleep(0.5)
    
    # Mark this state as done
    if state not in done_states:
        done_states.append(state)
    progress["states_completed"] = done_states
    save_progress(progress)

print(f"\n{'='*60}")
print(f"FOUND {total_new} NEW UNCACHED BILLS from {members_processed} members in {target_states}")
print(f"{'='*60}")
print(f"Bills breakdown:")
for key in sorted(all_new_bills.keys()):
    b = all_new_bills[key]
    print(f"  {key} | {b['sponsor_name']} | {b['title'][:80]}")

# Save bill list
with open(BILL_LIST_PATH, "w") as f:
    json.dump(all_new_bills, f, indent=2)
print(f"\nSaved bill list to {BILL_LIST_PATH}")

# Also save summary for delegation tasks
output_summary = {
    "target_states": target_states,
    "states_done": done_states,
    "members_processed": members_processed,
    "new_bills": len(all_new_bills),
    "steps_remaining": ["fetch_summaries", "generate_pros_cons", "merge_commit"]
}
print(f"\nDone with step 1. JSON result for downstream:")
print(json.dumps(output_summary))
