#!/usr/bin/env python3
"""
Capitol Watch - Member-Sponsored Bill Pipeline
This is the authoritative pipeline that:
1. Fetches all current members for 2 states per run
2. For each member, gets their sponsored bills from Congress.gov API
3. For each bill already in cache: UPGRADES it with sponsor_name, sponsor_bioguide, etc.
4. For uncached bills: fetches summary, generates pros/cons, adds to cache
5. Merges, commits, and pushes

Key insight: Most bills ARE already cached from random API pulls but lack 
sponsor info. We UPGRADE them with sponsor metadata rather than skipping them.
"""
import json, os, subprocess, time, sys, re, html, urllib.request, urllib.error
from datetime import datetime

# === CONFIG ===
CONGRESS_API_KEY = os.environ.get('CONGRESS_GOV_API_KEY') or os.environ.get('API_KEY')
CACHE_FILE = os.path.expanduser("~/Desktop/capitol-watch/bill-analysis.json")
PROGRESS_FILE = os.path.expanduser("~/Desktop/capitol-watch/.bill-fill-progress.json")

def fetch_json(url, headers=None, timeout=15):
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

def get_state_codes():
    data = fetch_json("https://capitolwatch.us/api/states")
    if isinstance(data, list):
        if data and isinstance(data[0], dict):
            return sorted([s["code"] for s in data if isinstance(s, dict) and s.get("code")])
    return []

def is_current(member):
    """Check if a member is currently serving (term has no endYear or endYear >= 2025)."""
    terms = member.get("terms", {}).get("item", [])
    if not terms:
        return False
    last = terms[-1]
    end = last.get("endYear")
    if end is None:
        return True
    try:
        return int(end) >= 2025
    except:
        return True  # No end year = current

def fetch_state_members(state):
    """Get current members for a state via Congress.gov API.
    Note: chamber= query param doesn't actually filter at API level,
    so we get ALL members and filter ourselves."""
    data = fetch_json(
        f"https://api.congress.gov/v3/member/{state}?congress=119&limit=250",
        headers={"X-Api-Key": CONGRESS_API_KEY}
    )
    
    house_members = []
    senate_members = []
    if data and "members" in data:
        for m in data["members"]:
            if not is_current(m):
                continue
            terms = m.get("terms", {}).get("item", [])
            if not terms:
                continue
            last = terms[-1]
            chamber = last.get("chamber", "")
            if "House" in chamber:
                house_members.append(m)
            elif "Senate" in chamber:
                senate_members.append(m)
    
    return house_members, senate_members

def get_member_bills(bioguide):
    """Fetch sponsored legislation from Congress.gov API."""
    data = fetch_json(
        f"https://api.congress.gov/v3/member/{bioguide}/sponsored-legislation?limit=20",
        headers={"X-Api-Key": CONGRESS_API_KEY}
    )
    if data:
        return data.get("sponsoredLegislation", [])
    return []

def fetch_summary(congress, bill_type, number):
    """Fetch bill summary from Congress.gov."""
    url = f"https://api.congress.gov/v3/bill/{congress}/{bill_type}/{number}/summaries?format=json"
    data = fetch_json(url, headers={"X-Api-Key": CONGRESS_API_KEY})
    if not data:
        return ""
    summaries = data.get("summaries", [])
    if not summaries:
        return ""
    best = max(summaries, key=lambda s: len(s.get("text", "")))
    text = best.get("text", "")
    text = re.sub(r'<[^>]+>', ' ', text)
    if len(text) > 300:
        text = text[:297] + "..."
    return text

