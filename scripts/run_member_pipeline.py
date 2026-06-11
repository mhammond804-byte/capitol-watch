#!/usr/bin/env python3
"""
Full cron job: Process 2-3 states per run, fetching member-sponsored bills,
checking cache, fetching summaries, generating pros/cons, and merging.

Phase 1: Start with FL (since Michael is a FL agent) + 2 others.
"""
import json, os, subprocess, time, sys, re, html
from datetime import datetime

# === CONFIG ===
CONGRESS_API_KEY = "xH3oHkvJab5BzhnVvJ5zXk3bHK5fPqHZ263Asebc"
CACHE_FILE = os.path.expanduser("~/Desktop/capitol-watch/bill-analysis.json")
PROGRESS_FILE = os.path.expanduser("~/Desktop/capitol-watch/.bill-fill-progress.json")

NEW_BILLS_FILE = "/tmp/new_bills.json"
SUMMARIES_FILE = "/tmp/summaries.json"
OUTPUT_FILE = "/tmp/final_results.json"

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

def get_state_codes():
    """Get list of US state codes."""
    data = fetch_json("https://capitolwatch.us/api/states")
    if isinstance(data, list):
        if data and isinstance(data[0], dict):
            return [s["code"] for s in data if isinstance(s, dict) and s.get("code")]
        elif data and isinstance(data[0], str):
            return [s for s in data if len(s) == 2]
    return []

def is_current_member(member):
    """Check if member is currently serving based on latest term."""
    terms = member.get("terms", {})
    items = terms.get("item", [])
    if not items:
        return False
    latest = items[-1]
    end = latest.get("endYear")
    if end is None:
        return True
    try:
        return int(end) >= 2025
    except (ValueError, TypeError):
        return False

def fetch_state_members(state):
    """Get House and Senate members for a state."""
    data = fetch_json(f"https://capitolwatch.us/api/state/{state}")
    if not isinstance(data, dict):
        return [], []
    house = data.get("house", [])
    senate = data.get("senate", [])
    return house, senate

def fetch_member_bills(bioguide):
    """Get bills from capitolwatch.us member endpoint.
    API returns {"member": {...}, "sponsored": [...]}
    """
    data = fetch_json(f"https://capitolwatch.us/api/member/{bioguide}")
    if not data:
        return []
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        # Member page wraps in {"member": ..., "sponsored": [...]}
        for key in ["sponsored", "bills", "sponsoredBills", "sponsoredLegislation"]:
            if key in data:
                return data[key]
        return []
    return []

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
    return {"states_completed": [], "members_processed": 0, "bills_added": 0}

def save_progress(p):
    with open(PROGRESS_FILE, "w") as f:
        json.dump(p, f, indent=2)

def make_cache_key(bill):
    """Build key: 'congress/type/number' lowercased."""
    congress = bill.get("congress", "")
    bill_type = (bill.get("type", "") or bill.get("billType", "") or "").lower().strip()
    bill_number = bill.get("number", bill.get("billNumber", ""))
    if congress and bill_type and bill_number:
        return f"{congress}/{bill_type}/{bill_number}".lower()
    return None

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
    if len(text) > 300:
        text = text[:297] + "..."
    return text

