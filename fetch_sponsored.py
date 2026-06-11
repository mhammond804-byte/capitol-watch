#!/usr/bin/env python3
"""Fetch all sponsored bills for current members of 3 states."""
import json
import subprocess
import time

API_KEY = "xH3oHkvJab5BzhnVvJ5zXk3bHK5fPqHZ263Asebc"
BILL_CACHE_PATH = "/Users/michaelhammond/Desktop/capitol-watch/bill-analysis.json"

# Current members: bioguide -> name
MEMBERS = {
    "B001323": "Begich (AK-H)",
    "S001198": "Sullivan (AK-S)",
    "M001153": "Murkowski (AK-S)",
    "M001238": "McBride (DE-H)",
    "C001088": "Coons (DE-S)",
    "B001303": "Blunt Rochester (DE-S)",
    "F000482": "Fedorchak (ND-H)",
    "H001061": "Hoeven (ND-S)",
    "C001096": "Cramer (ND-S)",
}

# Load existing cache
with open(BILL_CACHE_PATH) as f:
    cache = json.load(f)

cached_keys = set(cache.keys())
print(f"Existing cache: {len(cached_keys)} bills")

def fetch_all_pages(url, max_congress=119, min_congress=118):
    """Fetch all pages of sponsored legislation for a member. Only 118+ congress.
    Stops early once we've passed older congresses (bills are returned newest-first)."""
    all_bills = []
    page_num = 0
    while url:
        page_num += 1
        if page_num > 50:  # Safety limit
            break
        print(f"  Page {page_num}: {url[:80]}...")
        r = subprocess.run(
            ["curl", "-s", "-H", f"X-Api-Key: {API_KEY}", url],
            capture_output=True, text=True, timeout=30
        )
        data = json.loads(r.stdout)
        items = data.get("sponsoredLegislation", [])
        
        if not items:
            break
            
        for item in items:
            c = item.get("congress")
            if c and c >= min_congress and c <= max_congress:
                all_bills.append(item)
        
        # Check if the LAST bill on this page is from an older congress than min_congress
        # If so, all remaining pages will be even older - stop early
        last_congress = items[-1].get("congress", max_congress)
        if last_congress < min_congress:
            print(f"  Stopping early - reached congress {last_congress} < {min_congress}")
            break
        
        pagination = data.get("pagination", {})
        url = pagination.get("next")
        if url:
            time.sleep(0.25)
    return all_bills

all_new_bills = {}  # key -> {title, summary_url, congress, type, number}

for bioguide, name in MEMBERS.items():
    print(f"\n--- {name} ({bioguide}) ---")
    url = f"https://api.congress.gov/v3/member/{bioguide}/sponsored-legislation?format=json&limit=20"
    bills = fetch_all_pages(url)
    print(f"  Total sponsored: {len(bills)}")
    
    for b in bills:
        if b.get("type") is None:
            continue
        congress = b["congress"]
        bill_type = b["type"].lower()
        number = b["number"]
        if not number or not bill_type:
            continue
        key = f"{congress}/{bill_type}/{number}"
        
        if key in cached_keys:
            continue
        
        if key not in all_new_bills:
            all_new_bills[key] = {
                "title": b["title"],
                "congress": congress,
                "type": bill_type,
                "number": number,
                "bill_url": b["url"],
                "sponsor_name": name,
                "introduced_date": b.get("introducedDate", ""),
                "policy_area": b.get("policyArea", {}).get("name"),
            }

print(f"\n=== Summary ===")
print(f"New uncached bills to process: {len(all_new_bills)}")
for key, info in sorted(all_new_bills.items()):
    print(f"  {key} | {info['sponsor_name']} | {info['title'][:80]}")

# Save the list for the next step
with open("/tmp/new_bills_to_process.json", "w") as f:
    json.dump(all_new_bills, f, indent=2)

print(f"\nSaved {len(all_new_bills)} new bills to /tmp/new_bills_to_process.json")