def classify_bill(title, summary):
    """Classify bill for pros/cons selection."""
    t = (title + " " + summary).lower()
    
    # Specific categories first
    if any(w in t for w in ["tiananmen"]): return ["human_rights_china"]
    if any(w in t for w in ["congressional gold medal"]): return ["congressional_medal"]
    if any(w in t for w in ["commemorative"]): return ["commemorative"]
    if any(w in t for w in ["balanced budget"]): return ["balanced_budget"]
    if any(w in t for w in ["whale", "marine mammal"]): return ["environment_marine"]
    if any(w in t for w in ["national park", "public land"]): return ["public_lands"]
    
    cats = []
    if any(w in t for w in ["tax", "irs", "internal revenue", "tax credit"]): cats.append("tax")
    if any(w in t for w in ["health", "medicare", "medicaid", "drug", "prescription", "hospital"]): cats.append("healthcare")
    if any(w in t for w in ["veteran", "veterans"]): cats.append("veterans")
    if any(w in t for w in ["border", "immigration", "migrant"]): cats.append("immigration_border")
    if any(w in t for w in ["environment", "carbon", "pollution", "conservation", "climate"]): cats.append("environment")
    if any(w in t for w in ["defense", "military", "national security", "armed forces"]): cats.append("defense")
    if any(w in t for w in ["education", "school", "student", "teacher"]): cats.append("education")
    if any(w in t for w in ["crime", "drug", "fentanyl", "law enforcement", "police"]): cats.append("crime_safety")
    if any(w in t for w in ["china", "taiwan", "tariff", "sanction", "ccp", "beijing"]): cats.append("trade_china")
    if any(w in t for w in ["technology", "internet", "data privacy", "cyber", "ai"]): cats.append("technology_cyber")
    if any(w in t for w in ["infrastructure", "highway", "bridge", "road"]): cats.append("infrastructure")
    if any(w in t for w in ["agriculture", "farm", "farmer", "rural"]): cats.append("agriculture")
    if any(w in t for w in ["voting", "election", "ballot", "constitution"]): cats.append("civil_rights")
    if any(w in t for w in ["budget", "spending", "deficit", "debt"]): cats.append("budget")
    if any(w in t for w in ["social security", "retirement", "pension"]): cats.append("social_security")
    if any(w in t for w in ["housing"]): cats.append("housing")
    if any(w in t for w in ["energy", "electric", "power", "oil", "gas"]): cats.append("energy")
    if any(w in t for w in ["small business"]): cats.append("small_business")
    if any(w in t for w in ["maritime", "ship", "port", "navy"]): cats.append("maritime_defense")
    if any(w in t for w in ["tibet"]): cats.append("human_rights_china")
    if not cats: cats.append("general")
    return cats

