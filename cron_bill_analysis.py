#!/usr/bin/env python3
"""
Capitol Watch Bill Analysis Pipeline
Uses Congress.gov API to fetch 119th sponsored bills for current members,
finds uncached bills, generates pros/cons, merges to cache.
"""
import json, os, subprocess, time
from datetime import datetime

CONGRESS_API_KEY="xH3oHkvJab5BzhnVvJ5zXk3bHK5fPqHZ263Asebc"
CACHE_PATH = os.path.expanduser("~/Desktop/capitol-watch/bill-analysis.json")
TRACKER_PATH = os.path.expanduser("~/.hermes/logs/capitol_watch_states_done.json")

ALL_STATES = ['AK','AL','AR','AZ','CA','CO','CT','DE','FL','GA',
              'HI','IA','ID','IL','IN','KS','KY','LA','MA','MD',
              'ME','MI','MN','MO','MS','MT','NC','ND','NE','NH',
              'NJ','NM','NV','NY','OH','OK','OR','PA','RI','SC',
              'SD','TN','TX','UT','VA','VT','WA','WI','WV','WY']

def fetch_json(url, headers=None, timeout=20):
    cmd = ["curl", "-s", "--max-time", str(timeout)]
    if headers:
        for k, v in headers.items():
            cmd.extend(["-H", f"{k}: {v}"])
    cmd.append(url)
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout+5)
        if r.returncode != 0 or not r.stdout.strip():
            return None
        return json.loads(r.stdout)
    except Exception as e:
        print(f"  Error fetching {url}: {e}")
        return None

def load_cache():
    with open(CACHE_PATH) as f:
        return json.load(f)

def save_cache(cache):
    tmp = CACHE_PATH + ".tmp"
    with open(tmp, 'w') as f:
        json.dump(cache, f, indent=2)
    os.replace(tmp, CACHE_PATH)

def fetch_current_members(state_code):
    """Get current members for a state from capitolwatch.us API."""
    data = fetch_json(f"https://capitolwatch.us/api/state/{state_code}")
    if not isinstance(data, dict):
        return []
    members = []
    for chamber in ['house', 'senate']:
        for m in data.get(chamber, []):
            terms = m.get('terms', {}).get('item', [])
            bioguide = m.get('bioguideId', '')
            name = m.get('name', '')
            if not bioguide or not name:
                continue
            # Check if this is a current member (term ending with no endYear or current)
            is_current = False
            if terms:
                last = terms[-1]
                end = last.get('endYear')
                if end is None or str(end) == '':
                    is_current = True
            if is_current:
                chamber_name = 'Senate' if chamber == 'senate' else 'House'
                members.append({
                    'bioguideId': bioguide,
                    'name': name,
                    'chamber': chamber_name,
                    'party': m.get('partyName', ''),
                    'district': m.get('district', ''),
                    'state': state_code
                })
    return members

def fetch_sponsored_bills(bioguide):
    """Fetch 119th Congress sponsored bills for a member via Congress.gov API."""
    all_bills = []
    url = f"https://api.congress.gov/v3/member/{bioguide}/sponsored-legislation?format=json&limit=20"
    page_num = 0
    while url:
        page_num += 1
        if page_num > 30:
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
                try:
                    if int(c) == 119:
                        all_bills.append(item)
                except:
                    pass
        # Stop if we've moved past the 119th Congress
        last_congress = items[-1].get("congress", 119)
        try:
            if int(last_congress) < 119:
                break
        except:
            pass
        pagination = data.get("pagination", {})
        url = pagination.get("next")
        if url:
            time.sleep(0.2)
    return all_bills

def fetch_summary(congress, bill_type, number):
    url = f"https://api.congress.gov/v3/bill/{congress}/{bill_type}/{number}/summaries?format=json"
    data = fetch_json(url, headers={"X-Api-Key": CONGRESS_API_KEY})
    if not data or "summaries" not in data:
        return None
    summaries = data["summaries"]
    if not summaries:
        return None
    texts = [s.get("text", "") for s in summaries if s.get("text")]
    if texts:
        return max(texts, key=len)
    return None

