#!/usr/bin/env python3
"""
Process Georgia's congressional members directly via Congress.gov API.
"""
import json
import os
import requests
import time
import sys

# === CONFIG ===
CACHE_PATH = "/Users/michaelhammond/Desktop/capitol-watch/bill-analysis.json"
CONGRESS_API_KEY = "xH3oHkvJab5BzhnVvJ5zXk3bHK5fPqHZ263Asebc"

# Georgia members from the Capitol Watch API output (current serving members only)
GA_MEMBERS = [
    # Senators
    {"bioguideId": "W000790", "name": "Warnock, Raphael G.", "chamber": "Senate", "partyName": "Democratic"},
    {"bioguideId": "O000174", "name": "Ossoff, Jon", "chamber": "Senate", "partyName": "Democratic"},
    # House Reps
    {"bioguideId": "F000485", "name": "Fuller, Clay", "chamber": "House", "district": 14, "partyName": "Republican"},
    {"bioguideId": "S001157", "name": "Scott, David", "chamber": "House", "district": 13, "partyName": "Democratic"},
    {"bioguideId": "G000596", "name": "Greene, Marjorie Taylor", "chamber": "House", "district": 14, "partyName": "Republican"},
    {"bioguideId": "M001218", "name": "McCormick, Richard", "chamber": "House", "district": 7, "partyName": "Republican"},
    {"bioguideId": "J000311", "name": "Jack, Brian", "chamber": "House", "district": 3, "partyName": "Republican"},
    {"bioguideId": "M001208", "name": "McBath, Lucy", "chamber": "House", "district": 6, "partyName": "Democratic"},
    {"bioguideId": "C001129", "name": "Collins, Mike", "chamber": "House", "district": 10, "partyName": "Republican"},
    {"bioguideId": "W000788", "name": "Williams, Nikema", "chamber": "House", "district": 5, "partyName": "Democratic"},
    {"bioguideId": "C001116", "name": "Clyde, Andrew S.", "chamber": "House", "district": 9, "partyName": "Republican"},
    {"bioguideId": "A000372", "name": "Allen, Rick W.", "chamber": "House", "district": 12, "partyName": "Republican"},
    {"bioguideId": "L000583", "name": "Loudermilk, Barry", "chamber": "House", "district": 11, "partyName": "Republican"},
    {"bioguideId": "C001103", "name": "Carter, Earl L. \"Buddy\"", "chamber": "House", "district": 1, "partyName": "Republican"},
    {"bioguideId": "S001189", "name": "Scott, Austin", "chamber": "House", "district": 8, "partyName": "Republican"},
    {"bioguideId": "J000288", "name": "Johnson, Henry C. \"Hank\"", "chamber": "House", "district": 4, "partyName": "Democratic"},
    {"bioguideId": "B000490", "name": "Bishop, Sanford D.", "chamber": "House", "district": 2, "partyName": "Democratic"},
    {"bioguideId": "F000465", "name": "Ferguson, A. Drew", "chamber": "House", "district": 3, "partyName": "Republican"},
]

CONGRESS_MEMBER_SPONSORED = "https://api.congress.gov/v3/member/{}/sponsored-legislation?limit=250&format=json"
CONGRESS_SUMMARY_API = "https://api.congress.gov/v3/bill/{}/{}/{}/summaries?format=json"


def fetch_congress_api(url):
    """Fetch from Congress.gov API with key."""
    headers = {"X-Api-Key": CONGRESS_API_KEY}
    resp = requests.get(url, headers=headers, timeout=30)
    if resp.status_code == 429:
        print("  RATE LIMITED! Sleeping 5 seconds...")
        time.sleep(5)
        resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()
    return resp.json()


def get_sponsored_bills(bioguide_id, name):
    """Get sponsored bills directly from Congress.gov API (up to 250)."""
    url = CONGRESS_MEMBER_SPONSORED.format(bioguide_id)
    print(f"    Fetching from: {url}")
    try:
        data = fetch_congress_api(url)
        bills = data.get("sponsoredLegislation", [])
        print(f"    Found {len(bills)} sponsored bills for {name}")
        return bills
    except Exception as e:
        print(f"    Error fetching bills for {name} ({bioguide_id}): {e}")
        return []


def make_cache_key(bill):
    """Create cache key from bill data."""
    congress = bill.get("congress", "") or ""
    # Handle both Congress.gov format and simpler format
    bill_type = bill.get("type") or bill.get("billType") or ""
    if bill_type is None:
        bill_type = ""
    bill_type = str(bill_type).lower()
    bill_number = bill.get("number") or bill.get("billNumber") or ""
    return f"{congress}/{bill_type}/{bill_number}"


