#!/usr/bin/env python3
"""Find uncached bills for GA and HI members and generate pros/cons."""
import json
import urllib.request
import urllib.error
import os
import time
import re

CACHE_FILE = os.path.expanduser("~/Desktop/capitol-watch/bill-analysis.json")
STATE_TRACKER = os.path.expanduser("~/.hermes/logs/capitol_watch_states_done.json")
CONGRESS_API_KEY = "xH3oHkvJab5BzhnVvJ5zXk3bHK5fPqHZ263Asebc"
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"

def fetch_json(url, headers=None):
    """Fetch JSON from a URL."""
    req = urllib.request.Request(url)
    req.add_header("User-Agent", USER_AGENT)
    if headers:
        for k, v in headers.items():
            req.add_header(k, v)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        print(f"  ERROR fetching {url}: {e}")
        return None

def is_current_term(terms_item):
    """Check if a terms item indicates currently serving."""
    if not terms_item:
        return False
    end = terms_item.get("endYear")
    if not end:
        return True
    try:
        return int(end) >= 2025
    except (ValueError, TypeError):
        return False

def get_current_members(state_code):
    """Get bioguide IDs for current members of a state."""
    url = f"https://capitolwatch.us/api/state/{state_code}"
    data = fetch_json(url)
    if not data:
        return []
    
    current_bgs = []
    for chamber in ["house", "senate"]:
        for m in data.get(chamber, []):
            terms = m.get("terms", {}).get("item", [])
            is_current = any(is_current_term(t) for t in terms) if terms else False
            if is_current:
                bg = m.get("bioguideId", "")
                if bg:
                    current_bgs.append(bg)
    return current_bgs

def get_member_bills(bioguide):
    """Get sponsored bills for a member."""
    url = f"https://capitolwatch.us/api/member/{bioguide}"
    data = fetch_json(url)
    if not data:
        return []
    if isinstance(data, dict):
        return data.get("sponsored", [])
    return []

def make_cache_key(congress, bill_type, number):
    """Normalize a bill to its cache key."""
    t = bill_type.lower().strip()
    t_map = {"h": "hr", "hr": "hr", "hres": "hres", "hjres": "hjres", "hconres": "hconres",
             "s": "s", "sres": "sres", "sjres": "sjres", "sconres": "sconres",
             "house bill": "hr", "senate bill": "s", "house resolution": "hres",
             "senate resolution": "sres", "house joint resolution": "hjres",
             "senate joint resolution": "sjres",
             "house concurrent resolution": "hconres", "senate concurrent resolution": "sconres"}
    t = t_map.get(t, t)
    n = str(number).lower().strip()
    if n.startswith(t):
        n = n[len(t):]
    n = n.lstrip(" ")
    c = str(congress)
    return f"{c}/{t}/{n}"

def get_bill_summary(congress, bill_type, number):
    """Fetch bill summary from Congress.gov API."""
    url = f"https://api.congress.gov/v3/bill/{congress}/{bill_type}/{number}/summaries?format=json"
    data = fetch_json(url, {"X-Api-Key": CONGRESS_API_KEY})
    if not data:
        return None
    try:
        summaries = data.get("summaries", [])
        if summaries:
            text = summaries[0].get("text", "")
            if text and len(text.strip()) > 10:
                return text.strip()[:300]
    except:
        pass
    return None