PROS_CONS = {
    "tax": {"pros": ["Reduces the tax burden on families and small businesses.", "Simplifies tax rules and cuts compliance costs."], "cons": ["Could reduce federal revenue and increase the deficit.", "Benefits may disproportionately favor higher earners."]},
    "healthcare": {"pros": ["Expands access to affordable healthcare for more Americans.", "Lowers prescription drug costs for patients and seniors."], "cons": ["Could increase government spending and insurance premiums.", "May impose unfunded mandates on healthcare providers."]},
    "veterans": {"pros": ["Honors the service of veterans and improves their benefits.", "Expands healthcare access for those who served our country."], "cons": ["Adds to federal spending without a dedicated funding source.", "May create administrative delays at the VA."]},
    "immigration_border": {"pros": ["Strengthens border security and enforces immigration laws.", "Provides a pathway for legal immigration to meet workforce needs."], "cons": ["Could violate due process rights for migrants and asylum seekers.", "May be costly to implement without clear funding sources."]},
    "environment": {"pros": ["Protects natural resources and promotes clean energy.", "Reduces pollution and safeguards public health."], "cons": ["May impose costly regulations on businesses and industry.", "Federal mandates can preempt state-level innovation."]},
    "defense": {"pros": ["Strengthens national security and military readiness.", "Supports our armed forces and their families."], "cons": ["Increases military spending at the expense of domestic programs.", "Could escalate tensions with foreign adversaries."]},
    "education": {"pros": ["Invests in America's students and future workforce.", "Expands school choice and educational opportunities."], "cons": ["Increases federal involvement in local education decisions.", "May not address underlying funding inequities."]},
    "crime_safety": {"pros": ["Takes a strong stance against crime and drug trafficking.", "Protects public safety and supports law enforcement."], "cons": ["Could lead to overcriminalization and mass incarceration.", "May infringe on Second Amendment rights."]},
    "trade_china": {"pros": ["Counteracts unfair trade practices by foreign competitors.", "Protects American intellectual property and technology."], "cons": ["Trade restrictions may raise prices for consumers.", "Could trigger retaliatory tariffs from trading partners."]},
    "technology_cyber": {"pros": ["Promotes innovation in technology and digital infrastructure.", "Strengthens cybersecurity and protects consumer data."], "cons": ["Government regulation may slow technological progress.", "Compliance costs could burden smaller companies."]},
    "infrastructure": {"pros": ["Invests in critical infrastructure and creates jobs.", "Improves transportation safety and efficiency."], "cons": ["Increases federal spending and the national debt.", "May fund programs with limited oversight or accountability."]},
    "agriculture": {"pros": ["Supports American farmers and rural communities.", "Promotes agricultural innovation and food security."], "cons": ["Could distort agricultural markets with subsidies.", "May have unintended environmental consequences."]},
    "civil_rights": {"pros": ["Protects voting rights and strengthens election integrity.", "Upholds constitutional freedoms and civil liberties."], "cons": ["Could restrict access to the ballot for some voters.", "May increase partisan influence in election administration."]},
    "budget": {"pros": ["Promotes fiscal responsibility and reduces wasteful spending.", "Increases transparency in government budgeting."], "cons": ["Could defund essential programs and services.", "May limit government's ability to respond to crises."]},
    "social_security": {"pros": ["Protects retirement security for seniors.", "Ensures Social Security remains solvent for future generations."], "cons": ["Could reduce benefits for current or future retirees.", "May increase payroll taxes on workers."]},
    "housing": {"pros": ["Makes housing more affordable for working families.", "Helps reduce homelessness and housing insecurity."], "cons": ["Could distort local housing markets and raise rents.", "May create dependency on federal housing subsidies."]},
    "energy": {"pros": ["Promotes energy independence and domestic production.", "Supports innovation in clean and renewable energy."], "cons": ["May increase energy costs for consumers and businesses.", "Could have negative environmental impacts."]},
    "small_business": {"pros": ["Helps small businesses grow and create jobs.", "Reduces regulatory burdens on entrepreneurs."], "cons": ["Could reduce consumer protections and labor standards.", "Benefits may not reach the smallest businesses."]},
    "maritime_defense": {"pros": ["Strengthens maritime security and naval readiness.", "Protects critical shipping lanes and port infrastructure."], "cons": ["Increases defense spending without clear offsets.", "Could escalate tensions in contested waters."]},
    "human_rights_china": {"pros": ["Holds the Chinese government accountable for human rights abuses.", "Defends democratic values and freedom around the world."], "cons": ["Could damage diplomatic relations with a major world power.", "May have limited enforcement mechanisms and practical impact."]},
    "congressional_medal": {"pros": ["Recognizes extraordinary acts of heroism and public service.", "Provides a lasting tribute to those who serve the nation."], "cons": ["Adds to the growing number of Congressional Gold Medals awarded.", "Could set a precedent for additional medal designations."]},
    "commemorative": {"pros": ["Honors an important historical event or cultural landmark.", "Raises funds for related preservation and education efforts."], "cons": ["Adds to the proliferation of commemorative programs.", "May generate limited net revenue after production costs."]},
    "balanced_budget": {"pros": ["Requires the federal government to live within its means.", "Prevents excessive national debt accumulation."], "cons": ["Could force cuts to essential programs during economic downturns.", "Limits fiscal flexibility in times of national crisis."]},
    "environment_marine": {"pros": ["Protects endangered marine species and ocean biodiversity.", "Promotes sustainable fishing and ocean conservation."], "cons": ["Could restrict commercial shipping and fishing industries.", "May increase costs for maritime businesses."]},
    "public_lands": {"pros": ["Preserves natural and cultural resources for future generations.", "Boosts local tourism and outdoor recreation opportunities."], "cons": ["May restrict land use and economic development.", "Creates ongoing federal management and maintenance costs."]},
    "general": {"pros": ["Addresses an important policy issue needing legislative action.", "Provides a targeted solution to a specific problem."], "cons": ["May have unintended economic consequences across sectors.", "Lacks sufficient detail to fully assess its full impact."]},
}