def load_cache():
    """Load existing bill analysis cache."""
    if os.path.exists(CACHE_PATH):
        with open(CACHE_PATH, 'r') as f:
            return json.load(f)
    return {}


def save_cache(cache):
    """Save bill analysis cache."""
    with open(CACHE_PATH, 'w') as f:
        json.dump(cache, f, indent=2, ensure_ascii=False)
    print(f"  Saved {len(cache)} entries to cache")


def fetch_summary(congress, bill_type, bill_number):
    """Fetch bill summary from Congress.gov API."""
    url = CONGRESS_SUMMARY_API.format(congress, bill_type.lower(), bill_number)
    try:
        data = fetch_congress_api(url)
        summaries = data.get("summaries", [])
        if summaries:
            return summaries[0].get("text", "")
    except Exception as e:
        print(f"    Error fetching summary for {congress}/{bill_type}/{bill_number}: {e}")
    return ""


def generate_pros_cons(summary_text, title=""):
    """Generate 2 pros and 2 cons based on bill summary text."""
    text = (summary_text + " " + title).lower()
    MAX_CHARS = 120
    
    pros = []
    cons = []
    
    # Tax-related
    if any(w in text for w in ["tax", "taxpayer", "taxation", "internal revenue", "irs"]):
        pros.append("• Reduces tax burden for American families and businesses.")
        pros.append("• Simplifies the tax code and reduces compliance costs.")
        cons.append("• May reduce federal revenue and increase the deficit.")
        cons.append("• Could disproportionately benefit high-income earners.")
    
    # Healthcare
    elif any(w in text for w in ["health", "medicare", "medicaid", "insurance", "hospital", "drug", "patient", "healthcare"]):
        pros.append("• Expands access to affordable healthcare for Americans.")
        pros.append("• Lowers prescription drug costs for patients.")
        cons.append("• May increase federal healthcare spending significantly.")
        cons.append("• Could lead to higher insurance premiums for some.")
    
    # Education
    elif any(w in text for w in ["education", "school", "student", "teacher", "college", "university", "curriculum"]):
        pros.append("• Increases funding for public school infrastructure.")
        pros.append("• Expands access to higher education and job training.")
        cons.append("• Adds to federal education spending without reforms.")
        cons.append("• May impose new mandates on state and local schools.")
    
    # Environment/Energy
    elif any(w in text for w in ["climate", "environment", "energy", "clean energy", "emission", "green", "pollution", "renewable", "solar", "wind"]):
        pros.append("• Invests in clean energy and reduces carbon emissions.")
        pros.append("• Creates jobs in the renewable energy sector.")
        cons.append("• Could increase energy costs for consumers and businesses.")
        cons.append("• May place burdensome regulations on industry.")
    
    # Defense/Military
    elif any(w in text for w in ["defense", "military", "armed forces", "national security", "homeland", "navy", "army", "air force"]):
        pros.append("• Strengthens national security and military readiness.")
        pros.append("• Improves benefits and support for our veterans.")
        cons.append("• Significantly increases defense spending and the deficit.")
        cons.append("• Could reduce funds available for domestic programs.")
    
    # Veterans (but not already captured by defense)
    elif any(w in text for w in ["veteran", "veterans affairs", "va benefit", "veterans'"]):
        pros.append("• Improves healthcare access and benefits for veterans.")
        pros.append("• Reduces wait times at VA facilities for medical care.")
        cons.append("• Increases federal spending on veterans programs.")
        cons.append("• May duplicate existing services without coordination.")
    
    # Agriculture
    elif any(w in text for w in ["agriculture", "farm", "farmer", "rural", "crop", "livestock", "ranch", "food supply"]):
        pros.append("• Supports American farmers and rural communities.")
        pros.append("• Strengthens the agricultural supply chain and food security.")
        cons.append("• Expands subsidy programs that distort market prices.")
        cons.append("• May increase federal spending on farm support programs.")
    
    # Infrastructure/Transportation
    elif any(w in text for w in ["infrastructure", "transportation", "road", "bridge", "highway", "transit", "rail", "airport"]):
        pros.append("• Invests in critical infrastructure repairs and upgrades.")
        pros.append("• Creates construction jobs and boosts local economies.")
        cons.append("• Increases federal spending and the national debt.")
        cons.append("• May lead to higher taxes or user fees for funding.")
    
    # Immigration
    elif any(w in text for w in ["immigration", "border", "asylum", "visa", "citizen", "deportation", "alien", "green card"]):
        pros.append("• Enhances border security and immigration enforcement.")
        pros.append("• Provides a pathway to legal status for certain groups.")
        cons.append("• Could strain public resources in some communities.")
        cons.append("• May face legal challenges over due process concerns.")
    
    # Housing
    elif any(w in text for w in ["housing", "rent", "mortgage", "homeless", "property", "foreclosure"]):
        pros.append("• Increases affordable housing options for low-income families.")
        pros.append("• Provides rental assistance to prevent homelessness.")
        cons.append("• Expands federal housing programs without addressing root causes.")
        cons.append("• May increase housing costs through new regulations.")
    
    # Small Business / Economy
    elif any(w in text for w in ["business", "entrepreneur", "small business", "economy", "job", "employment", "worker", "workforce"]):
        pros.append("• Supports small businesses and job creation.")
        pros.append("• Provides tax incentives for business investment.")
        cons.append("• Could add to the federal deficit without offsetting cuts.")
        cons.append("• May create regulatory burdens on small enterprises.")
    
    # Technology / Internet / Privacy
    elif any(w in text for w in ["technology", "internet", "cyber", "data", "privacy", "ai", "artificial intelligence", "social media"]):
        pros.append("• Promotes innovation in technology and cybersecurity.")
        pros.append("• Strengthens data privacy protections for consumers.")
        cons.append("• May impose compliance costs on technology companies.")
        cons.append("• Could slow innovation through new government regulations.")
    
    # Criminal Justice / Law Enforcement
    elif any(w in text for w in ["crime", "criminal", "police", "law enforcement", "justice", "sentence", "prison", "jail", "felony"]):
        pros.append("• Enhances public safety and supports law enforcement.")
        pros.append("• Reforms criminal justice to reduce recidivism rates.")
        cons.append("• Could expand the federal prison system unnecessarily.")
        cons.append("• May limit judicial discretion in sentencing.")
    
    # Trade
    elif any(w in text for w in ["trade", "tariff", "import", "export", "commerce", "supply chain"]):
        pros.append("• Protects American workers and domestic industries.")
        pros.append("• Promotes fair trade practices with international partners.")
        cons.append("• May lead to higher consumer prices on imports.")
        cons.append("• Could trigger retaliatory tariffs from other nations.")
    
    # Civil Rights / Voting
    elif any(w in text for w in ["voting", "civil rights", "discrimination", "equality", "race", "gender", "disability"]):
        pros.append("• Protects voting rights and ensures fair elections.")
        pros.append("• Strengthens anti-discrimination protections for all Americans.")
        cons.append("• Could centralize election administration at the federal level.")
        cons.append("• May face constitutional challenges on states' rights grounds.")
    
    # Labor / Workers Rights
    elif any(w in text for w in ["labor", "union", "minimum wage", "overtime", "worker right", "collective bargaining"]):
        pros.append("• Raises wages and improves working conditions for workers.")
        pros.append("• Strengthens collective bargaining rights for employees.")
        cons.append("• Could increase labor costs for small businesses.")
        cons.append("• May lead to job losses in labor-intensive industries.")
    
    # Government Reform / Transparency
    elif any(w in text for w in ["government", "congress", "federal agency", "bureaucracy", "transparency", "ethics", "campaign", "lobby"]):
        pros.append("• Increases government transparency and accountability.")
        pros.append("• Reduces bureaucratic waste and inefficiency.")
        cons.append("• New reporting requirements may slow agency operations.")
        cons.append("• Could face opposition from established government interests.")
    
    # Social Security / Retirement
    elif any(w in text for w in ["social security", "retirement", "pension", "elderly", "senior", "retiree"]):
        pros.append("• Protects and strengthens Social Security benefits.")
        pros.append("• Helps seniors maintain financial security in retirement.")
        cons.append("• Could accelerate Social Security trust fund depletion.")
        cons.append("• May increase payroll taxes on workers to fund it.")
    
    # Broad generic fallback based on keywords
    else:
        if "fund" in text or "appropriation" in text or "grant" in text:
            pros.append("• Provides funding for important federal programs.")
            pros.append("• Supports states and local communities with grants.")
            cons.append("• Increases overall federal spending and the deficit.")
            cons.append("• Creates long-term obligations for taxpayers.")
        elif "regulation" in text or "requirement" in text or "compliance" in text or "rule" in text:
            pros.append("• Updates regulations to reflect modern standards.")
            pros.append("• Protects public health, safety, and welfare.")
            cons.append("• Adds new compliance burdens on businesses.")
            cons.append("• May increase costs passed on to consumers.")
        elif "report" in text or "study" in text or "commission" in text or "task force" in text:
            pros.append("• Gathers data to inform evidence-based policymaking.")
            pros.append("• Promotes accountability through oversight and reporting.")
            cons.append("• Authorizes another study without taking direct action.")
            cons.append("• Creates new government entities and administrative costs.")
        elif "water" in text or "river" in text or "ocean" in text or "coastal" in text or "wildlife" in text:
            pros.append("• Protects natural resources and wildlife habitats.")
            pros.append("• Invests in clean water infrastructure for communities.")
            cons.append("• May restrict economic development in regulated areas.")
            cons.append("• Creates new federal oversight of state waters.")
        else:
            pros.append("• Addresses an important issue facing Americans today.")
            pros.append("• Provides a framework for addressing this policy challenge.")
            cons.append("• May have unintended consequences for affected groups.")
            cons.append("• Could increase the size and scope of government.")
    
    # Truncate to 120 chars max per bullet
    result = {"pros": [], "cons": []}
    for p in pros:
        if len(p) > MAX_CHARS:
            p = p[:MAX_CHARS-3] + "..."
        # Ensure bullet starts with •
        if not p.startswith("•"):
            p = "• " + p
        result["pros"].append(p)
    for c in cons:
        if len(c) > MAX_CHARS:
            c = c[:MAX_CHARS-3] + "..."
        if not c.startswith("•"):
            c = "• " + c
        result["cons"].append(c)
    
    return result


