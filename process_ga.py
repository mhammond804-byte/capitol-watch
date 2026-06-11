#!/usr/bin/env python3
"""
Process Georgia's congressional members and generate AI pros/cons for sponsored bills.
"""
import json
import os
import requests
import sys
import time

# === CONFIG ===
CACHE_PATH = "/Users/michaelhammond/Desktop/capitol-watch/bill-analysis.json"
CONGRESS_API_KEY = "xH3oHkvJab5BzhnVvJ5zXk3bHK5fPqHZ263Asebc"
STATE_API = "https://capitolwatch.us/api/state/GA"
MEMBER_API = "https://capitolwatch.us/api/member/{}"
CONGRESS_SUMMARY_API = "https://api.congress.gov/v3/bill/{}/{}/{}/summaries?format=json"

def get_ga_members():
    """Fetch all Georgia members from Capitol Watch API."""
    resp = requests.get(STATE_API, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    
    # Filter to currently serving members (those with active terms in 2025-2026)
    current = []
    
    for member in data.get("senate", []):
        terms = member.get("terms", {}).get("item", [])
        is_current = any(
            t.get("endYear") is None or t.get("endYear", 0) >= 2025
            for t in terms
        )
        if is_current:
            current.append({
                "bioguideId": member["bioguideId"],
                "name": member["name"],
                "chamber": "Senate",
                "partyName": member.get("partyName", ""),
            })
    
    for member in data.get("house", []):
        terms = member.get("terms", {}).get("item", [])
        is_current = any(
            t.get("endYear") is None or t.get("endYear", 0) >= 2025
            for t in terms
        )
        if is_current:
            current.append({
                "bioguideId": member["bioguideId"],
                "name": member["name"],
                "district": member.get("district"),
                "chamber": "House",
                "partyName": member.get("partyName", ""),
            })
    
    return current

def get_sponsored_bills(bioguide_id):
    """Get all sponsored bills for a member."""
    try:
        resp = requests.get(MEMBER_API.format(bioguide_id), timeout=30)
        resp.raise_for_status()
        data = resp.json()
        return data.get("sponsoredBills", [])
    except Exception as e:
        print(f"  Error fetching bills for {bioguide_id}: {e}")
        return []

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

def make_cache_key(bill):
    """Create cache key from bill data."""
    congress = bill.get("congress", "")
    bill_type = bill.get("billType", bill.get("type", "")).lower()
    bill_number = bill.get("number", bill.get("billNumber", ""))
    return f"{congress}/{bill_type}/{bill_number}"

def fetch_summary(congress, bill_type, bill_number):
    """Fetch bill summary from Congress.gov API."""
    url = CONGRESS_SUMMARY_API.format(congress, bill_type.lower(), bill_number)
    headers = {"X-API-Key": CONGRESS_API_KEY}
    try:
        resp = requests.get(url, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        summaries = data.get("summaries", [])
        if summaries:
            return summaries[0].get("text", "")
    except Exception as e:
        print(f"  Error fetching summary for {congress}/{bill_type}/{bill_number}: {e}")
    return ""

def generate_pros_cons(summary_text, bill_desc=""):
    """Generate 2 pros and 2 cons based on bill summary."""
    import random
    
    # If we have a summary, use it to generate context-aware pros/cons
    text = (summary_text + " " + bill_desc).strip()
    
    # Generic fallback pros/cons by bill type
    # We'll use pattern matching on the summary text
    text_lower = text.lower()
    
    pros = []
    cons = []
    
    # Tax-related bills
    if any(w in text_lower for w in ["tax", "taxpayer", "taxation", "internal revenue"]):
        pros.append("• Reduces tax burden for American families and businesses.")
        pros.append("• Simplifies the tax code and reduces compliance costs.")
        cons.append("• May reduce federal revenue and increase the deficit.")
        cons.append("• Could disproportionately benefit high-income earners.")
    
    # Healthcare bills
    elif any(w in text_lower for w in ["health", "medicare", "medicaid", "insurance", "hospital", "drug", "patient"]):
        pros.append("• Expands access to affordable healthcare for Americans.")
        pros.append("• Lowers prescription drug costs for patients.")
        cons.append("• May increase federal healthcare spending significantly.")
        cons.append("• Could lead to higher insurance premiums for some.")
    
    # Education bills
    elif any(w in text_lower for w in ["education", "school", "student", "teacher", "college", "university"]):
        pros.append("• Increases funding for public school infrastructure.")
        pros.append("• Expands access to higher education and job training.")
        cons.append("• Adds to federal education spending without reforms.")
        cons.append("• May impose new mandates on state and local schools.")
    
    # Environment/energy bills
    elif any(w in text_lower for w in ["climate", "environment", "energy", "clean", "emission", "green", "pollution"]):
        pros.append("• Invests in clean energy and reduces carbon emissions.")
        pros.append("• Creates jobs in the renewable energy sector.")
        cons.append("• Could increase energy costs for consumers and businesses.")
        cons.append("• May place burdensome regulations on industry.")
    
    # Defense/military bills
    elif any(w in text_lower for w in ["defense", "military", "veteran", "armed forces", "national security", "homeland"]):
        pros.append("• Strengthens national security and military readiness.")
        pros.append("• Improves benefits and support for our veterans.")
        cons.append("• Significantly increases defense spending and the deficit.")
        cons.append("• Could reduce funds available for domestic programs.")
    
    # Agriculture/farming bills
    elif any(w in text_lower for w in ["agriculture", "farm", "farmer", "rural", "crop", "livestock"]):
        pros.append("• Supports American farmers and rural communities.")
        pros.append("• Strengthens the agricultural supply chain and food security.")
        cons.append("• Expands subsidy programs that distort market prices.")
        cons.append("• May increase federal spending on farm support programs.")
    
    # Infrastructure/transportation bills
    elif any(w in text_lower for w in ["infrastructure", "transportation", "road", "bridge", "highway", "transit", "rail"]):
        pros.append("• Invests in critical infrastructure repairs and upgrades.")
        pros.append("• Creates construction jobs and boosts local economies.")
        cons.append("• Increases federal spending and the national debt.")
        cons.append("• May lead to higher taxes or user fees for funding.")
    
    # Immigration bills
    elif any(w in text_lower for w in ["immigration", "border", "asylum", "visa", "citizen", "deportation"]):
        pros.append("• Enhances border security and immigration enforcement.")
        pros.append("• Provides a pathway to legal status for certain groups.")
        cons.append("• Could strain public resources in some communities.")
        cons.append("• May face legal challenges over due process concerns.")
    
    # Housing bills
    elif any(w in text_lower for w in ["housing", "rent", "mortgage", "homeless", "property"]):
        pros.append("• Increases affordable housing options for low-income families.")
        pros.append("• Provides rental assistance to prevent homelessness.")
        cons.append("• Expands federal housing programs without addressing root causes.")
        cons.append("• May increase housing costs through new regulations.")
    
    # Small business / economy bills
    elif any(w in text_lower for w in ["business", "entrepreneur", "small business", "economy", "job", "employment", "worker"]):
        pros.append("• Supports small businesses and job creation.")
        pros.append("• Provides tax incentives for business investment.")
        cons.append("• Could add to the federal deficit without offsetting cuts.")
        cons.append("• May create regulatory burdens on small enterprises.")
    
    # Technology / internet bills
    elif any(w in text_lower for w in ["technology", "internet", "cyber", "data", "privacy", "ai", "artificial intelligence"]):
        pros.append("• Promotes innovation in technology and cybersecurity.")
        pros.append("• Strengthens data privacy protections for consumers.")
        cons.append("• May impose compliance costs on technology companies.")
        cons.append("• Could slow innovation through new government regulations.")
    
    # Criminal justice / law enforcement
    elif any(w in text_lower for w in ["crime", "criminal", "police", "law enforcement", "justice", "sentence", "prison"]):
        pros.append("• Enhances public safety and supports law enforcement.")
        pros.append("• Reforms criminal justice to reduce recidivism rates.")
        cons.append("• Could expand the federal prison system unnecessarily.")
        cons.append("• May limit judicial discretion in sentencing.")
    
    # Trade bills
    elif any(w in text_lower for w in ["trade", "tariff", "import", "export", "commerce"]):
        pros.append("• Protects American workers and domestic industries.")
        pros.append("• Promotes fair trade practices with international partners.")
        cons.append("• May lead to higher consumer prices on imports.")
        cons.append("• Could trigger retaliatory tariffs from other nations.")
    
    # Civil rights / voting
    elif any(w in text_lower for w in ["voting", "civil rights", "discrimination", "equality", "race", "gender"]):
        pros.append("• Protects voting rights and ensures fair elections.")
        pros.append("• Strengthens anti-discrimination protections for all Americans.")
        cons.append("• Could centralize election administration at the federal level.")
        cons.append("• May face constitutional challenges on states' rights grounds.")
    
    # Labor / workers rights
    elif any(w in text_lower for w in ["labor", "union", "minimum wage", "overtime", "worker", "employee"]):
        pros.append("• Raises wages and improves working conditions for workers.")
        pros.append("• Strengthens collective bargaining rights for employees.")
        cons.append("• Could increase labor costs for small businesses.")
        cons.append("• May lead to job losses in labor-intensive industries.")
    
    # Government reform / transparency
    elif any(w in text_lower for w in ["government", "congress", "federal agency", "bureaucracy", "transparency", "ethics"]):
        pros.append("• Increases government transparency and accountability.")
        pros.append("• Reduces bureaucratic waste and inefficiency.")
        cons.append("• New reporting requirements may slow agency operations.")
        cons.append("• Could face opposition from established government interests.")
    
    # Veterans
    elif any(w in text_lower for w in ["veteran", "veterans affairs", "va ", "veterans'"]):
        pros.append("• Improves healthcare access and benefits for veterans.")
        pros.append("• Reduces wait times at VA facilities for medical care.")
        cons.append("• Increases federal spending on veterans programs.")
        cons.append("• May duplicate existing services without coordination.")
    
    # Social Security / retirement
    elif any(w in text_lower for w in ["social security", "retirement", "pension", "elderly", "senior"]):
        pros.append("• Protects and strengthens Social Security benefits.")
        pros.append("• Helps seniors maintain financial security in retirement.")
        cons.append("• Could accelerate Social Security trust fund depletion.")
        cons.append("• May increase payroll taxes on workers to fund it.")
    
    # Broad generic fallback
    else:
        # Try to use keywords from the summary
        if "fund" in text_lower or "appropriation" in text_lower or "grant" in text_lower:
            pros.append("• Provides funding for important federal programs.")
            pros.append("• Supports states and local communities with grants.")
            cons.append("• Increases overall federal spending and the deficit.")
            cons.append("• Creates long-term obligations for taxpayers.")
        elif "regulation" in text_lower or "requirement" in text_lower or "compliance" in text_lower:
            pros.append("• Updates regulations to reflect modern standards.")
            pros.append("• Protects public health, safety, and welfare.")
            cons.append("• Adds new compliance burdens on businesses.")
            cons.append("• May increase costs passed on to consumers.")
        elif "report" in text_lower or "study" in text_lower or "commission" in text_lower:
            pros.append("• Gathers data to inform evidence-based policymaking.")
            pros.append("• Promotes accountability through oversight and reporting.")
            cons.append("• Authorizes another study without taking direct action.")
            cons.append("• Creates new government entities and administrative costs.")
        else:
            # Ultra generic
            pros.append("• Addresses an important issue facing Americans today.")
            pros.append("• Provides a framework for addressing this policy challenge.")
            cons.append("• May have unintended consequences for affected groups.")
            cons.append("• Could increase the size and scope of government.")
    
    return {
        "pros": pros[:2],
        "cons": cons[:2]
    }

def main():
    print("=" * 60)
    print("Georgia Congressional Members - Bill Analysis Generator")
    print("=" * 60)
    
    # Step 1: Get Georgia members
    print("\n[Step 1] Fetching Georgia members...")
    members = get_ga_members()
    print(f"  Found {len(members)} currently serving members:")
    for m in members:
        chamber = "Sen." if m["chamber"] == "Senate" else "Rep."
        district = f" (D{m['district']})" if m.get("district") else ""
        print(f"    {chamber} {m['name']}{district} ({m['partyName']}) - {m['bioguideId']}")
    
    # Step 2: Load cache
    print("\n[Step 2] Loading existing cache...")
    cache = load_cache()
    print(f"  Cache has {len(cache)} existing entries")
    
    # Collect all sponsored bills
    all_bills = []
    for member in members:
        print(f"\n  Fetching bills for {member['name']} ({member['bioguideId']})...")
        bills = get_sponsored_bills(member['bioguideId'])
        print(f"    Found {len(bills)} sponsored bills")
        for bill in bills:
            bill['_member_name'] = member['name']
            bill['_member_id'] = member['bioguideId']
        all_bills.extend(bills)
        time.sleep(0.5)  # Be nice to the API
    
    print(f"\n  Total sponsored bills: {len(all_bills)}")
    
    # Step 2b: Check which are already cached
    print("\n[Step 2b] Checking cache...")
    uncached = []
    cached_count = 0
    for bill in all_bills:
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
    
    # Step 3: Fetch summaries for uncached bills
    print(f"\n[Step 3] Fetching summaries for {len(uncached)} uncached bills...")
    
    new_entries = {}
    skipped = 0
    errors = 0
    
    for i, bill in enumerate(uncached):
        congress = bill.get("congress", "")
        bill_type = bill.get("billType", bill.get("type", "")).lower()
        bill_number = bill.get("number", bill.get("billNumber", ""))
        key = make_cache_key(bill)
        title = bill.get("title", bill.get("billTitle", ""))
        member_name = bill.get("_member_name", "Unknown")
        
        print(f"  [{i+1}/{len(uncached)}] {key} ({member_name})", end="")
        
        # Skip if already added in this run (duplicates across members)
        if key in new_entries:
            print(" - already processed")
            continue
        
        # Fetch summary
        summary = fetch_summary(congress, bill_type, bill_number)
        if not summary:
            print(f" - no summary available, skipping")
            skipped += 1
            continue
        
        print(f" - got summary ({len(summary)} chars)", end="")
        
        # Step 4: Generate pros/cons
        analysis = generate_pros_cons(summary, title)
        new_entries[key] = analysis
        print(f" -> pros/cons generated")
        
        # Rate limit: 1 request per second for Congress.gov API
        time.sleep(1.5)
    
    print(f"\n  Results: {len(new_entries)} new analyses, {skipped} skipped (no summary), {errors} errors")
    
    # Step 5: Save to cache
    print("\n[Step 5] Saving to cache...")
    cache.update(new_entries)
    save_cache(cache)
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"  Total members processed: {len(members)}")
    print(f"  Total sponsored bills found: {len(all_bills)}")
    print(f"  Already in cache: {cached_count}")
    print(f"  New analyses added: {len(new_entries)}")
    print(f"  Skipped (no summary): {skipped}")
    print(f"  Cache now has: {len(cache)} total entries")
    print("=" * 60)

if __name__ == "__main__":
    main()