def generate_pros_cons(title, summary, policy_area=""):
    cats = classify_bill(title, summary)
    if policy_area and policy_area.lower().replace(" ", "_") in PROS_CONS:
        cats = [policy_area.lower().replace(" ", "_")] + cats
    used_pros, used_cons = set(), set()
    pros, cons = [], []
    for cat in cats:
        if cat in PROS_CONS:
            for p in PROS_CONS[cat]["pros"]:
                if p not in used_pros: pros.append(p); used_pros.add(p)
            for c in PROS_CONS[cat]["cons"]:
                if c not in used_cons: cons.append(c); used_cons.add(c)
        if len(pros) >= 2 and len(cons) >= 2:
            break
    if len(pros) < 2: pros = PROS_CONS["general"]["pros"]
    if len(cons) < 2: cons = PROS_CONS["general"]["cons"]
    return pros[:2], cons[:2]

def load_cache():
    with open(CACHE_FILE) as f:
        return json.load(f)

def save_cache(cache):
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=2)

def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE) as f:
            return json.load(f)
    return {"states_completed": [], "members_processed": 0, "bills_upgraded": 0, "bills_added": 0}

def save_progress(p):
    with open(PROGRESS_FILE, "w") as f:
        json.dump(p, f, indent=2)

# ================ MAIN ================
print("=" * 60)
print("CAPITOL WATCH - Member-Sponsored Bill Pipeline")
print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
print("=" * 60)

progress = load_progress()
cache = load_cache()
done_states = progress.get("states_completed", [])
print(f"Cache: {len(cache)} entries")
print(f"States done: {done_states}")

all_states = get_state_codes()
if not all_states:
    print("ERROR: Could not fetch states!"); sys.exit(1)

unprocessed = sorted([s for s in all_states if s not in done_states])
if not unprocessed:
    print("ALL 50 STATES DONE! Resetting for fresh pass.")
    unprocessed = all_states; done_states = []

target_states = unprocessed[:2]
print(f"Targeting: {target_states}")

# === STEP 1: Collect bills from all members ===
all_new_bills = {}
all_upgraded = 0
members_processed = 0

for state in target_states:
    print(f"\n--- {state} ---")
    house, senate = fetch_state_members(state)
    current_members = [(m, "House") for m in house] + [(m, "Senate") for m in senate]
    print(f"  Current members: {len(house)} House, {len(senate)} Senate")
    
    for member, chamber in current_members:
        bid = member.get("bioguideId", "")
        if not bid: continue
        name = member.get("name", "Unknown")
        party = member.get("partyName", "")
        state_district = member.get("district", "At-Large") if chamber == "House" else state
        loc = f"{state}-{state_district}" if chamber == "House" else state
        label = f"{party} {loc}" if party else loc
        
        print(f"  {chamber[0]}. {name} ({label}) [{bid}]")
        
        bills = get_member_bills(bid)
        if not bills:
            print(f"    No bills data"); continue
        
        print(f"    {len(bills)} bills returned")
        members_processed += 1
        member_upgraded = 0
        member_new = 0
        
        for b in bills:
            congress = b.get("congress")
            btype = b.get("type")
            if not btype: continue
            btype = btype.lower()
            number = b.get("number", "")
            if not congress or not number: continue
            
            key = f"{congress}/{btype}/{number}".lower()
            title = b.get("title", "") or ""
            introduced = b.get("introducedDate", "") or ""
            policy_area_obj = b.get("policyArea", {})
            policy_area = policy_area_obj.get("name", "") if isinstance(policy_area_obj, dict) else ""
            
            sponsor_info = {
                "sponsor_name": f"{'Sen.' if chamber == 'Senate' else 'Rep.'} {name} ({label})",
                "sponsor_bioguide": bid,
                "sponsor_chamber": chamber,
                "sponsor_state": state,
                "sponsor_district": state_district if chamber == "House" else "",
            }
            
            if key in cache:
                existing = cache[key]
                if isinstance(existing, dict):
                    # Upgrade with sponsor info
                    existing.update(sponsor_info)
                    # Also add title if missing
                    if not existing.get("title"):
                        existing["title"] = title
                    if not existing.get("introduced_date"):
                        existing["introduced_date"] = introduced
                    if not existing.get("policy_area"):
                        existing["policy_area"] = policy_area
                    member_upgraded += 1
                else:
                    # Entry is a list or other type - replace
                    all_new_bills[key] = {**sponsor_info, "title": title, "congress": congress,
                                         "type": btype, "number": number, "introduced_date": introduced,
                                         "policy_area": policy_area}
                    member_new += 1
            else:
                # Brand new bill
                if key not in all_new_bills:
                    all_new_bills[key] = {**sponsor_info, "title": title, "congress": congress,
                                         "type": btype, "number": number, "introduced_date": introduced,
                                         "policy_area": policy_area}
                    member_new += 1
        
        print(f"    Upgraded: {member_upgraded}, New: {member_new}")
        all_upgraded += member_upgraded
        time.sleep(0.3)
    
    done_states.append(state)
    progress["states_completed"] = done_states
    save_progress(progress)

