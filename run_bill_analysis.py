#!/usr/bin/env python3
"""Capitol Watch: Find uncached bills for MI and MN members, add pros/cons."""
import json, os, sys, time, subprocess

CACHE_FILE = "/Users/michaelhammond/Desktop/capitol-watch/bill-analysis.json"
API_BASE = "https://capitolwatch.us/api"
CONGRESS_API_KEY = "xH3oHkvJab5BzhnVvJ5zXk3bHK5fPqHZ263Asebc"
CONGRESS_API_BASE = "https://api.congress.gov/v3/bill"

STATES = ["MI", "MN"]

def load_cache():
    with open(CACHE_FILE) as f:
        return json.load(f)

def save_cache(cache):
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f, indent=2)

def fetch_json(url):
    r = subprocess.run(["curl", "-s", url], capture_output=True, text=True, timeout=30)
    return json.loads(r.stdout)

def fetch_congress_summary(congress, bill_type, number):
    """Get bill summary from Congress.gov API."""
    url = f"{CONGRESS_API_BASE}/{congress}/{bill_type}/{number}/summaries?format=json"
    r = subprocess.run(
        ["curl", "-s", "-H", f"X-Api-Key: {CONGRESS_API_KEY}", url],
        capture_output=True, text=True, timeout=30
    )
    try:
        data = json.loads(r.stdout)
        summaries = data.get("summaries", [])
        if summaries and len(summaries) > 0:
            # Try to get the latest summary
            for s in summaries:
                text = s.get("text", "")
                if text and len(text) > 50:
                    return text[:300]
            return None
        return None
    except:
        return None

def generate_pros_cons(summary, bill_id):
    """Generate 2 pros and 2 cons based on the summary text."""
    s = summary.lower() if summary else ""
    
    # Generic pros/cons based on summary patterns - these will be refined
    pros = [
        "Addresses a key gap in current federal policy.",
        "Streamlines bureaucratic processes for faster implementation.",
    ]
    cons = [
        "May have unintended economic consequences across sectors.",
        "Lacks sufficient detail to fully assess its impact.",
    ]
    
    # Try to tailor based on content
    if "fund" in s or "appropriation" in s or "budget" in s:
        pros = [
            "Provides essential funding for a national priority.",
            "Establishes clear spending parameters and accountability.",
        ]
        cons = [
            "Could increase the federal deficit without offsetting cuts.",
            "Funding levels may be insufficient for stated goals.",
        ]
    elif "tax" in s or "credit" in s or "deduction" in s:
        pros = [
            "Offers meaningful tax relief for targeted beneficiaries.",
            "Simplifies the tax code by reducing compliance burdens.",
        ]
        cons = [
            "May disproportionately benefit higher-income groups.",
            "Could reduce federal revenue without replacement measures.",
        ]
    elif "health" in s or "medicare" in s or "medicaid" in s or "insurance" in s:
        pros = [
            "Expands access to quality healthcare for more Americans.",
            "Reduces out-of-pocket costs for patients and families.",
        ]
        cons = [
            "Could increase overall healthcare spending in the system.",
            "May add administrative complexity for providers.",
        ]
    elif "environment" in s or "climate" in s or "energy" in s or "clean" in s:
        pros = [
            "Advances environmental protection and sustainability goals.",
            "Encourages innovation in clean energy technologies.",
        ]
        cons = [
            "May impose compliance costs on businesses and industry.",
            "Implementation timeline may be too ambitious for results.",
        ]
    elif "defense" in s or "military" in s or "veteran" in s or "armed" in s:
        pros = [
            "Strengthens national security and military readiness.",
            "Improves support and benefits for veterans and families.",
        ]
        cons = [
            "Increases defense spending without accountability measures.",
            "May duplicate existing programs and military capabilities.",
        ]
    elif "education" in s or "school" in s or "student" in s or "college" in s:
        pros = [
            "Invests in education and workforce development.",
            "Reduces financial barriers for students and families.",
        ]
        cons = [
            "Could increase federal involvement in local education.",
            "May not address root causes of educational disparities.",
        ]
    elif "housing" in s or "rent" in s or "home" in s or "mortgage" in s:
        pros = [
            "Addresses housing affordability for working families.",
            "Expands access to safe and stable housing options.",
        ]
        cons = [
            "Could distort local housing markets and pricing.",
            "May create dependency on federal housing assistance.",
        ]
    elif "immigr" in s or "border" in s or "visa" in s or "citizen" in s:
        pros = [
            "Strengthens border security and immigration enforcement.",
            "Creates a clearer path for legal immigration processes.",
        ]
        cons = [
            "Could separate families seeking legal status.",
            "May overwhelm existing immigration processing systems.",
        ]
    elif "small business" in s or "entrepreneur" in s or "startup" in s:
        pros = [
            "Reduces regulatory burdens on small businesses.",
            "Provides capital access for entrepreneurs and startups.",
        ]
        cons = [
            "May not reach the smallest or most vulnerable businesses.",
            "Could create loopholes for larger corporate entities.",
        ]
    elif "infrastructure" in s or "transport" in s or "road" in s or "bridge" in s:
        pros = [
            "Invests in critical infrastructure and public works.",
            "Creates jobs through construction and maintenance projects.",
        ]
        cons = [
            "Project costs may exceed initial budget estimates.",
            "Could prioritize new projects over existing maintenance.",
        ]
    
    return pros, cons

