#!/usr/bin/env python3
"""Cron job: find uncached bills for AZ and CA members, generate pros/cons, merge."""
import json, os, sys, urllib.request, time

CACHE_PATH = os.path.expanduser("~/Desktop/capitol-watch/bill-analysis.json")
CONGRESS_API_KEY = "xH3oHkvJab5BzhnVvJ5zXk3bHK5fPqHZ263Asebc"
TRACKER_PATH = os.path.expanduser("~/.hermes/logs/capitol_watch_states_done.json")

def fetch_json(url, headers=None):
    req = urllib.request.Request(url)
    req.add_header("User-Agent", "Capitol-Watch/1.0 (research; contact@capitolwatch.us)")
    if headers:
        for k, v in headers.items():
            req.add_header(k, v)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        print(f"  Error fetching {url}: {e}")
        return None

def load_cache():
    with open(CACHE_PATH) as f:
        return json.load(f)

def save_cache(cache):
    # Write to temp then atomically rename
    tmp = CACHE_PATH + ".tmp"
    with open(tmp, 'w') as f:
        json.dump(cache, f, indent=2)
    os.replace(tmp, CACHE_PATH)

def make_key(congress, bill_type, number):
    """Normalize bill key."""
    return f"{congress}/{bill_type}/{number}".lower()

def make_pros_cons(summary_text, bill_id):
    """Generate 2 pros and 2 cons based on summary."""
    # Generic fallback pros/cons if we can't derive from summary
    generic_pros = [
        "Addresses a targeted policy issue needing legislative action.",
        "Provides a structured approach to a specific problem.",
    ]
    generic_cons = [
        "May have unintended economic consequences across sectors.",
        "Lacks sufficient detail to fully assess its impact.",
    ]
    
    if not summary_text or len(summary_text.strip()) < 10:
        return generic_pros, generic_cons

    text = summary_text.strip().lower()
    words = text.split()
    
    pros = []
    cons = []
    
    # Try to derive pros from summary content
    if any(w in text for w in ["improve", "enhance", "strengthen", "support", "protect", "increase"]):
        pros.append("Strengthens existing protections or support systems.")
    elif any(w in text for w in ["establish", "create", "authorize", "direct"]):
        pros.append("Establishes new framework to address a policy gap.")
    elif any(w in text for w in ["reduce", "decrease", "lower", "cut"]):
        pros.append("Reduces regulatory or financial burdens where possible.")
    elif any(w in text for w in ["clarify", "define", "specify", "standardize"]):
        pros.append("Provides clarity and consistency in existing law.")
    else:
        pros.append("Addresses a targeted policy issue needing legislative action.")
    
    if any(w in text for w in ["fund", "appropriat", "grant", "allowance"]):
        pros.append("Authorizes funding for key programs and initiatives.")
    elif any(w in text for w in ["report", "study", "assess", "evaluate"]):
        pros.append("Requires accountability through reporting requirements.")
    elif any(w in text for w in ["prohibit", "ban", "restrict", "limit"]):
        pros.append("Restricts harmful practices or activities.")
    else:
        pros.append("Provides a structured approach to a specific problem.")
    
    # Derive cons
    if any(w in text for w in ["fund", "appropriat", "grant", "spend"]):
        cons.append("May increase federal spending without offsetting savings.")
    elif any(w in text for w in ["regulat", "require", "mandate", "compliance"]):
        cons.append("Could impose new compliance burdens on businesses.")
    elif any(w in text for w in ["report", "study", "assess"]):
        cons.append("May duplicate existing reporting or study requirements.")
    elif any(w in text for w in ["prohibit", "ban", "restrict", "limit"]):
        cons.append("May restrict legitimate activities without clear justification.")
    else:
        cons.append("May have unintended economic consequences across sectors.")
    
    if any(w in text for w in ["waive", "exempt", "exception", "carve"]):
        cons.append("Creates exemptions that could weaken overall policy goals.")
    elif any(w in text for w in ["deadline", "timeline", "effective"]):
        cons.append("Implementation timeline may be unrealistic for agencies.")
    elif any(w in text for w in ["state", "local", "federal", "agency"]):
        cons.append("May create unfunded mandates for state or local governments.")
    else:
        cons.append("Lacks sufficient detail to fully assess its impact.")
    
    # Ensure 2 each
    while len(pros) < 2:
        pros.append("Addresses a targeted policy issue needing legislative action.")
    while len(cons) < 2:
        cons.append("May have unintended economic consequences across sectors.")
    
    # Truncate to 120 chars
    return [p[:115].rstrip() + "." if len(p) > 115 else p for p in pros[:2]], \
           [c[:115].rstrip() + "." if len(c) > 115 else c for c in cons[:2]]