def generate_pros_cons(title, summary_text):
    if not summary_text or len(summary_text.strip()) < 20:
        return None
    lower = summary_text.lower()
    pros = []
    cons = []
    patterns = [
        ("protect" in lower or "safeguard" in lower, "Protects important public interests and safety."),
        ("establish" in lower or "create" in lower or "direct" in lower, "Creates a clear framework for addressing this issue."),
        ("support" in lower or "assist" in lower or "help" in lower, "Provides direct assistance to those affected."),
        ("improve" in lower or "enhance" in lower or "strengthen" in lower, "Strengthens existing systems for better outcomes."),
        ("fund" in lower or "grant" in lower or "authorize" in lower, "Authorizes funding to support critical programs."),
        ("prevent" in lower or "reduce" in lower or "limit" in lower, "Reduces risks and prevents potential harm."),
        ("study" in lower or "investigate" in lower or "research" in lower, "Supports research for informed policymaking."),
        ("require" in lower or "mandate" in lower, "Establishes accountability through clear requirements."),
        ("amend" in lower or "modify" in lower or "revise" in lower, "Updates outdated laws to reflect current needs."),
        ("expand" in lower or "increase" in lower or "extend" in lower, "Expands access to important services."),
    ]
    for match, pro in patterns:
        if match and len(pros) < 2:
            pros.append(pro)
    if "fund" in lower or "grant" in lower or "authorize" in lower:
        cons.append("May require significant taxpayer funding.")
    elif "regulat" in lower or "agency" in lower or "department" in lower:
        cons.append("May expand federal oversight and bureaucracy.")
    elif "amend" in lower or "modify" in lower:
        cons.append("Could have unintended effects on related laws.")
    else:
        cons.append("May create new regulatory burdens.")
    if "state" in lower or "local" in lower:
        cons.append("Could impose unfunded mandates on states.")
    elif "tax" in lower or "fee" in lower:
        cons.append("May increase financial burden on taxpayers.")
    elif "penalt" in lower or "criminal" in lower or "enforcement" in lower:
        cons.append("Enforcement mechanisms may disproportionately impact certain groups.")
    else:
        cons.append("May face legal challenges or implementation delays.")
    while len(pros) < 2:
        pros.append("Addresses an important policy issue needing legislative action.")
    while len(cons) < 2:
        cons.append("May have unintended consequences across related sectors.")
    return {"pros": pros[:2], "cons": cons[:2]}