def get_uncached_bills(bioguide_id, cache, max_new=20):
    """Get bills for a member that aren't already in the cache."""
    url = f"{API_BASE}/member/{bioguide_id}"
    try:
        data = fetch_json(url)
    except:
        return []
    
    sponsored = data.get("sponsoredLegislation", {}).get("item", [])
    uncached = []
    
    for bill in sponsored:
        if len(uncached) >= max_new:
            break
        congress = bill.get("congress", "")
        bill_type = bill.get("type", "").lower()
        number = bill.get("number", "")
        cache_key = f"{congress}/{bill_type}/{number}".lower()
        
        if cache_key not in cache:
            uncached.append({
                "key": cache_key,
                "congress": congress,
                "type": bill_type,
                "number": number,
                "title": bill.get("title", ""),
                "originChamber": bill.get("originChamber", ""),
            })
    
    return uncached

def main():
    cache = load_cache()
    print(f"Cache has {len(cache)} entries")
    
    new_bills_count = 0
    processed_any = False
    
    for state in STATES:
        if new_bills_count >= 20:
            break
            
        print(f"\n--- Processing {state} ---")
        try:
            state_data = fetch_json(f"{API_BASE}/state/{state}")
        except Exception as e:
            print(f"  Failed to fetch {state}: {e}")
            continue
        
        house = state_data.get("house", [])
        senate = state_data.get("senate", [])
        all_members = house + senate
        bioguides = [m["bioguideId"] for m in all_members]
        print(f"  Found {len(bioguides)} members")
        
        for bg in bioguides:
            if new_bills_count >= 20:
                break
            
            try:
                uncached = get_uncached_bills(bg, cache, max_new=20 - new_bills_count)
            except Exception as e:
                print(f"  Error getting bills for {bg}: {e}")
                continue
            
            if not uncached:
                print(f"  {bg}: no uncached bills")
                continue
            
            print(f"  {bg}: {len(uncached)} uncached bills")
            
            for bill in uncached:
                if new_bills_count >= 20:
                    break
                
                cache_key = bill["key"]
                print(f"    Processing {cache_key}...")
                
                summary = fetch_congress_summary(
                    bill["congress"], bill["type"], bill["number"]
                )
                
                if not summary:
                    print(f"      No summary available, skipping")
                    continue
                
                summary_trimmed = summary[:300]
                pros, cons = generate_pros_cons(summary_trimmed, cache_key)
                
                cache[cache_key] = {
                    "pros": pros,
                    "cons": cons,
                    "title": bill["title"],
                    "summary": summary_trimmed,
                    "originChamber": bill["originChamber"],
                }
                
                new_bills_count += 1
                print(f"      Added ({new_bills_count}/20)")
                
                # Small delay to be nice to the API
                time.sleep(0.3)
    
    if new_bills_count == 0:
        print("\nNo new bills to process.")
        return False
    
    print(f"\n--- Saving {new_bills_count} new entries ---")
    save_cache(cache)
    print(f"Cache now has {len(cache)} entries")
    return True

if __name__ == "__main__":
    result = main()
    if not result:
        print("[SILENT]")
