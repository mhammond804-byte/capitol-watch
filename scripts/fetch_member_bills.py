#!/usr/bin/env python3
"""
Fetch state members and their sponsored bills for Capitol Watch.
Processes 2-3 unprocessed states per run, checking which bills are uncached,
then delegates batch analysis.
"""
import json, os, sys, time, urllib.request, urllib.error, urllib.parse
from urllib.request import urlopen

# === CONFIG ===
API_BASE = "https://capitolwatch.us/api"
CONGRESS_API = "https://api.congress.gov/v3"
CONGRESS_API_KEY = "xH3oHkvJab5BzhnVvJ5zXk3bHK5fPqHZ263Asebc"
OUTPUT_DIR = "/tmp/cw_members"
STATE_TRACK_FILE = "/tmp/cw_processed_states.json"
CACHE_FILE = os.path.expanduser("~/Desktop/capitol-watch/bill-analysis.json")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def fetch_json(url, timeout=30):
    r = urlopen(url, timeout=timeout)
    return json.loads(r.read())

def get_state_codes():
    data = fetch_json(f"{API_BASE}/states")
    return [s["code"] for s in data]

def load_processed_states():
    if os.path.exists(STATE_TRACK_FILE):
        with open(STATE_TRACK_FILE) as f:
            return set(json.load(f))
    return set()

def save_processed_states(states):
    with open(STATE_TRACK_FILE, "w") as f:
        json.dump(list(states), f)

def load_bill_cache():
    with open(CACHE_FILE) as f:
        return json.load(f)

def save_bill_cache(cache):
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=2)
    print(f"Saved {len(cache)} bills to cache")

def get_member_bills(bioguide_id):
    """Get sponsored bills for a member from capitolwatch.us API."""
    try:
        url = f"{API_BASE}/member/{bioguide_id}"
        data = fetch_json(url)
        # The member response may have 'sponsoredBills' or 'bills' key
        if isinstance(data, dict):
            # Try different possible field names
            for key in ["bills", "sponsoredBills", "sponsoredLegislation"]:
                if key in data:
                    return data[key]
            # Maybe the whole response is the bill list
            print(f"  Unknown response format for {bioguide_id}: keys={list(data.keys())}")
            return None
        elif isinstance(data, list):
            return data
    except Exception as e:
        print(f"  Error fetching member {bioguide_id}: {e}")
        return None

def make_cache_key(bill):
    """Build cache key: 'congress/type/number' lowercased."""
    congress = bill.get("congress", "")
    bill_type = bill.get("type", bill.get("billType", "")).lower()
    bill_number = bill.get("number", bill.get("billNumber", ""))
    if not congress and "number" in bill:
        # Try to extract from other fields
        pass
    if congress and bill_type and bill_number:
        return f"{congress}/{bill_type}/{bill_number}".lower()
    return None

def fetch_summary(congress, bill_type, bill_number):
    """Fetch summary from Congress.gov API."""
    try:
        url = f"{CONGRESS_API}/bill/{congress}/{bill_type}/{bill_number}/summaries?format=json"
        req = urllib.request.Request(url)
        req.add_header("X-Api-Key", CONGRESS_API_KEY)
        r = urlopen(req, timeout=30)
        data = json.loads(r.read())
        summaries = data.get("summaries", [])
        if summaries:
            # Get the latest/longest summary
            best = max(summaries, key=lambda s: len(s.get("text", "")))
            text = best.get("text", "")
            # Trim to 300 chars
            if len(text) > 300:
                text = text[:297] + "..."
            return text
        return ""
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None  # No summary available
        print(f"  HTTP {e.code} for {congress}/{bill_type}/{bill_number}")
        return None
    except Exception as e:
        print(f"  Error fetching summary {congress}/{bill_type}/{bill_number}: {e}")
        return None

def main():
    all_states = get_state_codes()
    print(f"All states ({len(all_states)}): {', '.join(all_states[:5])}...")

    processed = load_processed_states()
    print(f"Already processed: {processed}")

    # Pick next 2-3 unprocessed states
    unprocessed = sorted([s for s in all_states if s not in processed])
    print(f"Unprocessed: {unprocessed}")

    if not unprocessed:
        print("ALL 50 STATES DONE! Resetting for fresh pass.")
        processed = set()
        unprocessed = sorted(all_states)

    target_states = unprocessed[:2]  # 2 per run to keep time reasonable
    print(f"\nTargeting: {target_states}")

    # Load bill cache
    bill_cache = load_bill_cache()
    print(f"Existing cache: {len(bill_cache)} bills")

    new_bills = {}  # {cache_key: {info}}
    new_member_bills = {}  # {bioguide: [bill_keys]}
    all_member_count = 0
    bill_count = 0

    for state in target_states:
        print(f"\n{'='*50}")
        print(f"=== Processing {state} ===")
        print(f"{'='*50}")

        data = fetch_json(f"{API_BASE}/state/{state}")
        house = data.get("house", [])
        senate = data.get("senate", [])

        for member in house + senate:
            bid = member.get("bioguideId", "")
            name = member.get("name", "Unknown")
            chamber = "Senate" if member in senate else "House"
            district = member.get("district", "At-Large") if "district" in member else "At-Large"
            print(f"\n  {name} ({chamber}, {state}-{district}) [bioguide: {bid}]")

            bills = get_member_bills(bid)
            if not bills:
                print(f"    No bills data")
                continue

            if isinstance(bills, dict):
                bills = bills.get("bills", bills.get("sponsoredBills", bills.get("sponsoredLegislation", [bills])))
            if isinstance(bills, list):
                all_member_count += 1
                member_new = 0
                for bill in bills:
                    if isinstance(bill, dict):
                        cache_key = make_cache_key(bill)
                        if cache_key and cache_key not in bill_cache and cache_key not in new_bills:
                            # Extract minimal info
                            new_bills[cache_key] = {
                                "congress": bill.get("congress", ""),
                                "type": bill.get("type", bill.get("billType", "")),
                                "number": bill.get("number", bill.get("billNumber", "")),
                                "title": bill.get("title", bill.get("shortTitle", bill.get("billTitle", "")))[:200]
                            }
                            member_new += 1
                            bill_count += 1
                print(f"    Found {member_new} new uncached bills")
                if bid not in new_member_bills:
                    new_member_bills[bid] = {"name": name, "chamber": chamber, "state": state, "bills": []}
                new_member_bills[bid]["bills"] = [b for b in new_bills.keys()
                                                   if any(b.startswith(str(binfo.get("congress","")).lower() + "/")
                                                          for binfo in [new_bills[k] for k in new_bills])][:5]

            # Rate limit - small delay between members
            time.sleep(0.5)

    print(f"\n{'='*50}")
    print(f"SUMMARY: Found {len(new_bills)} new uncached bills from {all_member_count} members in {target_states}")
    print(f"{'='*50}")

    # Save output for next step
    output = {
        "target_states": target_states,
        "total_new_bills": len(new_bills),
        "total_members": all_member_count,
        "bills": new_bills,
        "members": new_member_bills
    }

    # Also save a list of bills that need summaries fetched
    bill_list_path = os.path.join(OUTPUT_DIR, "bills_to_analyze.json")
    with open(bill_list_path, "w") as f:
        json.dump(output, f, indent=2, default=str)

    print(f"\nSaved bill list to {bill_list_path}")
    print(json.dumps({"states": target_states, "new_bills_count": len(new_bills), "members_count": all_member_count}))

if __name__ == "__main__":
    main()