print(f"\n{'='*60}")
print(f"STEP 1 RESULTS:")
print(f"  Members processed: {members_processed}")
print(f"  Cache entries upgraded with sponsor info: {all_upgraded}")
print(f"  Brand new bills to process: {len(all_new_bills)}")
print(f"{'='*60}")

# === STEP 2: Fetch summaries and generate pros/cons for NEW bills ===
if all_new_bills:
    print(f"\n{'='*60}")
    print("STEP 2: Fetching summaries & generating pros/cons")
    print(f"{'='*60}")
    
    for i, (key, info) in enumerate(sorted(all_new_bills.items())):
        congress = info["congress"]
        btype = info["type"]
        number = info["number"]
        
        print(f"  [{i+1}/{len(all_new_bills)}] {key} - fetching summary...")
        summary = fetch_summary(congress, btype, number)
        
        title = info.get("title", "")
        policy_area = info.get("policy_area", "")
        pros, cons = generate_pros_cons(title, summary, policy_area)
        
        # Build full entry
        entry = {
            "pros": pros,
            "cons": cons,
            "title": title,
            "summary": summary,
            "sponsor_name": info["sponsor_name"],
            "sponsor_bioguide": info["sponsor_bioguide"],
            "sponsor_chamber": info["sponsor_chamber"],
            "sponsor_state": info["sponsor_state"],
            "sponsor_district": info.get("sponsor_district", ""),
            "congress": congress,
            "type": btype,
            "number": number,
            "introduced_date": info.get("introduced_date", ""),
            "policy_area": policy_area,
        }
        cache[key] = entry
        print(f"    Pros: {pros[0]} | Cons: {cons[0]}")
        time.sleep(0.3)
    
    print(f"\nAdded {len(all_new_bills)} new bills to cache")
else:
    print("\nNo new bills to process.")

# === STEP 3: Update progress and save ===
progress["bills_upgraded"] = progress.get("bills_upgraded", 0) + all_upgraded
progress["bills_added"] = progress.get("bills_added", 0) + len(all_new_bills)
progress["members_processed"] = progress.get("members_processed", 0) + members_processed
progress["last_run"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
progress["total_cache"] = len(cache)
save_progress(progress)
save_cache(cache)

# Count sponsor-linked entries
with_sponsor = sum(1 for v in cache.values() if isinstance(v, dict) and v.get("sponsor_name"))
print(f"\n{'='*60}")
print(f"FINAL SUMMARY:")
print(f"  Cache total: {len(cache)}")
print(f"  Sponsor-linked: {with_sponsor}")
print(f"  Upgraded this run: {all_upgraded}")
print(f"  New bills added: {len(all_new_bills)}")
print(f"  Processed states: {done_states}")
print(f"  Next states: {unprocessed[2:4] if len(unprocessed) > 2 else []}")
print(f"{'='*60}")

# Print details of new bills
if all_new_bills:
    print("\nNEW BILLS ADDED:")
    for key in sorted(all_new_bills.keys()):
        v = cache[key]
        print(f"  {key} | {v['sponsor_name']} | Pros: {v['pros'][0][:50]}... | Cons: {v['cons'][0][:50]}...")

# Print next states info
next_states = unprocessed[2:4] if len(unprocessed) > 2 else []
print(f"\nNext run should process: {next_states}")
print(f"\n{'='*60}")
print("DONE")
