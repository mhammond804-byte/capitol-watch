#!/usr/bin/env python3
"""
Step 2: Fetch summaries for new bills, then step 3: generate pros/cons and merge.
Selects ~60 bills with meaningful titles, fetching summaries and generating pros/cons.
"""
import json, os, subprocess, time, sys

CONGRESS_API_KEY = "xH3oHkvJab5BzhnVvJ5zXk3bHK5fPqHZ263Asebc"
BILL_LIST_PATH = "/tmp/new_bills_to_process.json"
SUMMARY_PATH = "/tmp/bill_summaries.json"
CACHE_FILE = os.path.expanduser("~/Desktop/capitol-watch/bill-analysis.json")

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

# Load the new bills
with open(BILL_LIST_PATH) as f:
    all_new_bills = json.load(f)

print(f"Total new bills available: {len(all_new_bills)}")

# Select a focused batch: skip generic "To provide for a limitation" funding bills
# Prioritize bills with descriptive short titles
meaningful = {}
skimpy = {}
for key, info in all_new_bills.items():
    title = info.get("title", "")
    # Skip boilerplate funding limitation bills
    if "To provide for a limitation" in title or "To repeal" in title or "To amend" in title[:30]:
        skimpy[key] = info
    else:
        meaningful[key] = info

print(f"Meaningful titles: {len(meaningful)}")
print(f"Skimpy titles: {len(skimpy)}")

# Select ~60 bills total: prioritize from meaningful, fill rest from skimpy
selected = {}
# Pick from meaningful: one per sponsor first
sponsor_seen = {}
for key, info in sorted(meaningful.items()):
    sponsor = info.get("sponsor_name", "")
    if sponsor not in sponsor_seen:
        sponsor_seen[sponsor] = 0
    if sponsor_seen[sponsor] < 3:  # Max 3 per sponsor
        selected[key] = info
        sponsor_seen[sponsor] += 1
    if len(selected) >= 50:
        break

# If we need more, add from skimpy
if len(selected) < 50:
    for key, info in skimpy.items():
        if key not in selected:
            selected[key] = info
            if len(selected) >= 60:
                break

# But cap at 60
while len(selected) > 60:
    last_key = list(selected.keys())[-1]
    del selected[last_key]

print(f"\nSelected {len(selected)} bills for processing:")
for key in sorted(selected.keys()):
    b = selected[key]
    print(f"  {key} | {b['sponsor_name']} | {b['title'][:80]}")

# Save the selected batch
selected_path = "/tmp/selected_bills.json"
with open(selected_path, "w") as f:
    json.dump(selected, f, indent=2)

# === STEP 2: Fetch summaries ===
print(f"\n{'='*60}")
print("STEP 2: Fetching summaries from Congress.gov")
print(f"{'='*60}")

# Load existing summaries
all_summaries = {}
if os.path.exists(SUMMARY_PATH) and os.path.getsize(SUMMARY_PATH) > 0:
    with open(SUMMARY_PATH) as f:
        try:
            data = json.load(f)
            if isinstance(data, dict):
                all_summaries = data
                print(f"Loaded {len(all_summaries)} existing summaries")
        except:
            pass

bills_list = list(selected.items())
for i, (key, info) in enumerate(bills_list):
    if key in all_summaries:
        print(f"  [{i+1}/{len(bills_list)}] {key} - cached")
        continue
    
    congress = info["congress"]
    btype = info["type"]
    number = info["number"]
    
    url = f"https://api.congress.gov/v3/bill/{congress}/{btype}/{number}/summaries?format=json"
    data = fetch_json(url, headers={"X-Api-Key": CONGRESS_API_KEY})
    
    summary_text = ""
    if data:
        summaries = data.get("summaries", [])
        if summaries:
            best = max(summaries, key=lambda s: len(s.get("text", "")))
            summary_text = best.get("text", "")
            if len(summary_text) > 300:
                summary_text = summary_text[:297] + "..."
    
    all_summaries[key] = {
        "summary": summary_text,
        "title": info.get("title", ""),
        "sponsor_name": info.get("sponsor_name", ""),
        "sponsor_bioguide": info.get("sponsor_bioguide", ""),
        "sponsor_chamber": info.get("sponsor_chamber", ""),
        "sponsor_state": info.get("sponsor_state", ""),
        "introduced_date": info.get("introduced_date", ""),
        "policy_area": info.get("policy_area", ""),
        "congress": info.get("congress", ""),
        "type": info.get("type", ""),
        "number": info.get("number", ""),
    }
    
    if (i + 1) % 10 == 0:
        print(f"  Progress: {i+1}/{len(bills_list)}")
        with open(SUMMARY_PATH, "w") as f:
            json.dump(all_summaries, f, indent=2)
    
    time.sleep(0.25)

# Save all summaries
with open(SUMMARY_PATH, "w") as f:
    json.dump(all_summaries, f, indent=2)

with_summary = sum(1 for v in all_summaries.values() if v.get("summary"))
print(f"\nSummaries fetched: {with_summary}/{len(all_summaries)} with content")

# Output data for the next stage
output = {
    "bills_count": len(selected),
    "summaries_count": len(all_summaries),
    "with_content": with_summary,
    "summaries": all_summaries
}
print(f"\nDone. {len(all_summaries)} bills ready for pros/cons generation.")
with open("/tmp/ready_for_pros_cons.json", "w") as f:
    json.dump(output, f, indent=2, default=str)
print("Saved to /tmp/ready_for_pros_cons.json")
