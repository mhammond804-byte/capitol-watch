#!/usr/bin/env python3
"""Update tracking files and save progress."""
import json, os

STATE_TRACKING = os.path.expanduser("~/Desktop/capitol-watch/.state-tracking.json")
BILL_PROGRESS = os.path.expanduser("~/Desktop/capitol-watch/.bill-fill-progress.json")
CACHE_FILE = os.path.expanduser("~/Desktop/capitol-watch/bill-analysis.json")

# Load tracking
with open(STATE_TRACKING) as f:
    tracking = json.load(f)

with open(BILL_PROGRESS) as f:
    progress = json.load(f)

with open(CACHE_FILE) as f:
    cache = json.load(f)

# Update tracking
tracking["last_run"] = "2026-06-04 - Member-sponsored bill pipeline (AR, AZ)"
tracking["bills_added"] = 60
tracking["total_cache"] = len(cache)
tracking["last_uncached_count"] = len(cache)

# Update progress - states done
done = set(progress["states_completed"])
for s in ["AR", "AZ"]:
    done.add(s)
progress["states_completed"] = sorted(done)
progress["last_run"] = "2026-06-04 - Processed AR+AZ member-sponsored bills"
progress["members_processed"] = 57
progress["bills_added"] = 60
progress["total_bills"] = len(cache)

# Next states to process
all_states = ["AK","AL","AR","AZ","CA","CO","CT","DE","FL","GA","HI","IA","ID",
              "IL","IN","KS","KY","LA","MA","MD","ME","MI","MN","MO","MS","MT",
              "NC","ND","NE","NH","NJ","NM","NV","NY","OH","OK","OR","PA","RI",
              "SC","SD","TN","TX","UT","VA","VT","WA","WI","WV","WY"]
remaining = [s for s in all_states if s not in done]
progress["next_states"] = remaining[:3]

# Count sponsor-linked entries
with_sponsor = sum(1 for v in cache.values() if isinstance(v, dict) and v.get("sponsor_name"))
no_sponsor = len(cache) - with_sponsor

tracking["sponsor_linked_entries"] = with_sponsor
tracking["no_sponsor_entries"] = no_sponsor

with open(STATE_TRACKING, "w") as f:
    json.dump(tracking, f, indent=2)

with open(BILL_PROGRESS, "w") as f:
    json.dump(progress, f, indent=2)

print(f"Tracking updated.")
print(f"States done: {progress['states_completed']}")
print(f"Next up: {progress['next_states']}")
print(f"Cache: {len(cache)} total, {with_sponsor} sponsor-linked, {no_sponsor} generic")

# Summary for delivery
result = {
    "states_processed": ["AR", "AZ"],
    "members_processed": 57,
    "new_sponsor_linked_bills": 60,
    "total_cache": len(cache),
    "total_sponsor_linked": with_sponsor,
    "next_states": remaining[:3],
    "commit": "0f12397 Add 60 member-sponsored bill pros/cons for AR and AZ (118th-119th Congress)",
    "notes": "First run of member-sponsored bill pipeline. 60 bills from AR House + AZ House/Senate added with titles, sponsor info, summaries, and pros/cons."
}
print(f"\nFINAL SUMMARY:")
print(json.dumps(result, indent=2))