def process_state(state_code, cache):
    """Process all members for a state, find uncached bills, add pros/cons."""
    print(f"\n=== Processing {state_code} ===")
    
    state_url = f"https://capitolwatch.us/api/state/{state_code}"
    state_data = fetch_json(state_url)
    if not state_data:
        print(f"  Could not fetch {state_code} data")
        return 0, []
    
    members = []
    for chamber in ["house", "senate"]:
        members.extend(state_data.get(chamber, []))
    print(f"  Got {len(members)} members (house={len(state_data.get('house',[]))}, senate={len(state_data.get('senate',[]))})")
    
    all_bills = {}
    for member in members:
        bioguide = member.get("bioguideId", "")
        if not bioguide:
            continue
        
        member_url = f"https://capitolwatch.us/api/member/{bioguide}"
        member_data = fetch_json(member_url)
        if not member_data:
            continue
        
        sponsored = member_data.get("sponsored", [])
        if not sponsored:
            # Try alternate field names
            sponsored = member_data.get("bills", []) or member_data.get("legislation", []) or []
        
        for bill in sponsored:
            congress = bill.get("congress", bill.get("Congress", ""))
            bill_type = bill.get("type", bill.get("billType", bill.get("BillType", "")))
            number = bill.get("number", bill.get("billNumber", bill.get("BillNumber", "")))
            
            if congress and bill_type and number:
                key = make_key(congress, bill_type, number)
                if key not in cache and key not in all_bills:
                    # Get the title/summary
                    title = bill.get("title", bill.get("Title", ""))
                    all_bills[key] = {
                        "congress": congress,
                        "type": bill_type,
                        "number": number,
                        "title": title,
                    }
        
        time.sleep(0.2)  # Rate limit
    
    print(f"  Found {len(all_bills)} uncached bills")
    
    # Sort by key and take up to 20
    sorted_keys = sorted(all_bills.keys())
    to_process = sorted_keys[:20]
    
    bills_added = 0
    added_info = []
    
    for key in to_process:
        bill_info = all_bills[key]
        print(f"  Processing {key}...", end=" ")
        
        # Get summary from Congress.gov API
        summary_url = f"https://api.congress.gov/v3/bill/{bill_info['congress']}/{bill_info['type']}/{bill_info['number']}/summaries?format=json"
        summary_data = fetch_json(summary_url, headers={"X-Api-Key": CONGRESS_API_KEY})
        
        summary_text = ""
        if summary_data:
            summaries = summary_data.get("summaries", [])
            if summaries:
                summary_text = summaries[0].get("text", "") or summaries[0].get("Text", "")
                # Trim to 300 chars
                if len(summary_text) > 300:
                    summary_text = summary_text[:297] + "..."
        
        if not summary_text:
            print("no summary, skipping")
            continue
        
        pros, cons = make_pros_cons(summary_text, key)
        
        cache[key] = {
            "pros": pros,
            "cons": cons,
        }
        bills_added += 1
        added_info.append(key)
        print(f"added pros/cons")
        time.sleep(0.3)  # Rate limit for Congress.gov API
    
    return bills_added, added_info

def main():
    print("=" * 60)
    print("Capitol Watch - AI Bill Analysis Cron")
    print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Load cache
    cache = load_cache()
    print(f"Cache has {len(cache)} entries")
    
    # Load tracker
    try:
        with open(TRACKER_PATH) as f:
            tracker = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        tracker = {"states": []}
    
    done_states = set(tracker.get("states", []))
    print(f"Previously processed states: {done_states}")
    
    # Next 2 states alphabetically
    all_states = ["AK", "AL", "AR", "AZ", "CA", "CO", "CT", "DC", "DE", "FL", "GA", 
                  "HI", "IA", "ID", "IL", "IN", "KS", "KY", "LA", "MA", "MD", "ME", 
                  "MI", "MN", "MO", "MS", "MT", "NC", "ND", "NE", "NH", "NJ", "NM", 
                  "NV", "NY", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", 
                  "UT", "VA", "VT", "WA", "WI", "WV", "WY"]
    
    # Find next 2 undone states
    undone = [s for s in all_states if s not in done_states]
    if not undone:
        # Reset - all done
        done_states.clear()
        undone = all_states
    
    next_states = sorted(undone)[:2]
    print(f"Next states to process: {next_states}")
    
    total_added = 0
    all_added_info = []
    
    for state in next_states:
        added, info = process_state(state, cache)
        total_added += added
        all_added_info.extend(info)
        time.sleep(0.5)
    
    if total_added == 0:
        print("\nNo new bills found to process.")
        # Still update tracker so we don't retry same states
        tracker["states"] = list(done_states.union(next_states))
        tracker["timestamp"] = time.strftime("%Y-%m-%d")
        tracker["bills_added"] = 0
        tracker["note"] = f"No uncached bills found for {', '.join(next_states)} members"
        os.makedirs(os.path.dirname(TRACKER_PATH), exist_ok=True)
        with open(TRACKER_PATH, 'w') as f:
            json.dump(tracker, f, indent=2)
        save_cache(cache)
        print("Cache saved (unchanged), tracker updated.")
        return
    
    # Save cache
    save_cache(cache)
    print(f"\nSaved cache with {len(cache)} entries (+{total_added} new)")
    
    # Update tracker
    tracker["states"] = list(done_states.union(next_states))
    tracker["timestamp"] = time.strftime("%Y-%m-%d")
    tracker["bills_added"] = total_added
    tracker["note"] = f"Added pros/cons for {total_added} bills from {', '.join(next_states)} members"
    os.makedirs(os.path.dirname(TRACKER_PATH), exist_ok=True)
    with open(TRACKER_PATH, 'w') as f:
        json.dump(tracker, f, indent=2)
    
    print(f"Tracker updated: {next_states}")
    print(f"Bills added: {total_added}")
    for info in all_added_info:
        print(f"  - {info}")

if __name__ == "__main__":
    main()