def clean_html(text):
    if not text:
        return ""
    text = re.sub(r'<[^>]+>', ' ', text)
    text = html.unescape(text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def classify_bill(title, summary):
    """Classify a bill by policy area."""
    t = (title + " " + summary).lower()
    
    # Specific categories (checked first)
    if any(w in t for w in ["keystone", "keystone xl", "pipeline permit"]):
        return ["keystone_pipeline"]
    if any(w in t for w in ["congressional gold medal", "gold medal act"]):
        return ["congressional_gold_medal"]
    if any(w in t for w in ["commemorative coin"]):
        return ["commemorative_coin"]
    if any(w in t for w in ["balance budget amendment", "balanced budget"]):
        return ["balance_budget"]
    if "compact of free association" in t:
        return ["compact_of_free_association"]
    if any(w in t for w in ["parental rights", "women's bill of rights"]):
        return ["parental_rights"]
    if any(w in t for w in ["whale", "marine mammal", "endangered species"]):
        return ["whales_marine_life", "environment"]
    if any(w in t for w in ["national park"]):
        return ["national_park_designation", "environment"]
    if any(w in t for w in ["constitutional amendment", "proposing an amendment"]):
        return ["constitutional_amendment", "civil_rights_voting"]
    if "national emergency" in t:
        return ["national_emergency"]
    if any(w in t for w in ["water right", "water settlement", "indian water"]):
        return ["water_rights", "environment"]
    if any(w in t for w in ["firearm", "second amendment", "gun", "ammunition"]):
        return ["firearms_rights", "crime_guns"]
    if "mental health" in t:
        return ["mental_health", "healthcare"]
    if any(w in t for w in ["expressed disapproval", "providing for congressional disapproval"]):
        return ["congressional_approval_disapproval"]
    if any(w in t for w in ["cyber", "cybersecurity"]):
        return ["cybersecurity", "technology"]
    if any(w in t for w in ["climate", "resilien", "extreme heat"]):
        return ["climate_resilience", "environment"]
    if any(w in t for w in ["housing voucher", "affordable housing", "homeless"]):
        return ["housing_vouchers", "housing"]
    if any(w in t for w in ["energy independence", "domestic production"]):
        return ["energy_independence", "energy"]
    if any(w in t for w in ["social security", "retirement"]):
        return ["social_security"]
    if any(w in t for w in ["veteran", "veterans"]):
        return ["veterans"]
    if any(w in t for w in ["abortion", "reproductive", "pro-life", "pregnancy"]):
        return ["abortion"]
    
    # Broader categories
    cats = []
    if any(w in t for w in ["tax", "deduction", "irs", "internal revenue", "tax credit"]):
        cats.append("tax")
    if any(w in t for w in ["health", "medicare", "medicaid", "hospital", "drug", "pharmacy", "prescription"]):
        cats.append("healthcare")
    if any(w in t for w in ["border", "immigration", "migrant", "asylum"]):
        cats.append("immigration_border")
    if any(w in t for w in ["environment", "carbon", "emission", "pollution", "renewable", "conservation"]):
        cats.append("environment")
    if any(w in t for w in ["defense", "military", "armed forces", "national security"]):
        cats.append("defense_security")
    if any(w in t for w in ["education", "school", "student", "teacher"]):
        cats.append("education")
    if any(w in t for w in ["energy", "electric", "solar", "wind"]):
        cats.append("energy")
    if any(w in t for w in ["crime", "drug", "fentanyl", "law enforcement", "police"]):
        cats.append("crime_guns")
    if any(w in t for w in ["china", "taiwan", "tariff", "trade", "sanction"]):
        cats.append("trade_china")
    if any(w in t for w in ["technology", "internet", "data privacy", "artificial intelligence"]):
        cats.append("technology")
    if any(w in t for w in ["infrastructure", "highway", "bridge", "road"]):
        cats.append("infrastructure")
    if any(w in t for w in ["agriculture", "farm", "crop", "farmer", "rural"]):
        cats.append("agriculture")
    if any(w in t for w in ["native american", "tribal", "tribe"]):
        cats.append("native_americans")
    if any(w in t for w in ["voting", "election", "ballot", "voter"]):
        cats.append("civil_rights_voting")
    if any(w in t for w in ["budget", "spending", "appropriation", "deficit", "debt"]):
        cats.append("budget_spending")
    if any(w in t for w in ["small business", "entrepreneur"]):
        cats.append("small_business")
    if any(w in t for w in ["housing"]):
        cats.append("housing")
    
    if not cats:
        cats.append("general")
    return cats

# Pros/cons templates
PROS_CONS = {
    "tax": {"pros": ["Reduces the tax burden on families and small businesses.", "Simplifies the tax code and reduces compliance costs."], "cons": ["May reduce federal revenue and increase the deficit.", "Benefits could disproportionately favor higher earners."]},
    "healthcare": {"pros": ["Expands access to affordable healthcare for more Americans.", "Lowers prescription drug costs for patients and seniors."], "cons": ["Could increase government spending and insurance premiums.", "May impose unfunded mandates on healthcare providers."]},
    "veterans": {"pros": ["Honors the service of veterans and improves their benefits.", "Expands healthcare access for those who served."], "cons": ["Adds to federal spending without a dedicated funding source.", "May create administrative burdens at the VA."]},
    "immigration_border": {"pros": ["Strengthens border security and enforces immigration laws.", "Provides a pathway for legal immigration and workforce needs."], "cons": ["Could violate due process rights for migrants and asylum seekers.", "May be costly to implement without clear funding."]},
    "environment": {"pros": ["Protects natural resources and promotes clean energy.", "Reduces pollution and safeguards public health."], "cons": ["May impose costly regulations on businesses and industry.", "Federal mandates can preempt state-level innovation."]},
    "defense_security": {"pros": ["Strengthens national security and military readiness.", "Supports our armed forces and their families."], "cons": ["Increases military spending at the expense of domestic programs.", "Could escalate tensions with foreign adversaries."]},
    "education": {"pros": ["Invests in America's students and future workforce.", "Expands school choice and educational opportunities."], "cons": ["Increases federal involvement in local education decisions.", "May not address underlying funding inequities."]},
    "housing": {"pros": ["Makes housing more affordable for working families.", "Helps reduce homelessness and housing insecurity."], "cons": ["Could distort local housing markets and raise rents.", "May create dependency on federal housing subsidies."]},
    "energy": {"pros": ["Promotes energy independence and domestic production.", "Supports innovation in clean and renewable energy."], "cons": ["May increase energy costs for consumers and businesses.", "Could have negative environmental impacts."]},
    "crime_guns": {"pros": ["Takes a strong stance against crime and drug trafficking.", "Protects public safety and supports law enforcement."], "cons": ["Could lead to overcriminalization and mass incarceration.", "May infringe on Second Amendment rights."]},
    "trade_china": {"pros": ["Counteracts unfair trade practices by foreign competitors.", "Protects American intellectual property and technology."], "cons": ["Trade restrictions may raise prices for consumers.", "Could trigger retaliatory tariffs from trading partners."]},
    "technology": {"pros": ["Promotes innovation in technology and digital infrastructure.", "Strengthens cybersecurity and protects consumer data."], "cons": ["Government regulation may slow technological progress.", "Compliance costs could burden smaller companies."]},
    "infrastructure": {"pros": ["Invests in critical infrastructure and creates jobs.", "Improves transportation safety and efficiency."], "cons": ["Increases federal spending and the national debt.", "May fund programs with limited oversight or accountability."]},
    "agriculture": {"pros": ["Supports American farmers and rural communities.", "Promotes agricultural innovation and food security."], "cons": ["Could distort agricultural markets with subsidies.", "May have unintended environmental consequences."]},
    "small_business": {"pros": ["Helps small businesses grow and create jobs.", "Reduces regulatory burdens on entrepreneurs."], "cons": ["Could reduce consumer protections and labor standards.", "Benefits may not reach the smallest businesses."]},
    "native_americans": {"pros": ["Honors treaty obligations to Native American tribes.", "Supports tribal sovereignty and economic development."], "cons": ["Could create complex jurisdictional disputes.", "Funding may not be sufficient to meet long-term needs."]},
    "social_security": {"pros": ["Protects retirement security for seniors.", "Ensures Social Security remains solvent for future generations."], "cons": ["Could reduce benefits for current or future retirees.", "May increase payroll taxes on workers."]},
    "budget_spending": {"pros": ["Promotes fiscal responsibility and reduces wasteful spending.", "Increases transparency in government budgeting."], "cons": ["Could defund essential programs and services.", "May limit government's ability to respond to crises."]},
    "civil_rights_voting": {"pros": ["Protects voting rights and strengthens election integrity.", "Upholds constitutional freedoms and civil liberties."], "cons": ["Could restrict access to the ballot for some voters.", "May increase partisan influence in election administration."]},
    "abortion": {"pros": ["Protects the sanctity of human life at all stages.", "Supports the constitutional right to bodily autonomy."], "cons": ["Could restrict access to essential healthcare services.", "Limits women's reproductive freedom and medical choice."]},
    "keystone_pipeline": {"pros": ["Supports energy independence through cross-border pipeline infrastructure.", "Creates construction jobs and boosts oil supply from Canada."], "cons": ["Risks oil spills and environmental damage along the pipeline route.", "May undermine efforts to transition to cleaner energy sources."]},
    "congressional_approval_disapproval": {"pros": ["Provides congressional oversight of executive branch actions.", "Preserves the legislative branch's constitutional check on power."], "cons": ["Could create delays in implementing important regulations.", "May politicize routine administrative decisions."]},
    "commemorative_coin": {"pros": ["Honors an important historical event or cultural landmark.", "Raises funds for related preservation and education efforts."], "cons": ["Adds to the proliferation of commemorative coin programs.", "May generate limited net revenue after production costs."]},
    "constitutional_amendment": {"pros": ["Strengthens constitutional protections for fundamental rights.", "Ensures lasting change that cannot be easily reversed."], "cons": ["The amendment process is lengthy and uncertain to succeed.", "Could have unintended legal consequences when interpreted by courts."]},
    "congressional_gold_medal": {"pros": ["Recognizes extraordinary acts of heroism and public service.", "Provides a lasting tribute to individuals who serve the nation."], "cons": ["Adds to the number of Congressional Gold Medals awarded.", "Could set a precedent for additional medal designations."]},
    "water_rights": {"pros": ["Settles long-standing water rights disputes and provides certainty.", "Supports infrastructure for clean water in communities."], "cons": ["Could be costly to implement the settlements and infrastructure.", "May set precedents affecting other water rights negotiations."]},
    "national_park_designation": {"pros": ["Preserves natural and cultural resources for future generations.", "Boosts local tourism and economic activity."], "cons": ["May restrict land use and economic development opportunities.", "Creates ongoing federal maintenance and management costs."]},
    "firearms_rights": {"pros": ["Protects the Second Amendment rights of law-abiding citizens.", "Ensures veterans and others retain their constitutional rights."], "cons": ["Could make it easier for individuals with mental health issues to access guns.", "May undermine efforts to reduce gun violence."]},
    "whales_marine_life": {"pros": ["Protects endangered marine species and biodiversity.", "Promotes sustainable fishing and ocean conservation practices."], "cons": ["Could impose restrictions on commercial shipping and fishing industries.", "May increase costs for maritime businesses."]},
    "mental_health": {"pros": ["Expands access to mental health services and support.", "Reduces stigma around mental health treatment."], "cons": ["Adds to federal healthcare spending without dedicated funding.", "May strain existing mental health provider networks."]},
    "national_emergency": {"pros": ["Reasserts congressional authority over national emergency declarations.", "Prevents indefinite emergency powers without legislative review."], "cons": ["Could hamper the executive branch's ability to respond to crises.", "May create uncertainty for ongoing national security operations."]},
    "compact_of_free_association": {"pros": ["Strengthens strategic partnerships in the Indo-Pacific region.", "Supports economic development in freely associated states."], "cons": ["Increases U.S. financial commitments to Pacific island nations.", "May not address long-term sustainability of these agreements."]},
    "balance_budget": {"pros": ["Requires the federal government to live within its means.", "Prevents excessive national debt accumulation."], "cons": ["Could force cuts to essential programs during economic downturns.", "Limits fiscal flexibility in times of national crisis."]},
    "parental_rights": {"pros": ["Protects the rights of parents in education and healthcare decisions.", "Increases transparency in school curricula and policies."], "cons": ["Could undermine inclusive educational environments.", "May create legal conflicts between parental and student rights."]},
    "cybersecurity": {"pros": ["Strengthens protection of critical infrastructure against cyber threats.", "Enhances information sharing between government and private sector."], "cons": ["Could impose costly compliance requirements on businesses.", "May raise privacy concerns about government data monitoring."]},
    "climate_resilience": {"pros": ["Prepares communities for the impacts of climate change.", "Invests in infrastructure that can withstand extreme weather."], "cons": ["Increases federal spending without immediate economic returns.", "May not adequately address the root causes of climate change."]},
    "housing_vouchers": {"pros": ["Helps low-income families afford stable housing.", "Reduces homelessness and housing insecurity for vulnerable populations."], "cons": ["Could increase federal rental assistance spending significantly.", "May not address the underlying shortage of affordable housing units."]},
    "energy_independence": {"pros": ["Reduces reliance on foreign energy sources and strengthens security.", "Supports domestic energy production and American energy jobs."], "cons": ["May have negative environmental impacts from increased production.", "Could slow the transition to renewable energy sources."]},
    "general": {"pros": ["Addresses an important policy issue needing legislative action.", "Provides a targeted solution to a specific problem."], "cons": ["May have unintended economic consequences across sectors.", "Lacks sufficient detail to fully assess its impact."]},
}

def generate_pros_cons(title, summary, policy_area=""):
    cats = classify_bill(title, summary)
    if policy_area and policy_area.lower().replace(" ", "_") in PROS_CONS:
        cats = [policy_area.lower().replace(" ", "_")] + cats
    used_pros = set()
    used_cons = set()
    pros = []
    cons = []
    for cat in cats:
        if cat in PROS_CONS:
            for p in PROS_CONS[cat]["pros"]:
                if p not in used_pros:
                    pros.append(p)
                    used_pros.add(p)
            for c in PROS_CONS[cat]["cons"]:
                if c not in used_cons:
                    cons.append(c)
                    used_cons.add(c)
        if len(pros) >= 2 and len(cons) >= 2:
            break
    if len(pros) < 2:
        pros = PROS_CONS["general"]["pros"]
    if len(cons) < 2:
        cons = PROS_CONS["general"]["cons"]
    return pros[:2], cons[:2]


# ================ MAIN ================
print("=" * 60)
print("CAPITOL WATCH - Member Sponsored Bill Pipeline")
print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
print("=" * 60)

# Load state from progress
progress = load_progress()
cache = load_cache()
cached_keys = set(cache.keys())

done_states = progress.get("states_completed", [])
print(f"Exising cache: {len(cache)} entries")
print(f"States already processed: {done_states}")

# Get all states
all_states = get_state_codes()
if not all_states:
    print("ERROR: Could not fetch states!")
    sys.exit(1)

print(f"All states: {all_states}")

# Filter out already-done states
unprocessed = sorted([s for s in all_states if s not in done_states])
print(f"Unprocessed states: {unprocessed}")

if not unprocessed:
    print("ALL STATES PROCESSED! Resetting.")
    unprocessed = all_states
    done_states = []

# Pick next 2 states
target_states = unprocessed[:2]
print(f"\nTargeting states: {target_states}")

# Track everything
all_new_bills = {}  # cache_key -> bill info
members_processed = 0
total_new = 0

for state in target_states:
    print(f"\n--- {state} ---")
    house, senate = fetch_state_members(state)
    print(f"  House members: {len(house)}, Senate: {len(senate)}")
    
    for member in house + senate:
        if not is_current_member(member):
            continue
        bid = member.get("bioguideId", "")
        if not bid:
            continue
        name = member.get("name", "Unknown")
        chamber = "Senate" if member in senate else "House"
        district = member.get("district", "")
        if district:
            loc = f"{state}-{district}"
        else:
            loc = state
        print(f"  {chamber[:1]}. {name} ({loc}) [{bid}]")
        
        bills = fetch_member_bills(bid)
        if not bills:
            print(f"    No bills data")
            continue
        
        print(f"    Bills returned: {len(bills)}")
        members_processed += 1
        member_new = 0
        
        for bill in bills:
            if not isinstance(bill, dict):
                continue
            cache_key = make_cache_key(bill)
            if not cache_key:
                continue
            if cache_key in all_new_bills:
                continue
            if cache_key in cached_keys:
                existing = cache[cache_key]
                # If existing entry already has sponsor info, skip
                if isinstance(existing, dict) and existing.get("sponsor_name"):
                    continue
                # Otherwise, we'll upgrade this entry
    
            title = bill.get("title", bill.get("shortTitle", ""))
            bill_type = bill.get("type", bill.get("billType", ""))
            number = bill.get("number", bill.get("billNumber", ""))
            congress = bill.get("congress", "")
            
            if not title:
                title = f"{bill_type.upper()} {number}"
            
            all_new_bills[cache_key] = {
                "title": str(title)[:200],
                "congress": congress,
                "type": bill_type,
                "number": number,
                "sponsor_name": f"{chamber[:1]}. {name} ({loc})",
                "sponsor_bioguide": bid,
                "sponsor_chamber": chamber,
                "sponsor_state": state,
                "introduced_date": bill.get("introducedDate", ""),
                "policy_area": bill.get("policyArea", {}).get("name") if isinstance(bill.get("policyArea"), dict) else "",
            }
            member_new += 1
            total_new += 1
        
        print(f"    New uncached: {member_new}")
        time.sleep(0.3)  # Rate limit
    
    # Mark state done
    if state not in done_states:
        done_states.append(state)
    progress["states_completed"] = done_states
    progress["last_run"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    save_progress(progress)

print(f"\n{'='*60}")
print(f"FOUND {total_new} NEW UNCACHED BILLS from {members_processed} members in {target_states}")
print(f"{'='*60}")

if total_new == 0:
    print("No new bills found. Nothing to do.")
    sys.exit(0)

# List bills
for key in sorted(all_new_bills.keys()):
    b = all_new_bills[key]
    print(f"  {key} | {b['sponsor_name']} | {b['title'][:70]}")

# Save new bills
with open(NEW_BILLS_FILE, "w") as f:
    json.dump(all_new_bills, f, indent=2)
print(f"\nSaved {total_new} new bills to {NEW_BILLS_FILE}")

# ================ STEP 2: Fetch summaries ================
print(f"\n{'='*60}")
print("STEP 2: Fetching summaries from Congress.gov API")
print(f"{'='*60}")

all_summaries = {}
bills_list = sorted(all_new_bills.items())
for i, (key, info) in enumerate(bills_list):
    congress = info["congress"]
    btype = info["type"].lower()
    number = info["number"]
    
    summary = fetch_summary(congress, btype, number)
    
    all_summaries[key] = {
        "summary": summary,
        "title": info.get("title", ""),
        "sponsor_name": info.get("sponsor_name", ""),
        "sponsor_bioguide": info.get("sponsor_bioguide", ""),
        "sponsor_chamber": info.get("sponsor_chamber", ""),
        "sponsor_state": info.get("sponsor_state", ""),
        "introduced_date": info.get("introduced_date", ""),
        "policy_area": info.get("policy_area", ""),
        "congress": congress,
        "type": btype,
        "number": number,
    }
    
    if (i + 1) % 10 == 0:
        print(f"  Progress: {i+1}/{len(bills_list)}")
        # Save checkpoint
        with open(SUMMARIES_FILE, "w") as f:
            json.dump(all_summaries, f, indent=2)
    
    time.sleep(0.2)

# Save all summaries
with open(SUMMARIES_FILE, "w") as f:
    json.dump(all_summaries, f, indent=2)

with_summary = sum(1 for v in all_summaries.values() if v.get("summary"))
print(f"\nSummaries fetched: {with_summary}/{len(all_summaries)} with content")

# ================ STEP 3: Generate pros/cons and merge ================
print(f"\n{'='*60}")
print("STEP 3: Generating pros/cons and merging into cache")
print(f"{'='*60}")

new_entries = {}
for key, info in all_summaries.items():
    title = info.get("title", "")
    summary = info.get("summary", "")
    policy_area = info.get("policy_area", "")
    
    cleaned = clean_html(summary)
    pros, cons = generate_pros_cons(title, cleaned, policy_area)
    
    new_entries[key] = {
        "pros": pros,
        "cons": cons,
        "title": title,
        "sponsor_name": info.get("sponsor_name", ""),
        "sponsor_bioguide": info.get("sponsor_bioguide", ""),
        "sponsor_chamber": info.get("sponsor_chamber", ""),
        "sponsor_state": info.get("sponsor_state", ""),
        "summary": cleaned,
        "congress": info.get("congress", ""),
        "type": info.get("type", ""),
        "number": info.get("number", ""),
        "introduced_date": info.get("introduced_date", ""),
        "policy_area": policy_area,
    }

print(f"Generated pros/cons for {len(new_entries)} bills")

# Merge into cache
before = len(cache)
for key, value in new_entries.items():
    if key in cache:
        existing = cache[key]
        if isinstance(existing, dict):
            # Merge: add sponsor fields to existing entry, but keep existing pros/cons if better
            for k, v in value.items():
                if k in ["pros", "cons"]:
                    # Only override if existing doesn't have them or they look generic
                    existing_pros = existing.get("pros", [])
                    existing_cons = existing.get("cons", [])
                    generic_pros = ["Addresses an important policy issue needing legislative action.", "Provides a targeted solution to a specific problem."]
                    generic_cons = ["May have unintended economic consequences across sectors.", "Lacks sufficient detail to fully assess its impact."]
                    if not existing_pros or all(p in generic_pros for p in existing_pros):
                        existing[k] = v
                    elif not existing_cons or all(c in generic_cons for c in existing_cons):
                        existing[k] = v
                else:
                    existing[k] = v
        else:
            cache[key] = value
    else:
        cache[key] = value

after = len(cache)
print(f"Cache before: {before}, after: {after}")
print(f"New keys added: {after - before}")

# Save cache
with open(CACHE_FILE, "w") as f:
    json.dump(cache, f, indent=2)
print(f"Saved {len(cache)} entries to {CACHE_FILE}")

# Update tracking
progress["states_completed"] = done_states
progress["last_run"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
progress["members_processed"] = members_processed
progress["bills_added"] = total_new
progress["total_bills"] = len(cache)
save_progress(progress)

# Show results
print(f"\n{'='*60}")
print("RESULTS:")
for key in sorted(new_entries.keys()):
    v = new_entries[key]
    print(f"  {key}")
    print(f"    Sponsor: {v['sponsor_name']}")
    print(f"    Title: {v['title'][:80]}")
    print(f"    Pros: {' | '.join(v['pros'])}")
    print(f"    Cons: {' | '.join(v['cons'])}")

print(f"\n{'='*60}")
print(f"SUMMARY:")
print(f"  States processed: {target_states}")
print(f"  Members: {members_processed}")
print(f"  New bills with pros/cons: {total_new}")
print(f"  Total cache: {len(cache)}")
print(f"  States done total: {done_states}")
print(f"  Next states: {unprocessed[2:4] if len(unprocessed) > 2 else ['(all done)']}")
print(f"{'='*60}")