def main():
    print("=" * 60)
    print("CAPITOL WATCH - Bill Analysis Pipeline")
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 60)

    # Load cache
    cache = load_cache()
    cached_keys = set(cache.keys())
    print(f"Cache has {len(cached_keys)} entries")

    # Determine next states to process
    try:
        with open(TRACKER_PATH) as f:
            tracker = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        tracker = {"states": []}

    done_states = list(tracker.get("states", []))
    print(f"Previously processed states: {done_states}")

    # Find next 2 undone states alphabetically
    done_set = set(done_states)
    undone = [s for s in ALL_STATES if s not in done_set]
    if not undone:
        done_set.clear()
        undone = ALL_STATES
        print("All states done, resetting.")
    next_states = sorted(undone)[:2]
    print(f"Next states: {next_states}")
    if not next_states:
        print("[SILENT]")
        return

    all_new_bills = {}
    all_members = {}

    for state in next_states:
        print(f"\n--- {state} ---")
        members = fetch_current_members(state)
        all_members[state] = members
        print(f"  Current members: {len(members)}")

        for m in members:
            bid = m['bioguideId']
            name = m['name']
            chamber = m['chamber']
            label = f"{chamber[0]}. {name} ({m['state']}-{m['district']})" if m.get('district') else f"{chamber[0]}. {name} ({m['state']})"
            print(f"  {label} [{bid}]", end=" ", flush=True)

            bills = fetch_sponsored_bills(bid)
            print(f"→ {len(bills)} 119th bills")

            new_count = 0
            for b in bills:
                congress = b.get("congress")
                bill_type = b.get("type", "")
                number = b.get("number", "")
                if not (congress and bill_type and number):
                    continue
                bill_type = str(bill_type).lower()
                key = f"{congress}/{bill_type}/{number}"

                if key in cached_keys or key in all_new_bills:
                    continue

                sponsor = f"{'Rep.' if chamber == 'House' else 'Sen.'} {name} ({m['state']}-{m['district']})" if m.get('district') else f"{'Rep.' if chamber == 'House' else 'Sen.'} {name} ({m['state']})"
                all_new_bills[key] = {
                    "title": b.get("title", ""),
                    "congress": congress,
                    "type": bill_type,
                    "number": number,
                    "sponsor_name": sponsor,
                    "sponsor_bioguide": bid,
                    "sponsor_chamber": chamber,
                    "sponsor_state": state,
                    "introduced_date": b.get("introducedDate", ""),
                    "policy_area": b.get("policyArea", {}).get("name", "") if isinstance(b.get("policyArea"), dict) else "",
                }
                new_count += 1

            print(f"    New uncached: {new_count}")
            time.sleep(0.3)

        state_count = sum(1 for v in all_new_bills.values() if v['sponsor_state'] == state)
        print(f"  Total uncached for {state}: {state_count}")

    total_uncached = len(all_new_bills)
    print(f"\n{'='*60}")
    print(f"FOUND {total_uncached} NEW UNCACHED 119TH BILLS TOTAL")
    print(f"{'='*60}")

    if total_uncached == 0:
        print("Nothing to process.")
        tracker["states"] = list(done_set.union(next_states))
        tracker["timestamp"] = datetime.now().strftime("%Y-%m-%d")
        tracker["bills_added"] = 0
        tracker["note"] = f"Scanned {next_states[0]} ({len(all_members.get(next_states[0], []))} members) + {next_states[1]} ({len(all_members.get(next_states[1], []))} members). No uncached 119th bills found."
        os.makedirs(os.path.dirname(TRACKER_PATH), exist_ok=True)
        with open(TRACKER_PATH, 'w') as f:
            json.dump(tracker, f, indent=2)
        print("Tracker updated. [SILENT]")
        return

    bill_keys = sorted(all_new_bills.keys())[:20]
    bills_to_process = {k: all_new_bills[k] for k in bill_keys}
    print(f"\nProcessing {len(bills_to_process)} bills (capped at 20)")

    processed = 0
    bills_added = 0
    failed = []

    for key, bill_info in bills_to_process.items():
        processed += 1
        title_short = bill_info['title'][:80] if bill_info['title'] else "No title"
        print(f"\n[{processed}/{len(bills_to_process)}] {key}: {title_short}")

        summary_text = fetch_summary(bill_info['congress'], bill_info['type'], bill_info['number'])

        if not summary_text or len(summary_text.strip()) < 20:
            print(f"  No summary - skipping")
            failed.append(key)
            continue

        result = generate_pros_cons(bill_info['title'], summary_text)
        if not result:
            print(f"  Cannot generate pros/cons - skipping")
            failed.append(key)
            continue

        trimmed_summary = summary_text[:300]
        entry = {
            "pros": result["pros"],
            "cons": result["cons"],
            "summary": trimmed_summary,
            "title": bill_info["title"],
            "sponsor_name": bill_info["sponsor_name"],
            "sponsor_bioguide": bill_info["sponsor_bioguide"],
            "sponsor_chamber": bill_info["sponsor_chamber"],
            "sponsor_state": bill_info["sponsor_state"],
            "introduced_date": bill_info["introduced_date"],
            "policy_area": bill_info["policy_area"],
        }

        if key not in cache:
            cache[key] = entry
            print(f"  ADDED: {result['pros'][0]} / {result['cons'][0]}")
            bills_added += 1
        else:
            print(f"  Already cached (race)")

        time.sleep(0.3)

    print(f"\n{'='*60}")
    print(f"RESULTS: {bills_added} added, {len(failed)} skipped (no summary)")
    print(f"Cache now: {len(cache)} entries")
    print(f"{'='*60}")

    # Save
    save_cache(cache)
    print(f"Cache saved")

    # Update tracker
    tracker["states"] = list(done_set.union(next_states))
    tracker["timestamp"] = datetime.now().strftime("%Y-%m-%d")
    tracker["bills_added"] = bills_added
    tracker["note"] = (
        f"Scanned {next_states[0]} ({len(all_members.get(next_states[0], []))} members)"
        f" + {next_states[1]} ({len(all_members.get(next_states[1], []))} members)."
        f" Found {total_uncached} uncached, processed {len(bills_to_process)},"
        f" added {bills_added}."
    )
    tracker["failed_count"] = len(failed)
    tracker["cache_now"] = len(cache)

    os.makedirs(os.path.dirname(TRACKER_PATH), exist_ok=True)
    with open(TRACKER_PATH, 'w') as f:
        json.dump(tracker, f, indent=2)
    print("Tracker written.")

if __name__ == "__main__":
    main()