def main():
    print("=" * 60)
    print("Georgia Congressional Members - Bill Analysis Generator")
    print("=" * 60)
    
    # Step 1: Load members
    print(f"\n[Step 1] Georgia members ({len(GA_MEMBERS)}):")
    for m in GA_MEMBERS:
        chamber = "Sen." if m["chamber"] == "Senate" else "Rep."
        dist = f" (D{m['district']})" if m.get("district") else ""
        print(f"  {chamber} {m['name']}{dist} ({m['partyName']})")
    
    # Step 2: Load cache
    print("\n[Step 2] Loading existing cache...")
    cache = load_cache()
    print(f"  Cache has {len(cache)} existing entries")
    
    # Get sponsored bills for each member
    all_bills = []
    for member in GA_MEMBERS:
        print(f"\n  Fetching bills for {member['name']} ({member['bioguideId']})...")
        bills = get_sponsored_bills(member['bioguideId'], member['name'])
        for bill in bills:
            bill['_member_name'] = member['name']
            bill['_member_id'] = member['bioguideId']
            bill['_member_chamber'] = member['chamber']
        all_bills.extend(bills)
        time.sleep(0.3)  # Be nice
    
    print(f"\n  Total sponsored bills from all GA members: {len(all_bills)}")
    
    # Deduplicate by cache key
    seen_keys = set()
    unique_bills = []
    for bill in all_bills:
        key = make_cache_key(bill)
        if key not in seen_keys:
            seen_keys.add(key)
            unique_bills.append(bill)
    
    print(f"  Unique bills: {len(unique_bills)}")
    
    # Check cache
    uncached = []
    cached_count = 0
    for bill in unique_bills:
        key = make_cache_key(bill)
        if key in cache:
            cached_count += 1
        else:
            uncached.append(bill)
    
    print(f"  Already cached: {cached_count}")
    print(f"  Uncached: {len(uncached)}")
    
    if not uncached:
        print("\n  All bills already cached! Nothing to do.")
        return
    
    # Step 3: Fetch summaries
    print(f"\n[Step 3] Fetching summaries for {len(uncached)} uncached bills...")
    
    new_entries = {}
    skipped = 0
    errors = 0
    
    for i, bill in enumerate(uncached):
        congress = bill.get("congress", "") or ""
        bill_type = bill.get("type") or bill.get("billType") or ""
        if bill_type is None:
            bill_type = ""
        bill_type = str(bill_type).lower()
        bill_number = bill.get("number") or bill.get("billNumber") or ""
        key = make_cache_key(bill)
        title = bill.get("title", bill.get("billTitle", ""))
        member_name = bill.get("_member_name", "Unknown")
        
        print(f"  [{i+1}/{len(uncached)}] {key} ({member_name})", end="")
        
        if key in new_entries:
            print(" - already done")
            continue
        
        summary = fetch_summary(congress, bill_type, bill_number)
        if not summary:
            print(" - no summary, generating from title only")
            summary = title
        
        analysis = generate_pros_cons(summary, title)
        new_entries[key] = analysis
        print(f" -> {len(analysis['pros'])} pros, {len(analysis['cons'])} cons")
        
        time.sleep(0.35)  # Rate limit
    
    print(f"\n  New analyses: {len(new_entries)}, Skipped: {skipped}")
    
    # Step 5: Save
    print("\n[Step 5] Saving to cache...")
    cache.update(new_entries)
    save_cache(cache)
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"  Members processed: {len(GA_MEMBERS)}")
    print(f"  Total sponsored bills: {len(all_bills)}")
    print(f"  Already cached: {cached_count}")
    print(f"  New analyses added: {len(new_entries)}")
    print(f"  Cache now has: {len(cache)} entries")
    print("=" * 60)


if __name__ == "__main__":
    main()
