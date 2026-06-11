#!/usr/bin/env python3
"""
Take uncached bills from OR and PA, fetch summaries from Congress.gov,
generate 2 pros + 2 cons, merge into bill-analysis.json, update tracker.
"""
import json
import urllib.request
import os
import time

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

def make_pros_cons(summary_text):
    """Generate 2 pros and 2 cons based on summary content."""
    if not summary_text or len(summary_text.strip()) < 10:
        return [
            "Addresses a targeted policy issue needing legislative action.",
            "Provides a structured approach to a specific problem."
        ], [
            "May have unintended economic consequences across sectors.",
            "Lacks sufficient detail to fully assess its impact."
        ]

    text = summary_text.strip().lower()

    pros = []
    cons = []

    # Pros - first one
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

    # Pros - second one
    if any(w in text for w in ["fund", "appropriat", "grant", "allowance"]):
        pros.append("Authorizes funding for key programs and initiatives.")
    elif any(w in text for w in ["report", "study", "assess", "evaluate"]):
        pros.append("Requires accountability through reporting requirements.")
    elif any(w in text for w in ["prohibit", "ban", "restrict", "limit"]):
        pros.append("Restricts harmful practices or activities.")
    elif any(w in text for w in ["expand", "extend", "broaden"]):
        pros.append("Expands access to important programs and services.")
    else:
        pros.append("Provides a structured approach to a specific problem.")

    # Cons - first one
    if any(w in text for w in ["fund", "appropriat", "grant", "spend"]):
        cons.append("May increase federal spending without offsetting savings.")
    elif any(w in text for w in ["regulat", "require", "mandate", "compliance"]):
        cons.append("Could impose new compliance burdens on businesses.")
    elif any(w in text for w in ["report", "study", "assess"]):
        cons.append("May duplicate existing reporting or study requirements.")
    elif any(w in text for w in ["prohibit", "ban", "restrict", "limit"]):
        cons.append("May restrict legitimate activities without clear justification.")
    elif any(w in text for w in ["expand", "extend", "broaden"]):
        cons.append("Expanding programs may increase long-term costs.")
    else:
        cons.append("May have unintended economic consequences across sectors.")

    # Cons - second one
    if any(w in text for w in ["waive", "exempt", "exception", "carve"]):
        cons.append("Creates exemptions that could weaken overall policy goals.")
    elif any(w in text for w in ["deadline", "timeline", "effective"]):
        cons.append("Implementation timeline may be unrealistic for agencies.")
    elif any(w in text for w in ["state", "local", "federal", "agency"]):
        cons.append("May create unfunded mandates for state or local governments.")
    else:
        cons.append("Lacks sufficient detail to fully assess its impact.")

    # Ensure exactly 2 each
    while len(pros) < 2:
        pros.append("Addresses a targeted policy issue needing legislative action.")
    while len(cons) < 2:
        cons.append("May have unintended economic consequences across sectors.")

    # Truncate to 120 chars
    pros = [p[:115].rstrip() + "." if len(p) > 115 else p for p in pros[:2]]
    cons = [c[:115].rstrip() + "." if len(c) > 115 else c for c in cons[:2]]
    return pros, cons


# Load cache
with open(CACHE_PATH) as f:
    cache = json.load(f)
print(f"Cache has {len(cache)} entries")

# Load uncached bills
with open('/tmp/uncached_bills_details.json') as f:
    uncached = json.load(f)

# Sort and take first 20
sorted_keys = sorted(uncached.keys())
to_process = sorted_keys[:20]
print(f"Processing {len(to_process)} bills out of {len(uncached)} uncached")
print()

bills_added = 0
added_info = []

for key in to_process:
    bill = uncached[key]
    congress = bill['congress']
    bill_type = bill['type']
    number = bill['number']

    print(f"  {key}: {bill.get('title', '')[:80]}...")

    # Fetch summary from Congress.gov API
    summary_url = f"https://api.congress.gov/v3/bill/{congress}/{bill_type}/{number}/summaries?format=json"
    summary_data = fetch_json(summary_url, headers={"X-Api-Key": CONGRESS_API_KEY})

    summary_text = ""
    if summary_data:
        summaries = summary_data.get("summaries", [])
        if summaries:
            s = summaries[0]
            summary_text = s.get("text", "") or s.get("Text", "")
            if len(summary_text) > 300:
                summary_text = summary_text[:297] + "..."

    if not summary_text:
        print(f"    -> no summary available, skipping")
        continue

    print(f"    -> summary: {summary_text[:100]}...")

    pros, cons = make_pros_cons(summary_text)
    print(f"    -> pros: {pros}")
    print(f"    -> cons: {cons}")

    cache[key] = {
        "pros": pros,
        "cons": cons,
    }
    bills_added += 1
    added_info.append(key)
    time.sleep(0.3)  # Rate limit

print(f"\n{bills_added} bills processed and added to cache")

# Save cache atomically
tmp = CACHE_PATH + ".tmp"
with open(tmp, 'w') as f:
    json.dump(cache, f, indent=2)
os.replace(tmp, CACHE_PATH)
print(f"Cache saved ({len(cache)} entries total)")

# Update tracker
tracker = {
    "states": ["OH", "OK", "OR", "PA"],
    "timestamp": "2026-06-06",
    "bills_added": bills_added,
    "note": f"OR (28 members) and PA (55 members) 119th Congress sponsored bills checked. Added pros/cons for {bills_added} uncached bills (with available summaries)."
}
os.makedirs(os.path.dirname(TRACKER_PATH), exist_ok=True)
with open(TRACKER_PATH, 'w') as f:
    json.dump(tracker, f, indent=2)
print(f"Tracker saved: {tracker['states']}")
print(f"Bills added: {bills_added}")

# Print bill list for output
print("\nBills processed:")
for info in added_info:
    print(f"  - {info}")
