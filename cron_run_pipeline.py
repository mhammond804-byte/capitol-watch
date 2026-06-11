#!/usr/bin/env python3
"""
Complete pipeline: fetch sponsored bills for MD and ME members,
find uncached ones, fetch summaries, generate pros/cons, merge to cache.
"""
import json, os, subprocess, time, sys
from datetime import datetime

CONGRESS_API_KEY="xH3oHkvJab5BzhnVvJ5zXk3bHK5fPqHZ263Asebc"
CACHE_FILE=os.path.expanduser("~/Desktop/capitol-watch/bill-analysis.json")

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

def fetch_current_members(state_code):
    data = fetch_json(f"https://capitolwatch.us/api/state/{state_code}")
    if not isinstance(data, dict):
        return []
    members = []
    for chamber in ['house', 'senate']:
        for m in data.get(chamber, []):
            terms = m.get('terms', {}).get('item', [])
            if terms:
                last = terms[-1]
                end = last.get('endYear')
                if end is None:
                    members.append({
                        'bioguideId': m['bioguideId'],
                        'name': m['name'],
                        'chamber': 'House' if chamber == 'house' else 'Senate',
                        'party': m.get('partyName', ''),
                        'district': m.get('district', ''),
                        'state': state_code
                    })
    return members

def fetch_sponsored_bills(bioguide):
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
                c = int(c)
                if c == 119:
                    all_bills.append(item)
        last_congress = items[-1].get("congress", 119)
        if isinstance(last_congress, (int, str)):
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
    trimmed = summary_text[:300]
    lower = summary_text.lower()

    pros = []
    cons = []

    # Generate pros based on content
    patterns = [
        ("protect" in lower or "safeguard" in lower, "Protects important public interests and safety."),
        ("establish" in lower or "create" in lower or "direct", "Creates a clear framework for addressing this issue."),
        ("support" in lower or "assist" in lower or "help" in lower, "Provides direct assistance to those affected."),
        ("improve" in lower or "enhance" in lower or "strengthen", "Strengthens existing systems for better outcomes."),
        ("fund" in lower or "grant" in lower or "authorize" in lower, "Authorizes funding to support critical programs."),
        ("prevent" in lower or "reduce" in lower or "limit" in lower, "Reduces risks and prevents potential harm."),
        ("study" in lower or "investigate" in lower or "research", "Supports research for informed policymaking."),
        ("require" in lower or "mandate" in lower, "Establishes accountability through clear requirements."),
        ("amend" in lower or "modify" in lower or "revise", "Updates outdated laws to reflect current needs."),
        ("expand" in lower or "increase" in lower or "extend", "Expands access to important services."),
    ]
    for match, pro in patterns:
        if match and len(pros) < 2:
            pros.append(pro)

    # Cons based on topic keywords
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

    with open(CACHE_FILE) as f:
        cache = json.load(f)
    cached_keys = set(cache.keys())
    print(f"Cache has {len(cached_keys)} entries")

    states = ['MD', 'ME']
    all_new_bills = {}
    total_uncached = 0
    all_members = {}

    for state in states:
        print(f"\n--- {state} ---")
        members = fetch_current_members(state)
        all_members[state] = members
        print(f"  Current members: {len(members)}")

        for m in members:
            bid = m['bioguideId']
            name = m['name']
            chamber = m['chamber']
            if m.get('district'):
                label = f"{chamber[0]}. {name} ({m['state']}-{m['district']})"
            else:
                label = f"{chamber[0]}. {name} ({m['state']})"
            print(f"  {label} [{bid}]")

            bills = fetch_sponsored_bills(bid)
            print(f"    119th sponsored bills: {len(bills)}")

            new_count = 0
            for b in bills:
                congress = b.get("congress")
                bill_type = b.get("type", "")
                number = b.get("number", "")
                if not (congress and bill_type and number):
                    continue
                bill_type = bill_type.lower()

                key = f"{congress}/{bill_type}/{number}"
                if key in cached_keys or key in all_new_bills:
                    continue

                if m.get('district'):
                    sponsor = f"{'Rep.' if chamber == 'House' else 'Sen.'} {name} ({m['state']}-{m['district']})"
                else:
                    sponsor = f"{'Rep.' if chamber == 'House' else 'Sen.'} {name} ({m['state']})"

                all_new_bills[key] = {
                    "title": b.get("title", ""),
                    "congress": congress,
                    "type": bill_type,
                    "number": number,
                    "bill_url": b.get("url", ""),
                    "sponsor_name": sponsor,
                    "sponsor_bioguide": bid,
                    "sponsor_chamber": chamber,
                    "sponsor_state": state,
                    "introduced_date": b.get("introducedDate", ""),
                    "policy_area": b.get("policyArea", {}).get("name", "") if isinstance(b.get("policyArea"), dict) else "",
                }
                new_count += 1
                total_uncached += 1

            print(f"    New uncached: {new_count}")
            time.sleep(0.3)

        state_count = sum(1 for v in all_new_bills.values() if v['sponsor_state'] == state)
        print(f"  Total uncached 119th for {state}: {state_count}")

    print(f"\n{'='*60}")
    print(f"FOUND {total_uncached} NEW UNCACHED 119TH BILLS TOTAL")
    print(f"{'='*60}")

    if total_uncached == 0:
        print("Nothing to process.")
        tracking = {
            "states": states,
            "timestamp": datetime.now().strftime("%Y-%m-%d"),
            "bills_added": 0,
            "note": f"Scanned {states[0]} ({len(all_members.get(states[0], []))} members) + {states[1]} ({len(all_members.get(states[1], []))} members). No uncached 119th bills found."
        }
        return tracking

    bill_keys = sorted(all_new_bills.keys())[:20]
    bills_to_process = {k: all_new_bills[k] for k in bill_keys}
    print(f"\nProcessing {len(bills_to_process)} bills (capped at 20)")

    processed = 0
    bills_added = 0
    failed = []

    for key, bill_info in bills_to_process.items():
        processed += 1
        title_short = bill_info['title'][:80]
        print(f"\n[{processed}/{len(bills_to_process)}] {key}: {title_short}")

        summary_text = fetch_summary(bill_info['congress'], bill_info['type'], bill_info['number'])

        if not summary_text or len(summary_text.strip()) < 20:
            print(f"  No summary available - skipping")
            failed.append(key)
            continue

        result = generate_pros_cons(bill_info['title'], summary_text)
        if not result:
            print(f"  Could not generate pros/cons - skipping")
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
            print(f"  ADDED: pro={result['pros'][0][:50]} | con={result['cons'][0][:50]}")
            bills_added += 1
        else:
            print(f"  Already in cache")

        time.sleep(0.3)

    print(f"\n{'='*60}")
    print(f"RESULTS: {bills_added} bills added, {len(failed)} skipped (no summary)")
    print(f"Cache now: {len(cache)} entries")
    print(f"{'='*60}")

    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=2)
    print(f"Cache saved ({len(cache)} entries)")

    tracking = {
        "states": states,
        "timestamp": datetime.now().strftime("%Y-%m-%d"),
        "bills_added": bills_added,
        "note": (
            f"Scanned {states[0]} ({len(all_members.get(states[0], []))} members)"
            f" + {states[1]} ({len(all_members.get(states[1], []))} members)."
            f" Found {total_uncached} uncached 119th bills,"
            f" processed {len(bills_to_process)},"
            f" added {bills_added}."
        ),
        "failed_count": len(failed),
        "cache_now": len(cache)
    }
    return tracking

if __name__ == "__main__":
    result = main()

    with open(os.path.expanduser("~/.hermes/logs/capitol_watch_states_done.json"), "w") as f:
        json.dump(result, f, indent=2)

    print("\nTracking file written.")