def generate_pros_cons(bill_key, summary):
    """Generate 2 pros and 2 cons based on the summary."""
    if not summary:
        return None
    
    summary_lower = summary.lower()
    
    has_spending = any(w in summary_lower for w in ["fund", "appropriation", "grant", "spending", "appropriated", "authorization", "fiscal"])
    has_regulation = any(w in summary_lower for w in ["regulat", "compliance", "requirement", "mandate", "standard", "oversight", "restrict"])
    has_tax = any(w in summary_lower for w in ["tax", "revenue", "credit", "deduction", "internal revenue"])
    has_health = any(w in summary_lower for w in ["health", "medicare", "medicaid", "hospital", "patient", "disease", "treatment"])
    has_education = any(w in summary_lower for w in ["education", "school", "student", "teacher", "college", "curriculum"])
    has_energy = any(w in summary_lower for w in ["energy", "renewable", "clean energy", "carbon", "emission", "climate"])
    has_defense = any(w in summary_lower for w in ["defense", "military", "veteran", "armed force", "national security", "intelligence", "weapon"])
    has_immigration = any(w in summary_lower for w in ["immigr", "visa", "border", "citizen", "alien", "asylum", "refugee"])
    has_tech = any(w in summary_lower for w in ["technology", "digital", "cyber", "data", "internet", "artificial intelligence", "computer", "broadband"])
    has_environment = any(w in summary_lower for w in ["environment", "conservation", "wildlife", "pollution", "water", "forest", "park", "natural resource"])
    has_housing = any(w in summary_lower for w in ["housing", "rent", "mortgage", "homeless", "affordable housing"])
    has_transport = any(w in summary_lower for w in ["transport", "highway", "road", "bridge", "transit", "infrastructure"])
    has_trade = any(w in summary_lower for w in ["trade", "tariff", "import", "export", "commerce", "international"])
    has_crime = any(w in summary_lower for w in ["crime", "criminal", "enforcement", "penalty", "offense", "sentence", "prison", "drug"])
    has_agriculture = any(w in summary_lower for w in ["agriculture", "farm", "crop", "food", "rural", "livestock", "fishery"])
    has_labor = any(w in summary_lower for w in ["labor", "worker", "employment", "wage", "minimum wage", "union", "workplace"])
    has_small_business = any(w in summary_lower for w in ["small business", "small and medium", "startup", "entrepreneur"])
    has_benefits = any(w in summary_lower for w in ["benefit", "insurance", "assistance", "program", "service", "social security"])
    has_study = any(w in summary_lower for w in ["study", "report", "pilot", "demonstration", "feasibility", "assessment", "evaluation"])
    has_government = any(w in summary_lower for w in ["government", "federal", "agency", "department", "administration", "office", "bureau", "commission"])
    has_veterans = any(w in summary_lower for w in ["veteran", "va ", "veterans"])
    has_congress_ops = any(w in summary_lower for w in ["congress", "senate", "house of representatives", "committee", "resolution", "rule", "session"])
    
    # Build pros based on detected themes
    pros = []
    if has_veterans:
        pros.append("Improves benefits and services for military veterans.")
        pros.append("Honors commitments made to those who served.")
    elif has_health:
        pros.append("Improves access to healthcare services for Americans.")
        pros.append("Supports better health outcomes and patient care.")
    elif has_education:
        pros.append("Strengthens educational opportunities for students.")
        pros.append("Invests in workforce development and training.")
    elif has_energy:
        pros.append("Advances clean energy innovation and adoption.")
        pros.append("Reduces dependence on fossil fuel sources.")
    elif has_defense:
        pros.append("Strengthens national security and defense readiness.")
        pros.append("Supports military personnel and veterans.")
    elif has_immigration:
        pros.append("Reforms immigration system for greater efficiency.")
        pros.append("Addresses border security and immigration enforcement.")
    elif has_tech:
        pros.append("Promotes technological innovation and competitiveness.")
        pros.append("Enhances digital infrastructure and cybersecurity.")
    elif has_environment:
        pros.append("Protects natural resources and wildlife habitats.")
        pros.append("Promotes environmental conservation and sustainability.")
    elif has_housing:
        pros.append("Improves access to affordable housing options.")
        pros.append("Addresses homelessness and housing instability.")
    elif has_transport:
        pros.append("Invests in critical transportation infrastructure.")
        pros.append("Improves safety and efficiency of transit systems.")
    elif has_trade:
        pros.append("Expands market access for American businesses.")
        pros.append("Strengthens trade relationships with key partners.")
    elif has_crime:
        pros.append("Enhances public safety and law enforcement tools.")
        pros.append("Provides stronger penalties for criminal offenses.")
    elif has_agriculture:
        pros.append("Supports American farmers and agricultural producers.")
        pros.append("Promotes food security and rural development.")
    elif has_labor:
        pros.append("Protects worker rights and improves labor conditions.")
        pros.append("Strengthens workplace safety and fair wages.")
    elif has_small_business:
        pros.append("Helps small businesses grow and create jobs.")
        pros.append("Reduces regulatory burdens on entrepreneurs.")
    elif has_benefits:
        pros.append("Expands access to essential benefits and services.")
        pros.append("Provides assistance to vulnerable populations.")
    elif has_study:
        pros.append("Provides data-driven insights for policy decisions.")
        pros.append("Evaluates program effectiveness before expansion.")
    elif has_spending:
        pros.append("Directs funding toward important national priorities.")
        pros.append("Provides resources for essential government programs.")
    elif has_regulation:
        pros.append("Establishes clear standards for industry compliance.")
        pros.append("Increases accountability and consumer protections.")
    elif has_tax:
        pros.append("Reduces tax burden on families and businesses.")
        pros.append("Simplifies the tax code for easier compliance.")
    elif has_congress_ops:
        pros.append("Improves the efficiency of congressional operations.")
        pros.append("Enhances transparency and accountability in government.")
    elif has_government:
        pros.append("Improves efficiency of federal government operations.")
        pros.append("Enhances accountability in government programs.")
    else:
        pros.append("Addresses an important policy need in this area.")
        pros.append("Provides a framework for federal action and oversight.")
    
    # Build cons based on detected themes
    cons = []
    if has_spending:
        cons.append("Increases federal spending and the national deficit.")
        cons.append("May lead to higher taxes to fund new programs.")
    elif has_regulation:
        cons.append("Adds regulatory burdens on businesses and industry.")
        cons.append("May increase compliance costs for small businesses.")
    elif has_tax:
        cons.append("Could reduce federal revenue for other programs.")
        cons.append("May disproportionately benefit certain groups.")
    elif has_health:
        cons.append("May increase government involvement in healthcare.")
        cons.append("Could raise healthcare costs for taxpayers.")
    elif has_education:
        cons.append("Expands federal role in local education policy.")
        cons.append("May create unfunded mandates for school districts.")
    elif has_energy:
        cons.append("Could raise energy costs for consumers and businesses.")
        cons.append("May impose burdensome regulations on energy producers.")
    elif has_defense:
        cons.append("Increases military spending and defense budget.")
        cons.append("May expand overseas military commitments.")
    elif has_immigration:
        cons.append("Could face implementation and enforcement challenges.")
        cons.append("May have unintended effects on labor markets.")
    elif has_tech:
        cons.append("May raise privacy and civil liberty concerns.")
        cons.append("Could create new regulatory burdens on tech firms.")
    elif has_environment:
        cons.append("May impose restrictions on land use and development.")
        cons.append("Could increase costs for businesses and consumers.")
    elif has_housing:
        cons.append("May distort local housing markets and prices.")
        cons.append("Could create dependency on federal housing programs.")
    elif has_transport:
        cons.append("May lead to cost overruns on infrastructure projects.")
        cons.append("Could increase the federal transportation budget.")
    elif has_trade:
        cons.append("May expose domestic industries to foreign competition.")
        cons.append("Could have complex and uneven economic effects.")
    elif has_crime:
        cons.append("May lead to overcriminalization or mass incarceration.")
        cons.append("Could expand federal law enforcement authority.")
    elif has_agriculture:
        cons.append("May distort agricultural markets with subsidies.")
        cons.append("Could increase federal farm program spending.")
    elif has_labor:
        cons.append("May increase costs and burdens on employers.")
        cons.append("Could reduce workplace flexibility and innovation.")
    elif has_small_business:
        cons.append("May not address root causes of business challenges.")
        cons.append("Could create uneven competitive advantages.")
    elif has_benefits:
        cons.append("Increases long-term entitlement program obligations.")
        cons.append("May create dependency on federal assistance programs.")
    elif has_study:
        cons.append("Delays action while awaiting study results.")
        cons.append("May lead to inconclusive or conflicting findings.")
    elif has_congress_ops:
        cons.append("May prioritize procedural matters over public needs.")
        cons.append("Could be used to delay or obstruct other legislation.")
    elif has_government:
        cons.append("May expand the size of the federal bureaucracy.")
        cons.append("Could create inefficiencies in government operations.")
    else:
        cons.append("May have unintended economic consequences across sectors.")
        cons.append("Lacks sufficient detail to fully assess its impact.")
    
    def trunc(s):
        return s[:117] + "..." if len(s) > 120 else s
    
    return {
        "pros": [trunc(p) for p in pros[:2]],
        "cons": [trunc(c) for c in cons[:2]]
    }

def main():
    # Load cache
    cache = {}
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE) as f:
            cache = json.load(f)
    
    print(f"Cache has {len(cache)} entries")
    
    # Load state tracker
    done_states = []
    if os.path.exists(STATE_TRACKER):
        with open(STATE_TRACKER) as f:
            tracker = json.load(f)
            done_states = tracker.get("states", [])
    
    # All states alphabetically
    all_states = ["AK", "AL", "AR", "AZ", "CA", "CO", "CT", "DC", "DE", "FL", 
                  "GA", "HI", "IA", "ID", "IL", "IN", "KS", "KY", "LA", "MA", 
                  "MD", "ME", "MI", "MN", "MO", "MS", "MT", "NC", "ND", "NE", 
                  "NH", "NJ", "NM", "NV", "NY", "OH", "OK", "OR", "PA", "RI", 
                  "SC", "SD", "TN", "TX", "UT", "VA", "VT", "WA", "WI", "WV", "WY"]
    
    remaining = [s for s in all_states if s not in done_states]
    if not remaining:
        print("All states processed. Nothing new to do.")
        return
    
    states_to_process = remaining[:2]
    print(f"States to process: {states_to_process}")
    
    total_new = 0
    total_failed = 0
    
    for state_code in states_to_process:
        print(f"\n=== Processing {state_code} ===")
        
        # Get current member bioguide IDs (filters by current term)
        bioguides = get_current_members(state_code)
        print(f"  Found {len(bioguides)} current members for {state_code}: {bioguides}")
        
        if not bioguides:
            print(f"  No current members found, skipping")
            continue
        
        # For each member, get their sponsored bills
        uncached_bills = {}  # key -> {congress, type, number, summary}
        
        for bg in bioguides:
            if total_new >= 20:
                break
            print(f"  Fetching bills for member {bg}...")
            bills = get_member_bills(bg)
            print(f"    Found {len(bills)} sponsored bills")
            
            for bill in bills:
                if total_new >= 20:
                    break
                
                congress = bill.get("congress", "")
                bill_type = bill.get("type", "")
                number = bill.get("number", "")
                
                if not congress or not bill_type or not number:
                    continue
                
                key = make_cache_key(congress, bill_type, number)
                
                # Skip if already in cache
                if key in cache or key in uncached_bills:
                    continue
                
                # Skip placeholder/empty keys
                if key in ["///", ""]:
                    continue
                
                # Fetch summary
                print(f"    Fetching summary for {key}...")
                summary = get_bill_summary(congress, bill_type, number)
                if not summary:
                    print(f"      No summary available, skipping")
                    total_failed += 1
                    continue
                
                uncached_bills[key] = {
                    "congress": str(congress),
                    "type": str(bill_type),
                    "number": str(number),
                    "summary": summary
                }
                total_new += 1
                print(f"      Got summary ({len(summary)} chars) — {total_new}/20")
                time.sleep(0.3)  # Rate limit
            
            if total_new >= 20:
                break
        
        if total_new >= 20:
            break
    
    if total_new == 0:
        print("\nNo new uncached bills found with available summaries.")
        # Still update the tracker
        os.makedirs(os.path.dirname(STATE_TRACKER), exist_ok=True)
        tracker_data = {"states": done_states + states_to_process, "timestamp": "2026-06-09", "bills_added": 0, "cache_now": len(cache)}
        with open(STATE_TRACKER, 'w') as f:
            json.dump(tracker_data, f, indent=2)
        print(f"Updated state tracker: {tracker_data}")
        return
    
    # Generate pros/cons and add to cache
    print(f"\n=== Generating pros/cons for {total_new} bills ===")
    
    for key, info in uncached_bills.items():
        analysis = generate_pros_cons(key, info["summary"])
        if analysis:
            cache[key] = {
                "pros": analysis["pros"],
                "cons": analysis["cons"]
            }
            print(f"  Added {key}: pro1={analysis['pros'][0][:40]}...")
        else:
            total_failed += 1
            print(f"  Failed to generate for {key}")
    
    # Write cache
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f, indent=2)
    print(f"\nCache now has {len(cache)} entries (+{total_new})")
    
    # Update state tracker
    tracker_data = {
        "states": done_states + states_to_process,
        "timestamp": "2026-06-09",
        "bills_added": total_new,
        "note": f"Scanned {states_to_process[0]} + {states_to_process[1]} members. {total_new} new bills added.",
        "failed_count": total_failed,
        "cache_now": len(cache)
    }
    with open(STATE_TRACKER, 'w') as f:
        json.dump(tracker_data, f, indent=2)
    print(f"Updated state tracker")

if __name__ == "__main__":
    main()
