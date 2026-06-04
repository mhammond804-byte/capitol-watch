#!/usr/bin/env python3
"""
Re-run pros/cons generation with better classification, then commit and push.
"""
import json, os, re, html

CACHE_FILE = os.path.expanduser("~/Desktop/capitol-watch/bill-analysis.json")

def clean_html(text):
    if not text:
        return ""
    text = re.sub(r'<[^>]+>', ' ', text)
    text = html.unescape(text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# Expanded pros/cons by category
PROS_CONS = {
    "tax": {
        "pros": ["Reduces the tax burden on families and small businesses.", "Simplifies the tax code and reduces compliance costs."],
        "cons": ["May reduce federal revenue and increase the deficit.", "Benefits could disproportionately favor higher earners."],
    },
    "healthcare": {
        "pros": ["Expands access to affordable healthcare for more Americans.", "Lowers prescription drug costs for patients and seniors."],
        "cons": ["Could increase government spending and insurance premiums.", "May impose unfunded mandates on healthcare providers."],
    },
    "veterans": {
        "pros": ["Honors the service of veterans and improves their benefits.", "Expands healthcare access for those who served."],
        "cons": ["Adds to federal spending without a dedicated funding source.", "May create administrative burdens at the VA."],
    },
    "immigration_border": {
        "pros": ["Strengthens border security and enforces immigration laws.", "Provides a pathway for legal immigration and workforce needs."],
        "cons": ["Could violate due process rights for migrants and asylum seekers.", "May be costly to implement without clear funding."],
    },
    "environment": {
        "pros": ["Protects natural resources and promotes clean energy.", "Reduces pollution and safeguards public health."],
        "cons": ["May impose costly regulations on businesses and industry.", "Federal mandates can preempt state-level innovation."],
    },
    "defense_security": {
        "pros": ["Strengthens national security and military readiness.", "Supports our armed forces and their families."],
        "cons": ["Increases military spending at the expense of domestic programs.", "Could escalate tensions with foreign adversaries."],
    },
    "education": {
        "pros": ["Invests in America's students and future workforce.", "Expands school choice and educational opportunities."],
        "cons": ["Increases federal involvement in local education decisions.", "May not address underlying funding inequities."],
    },
    "housing": {
        "pros": ["Makes housing more affordable for working families.", "Helps reduce homelessness and housing insecurity."],
        "cons": ["Could distort local housing markets and raise rents.", "May create dependency on federal housing subsidies."],
    },
    "energy": {
        "pros": ["Promotes energy independence and domestic production.", "Supports innovation in clean and renewable energy."],
        "cons": ["May increase energy costs for consumers and businesses.", "Could have negative environmental impacts."],
    },
    "crime_guns": {
        "pros": ["Takes a strong stance against crime and drug trafficking.", "Protects public safety and supports law enforcement."],
        "cons": ["Could lead to overcriminalization and mass incarceration.", "May infringe on Second Amendment rights."],
    },
    "trade_china": {
        "pros": ["Counteracts unfair trade practices by foreign competitors.", "Protects American intellectual property and technology."],
        "cons": ["Trade restrictions may raise prices for consumers.", "Could trigger retaliatory tariffs from trading partners."],
    },
    "technology": {
        "pros": ["Promotes innovation in technology and digital infrastructure.", "Strengthens cybersecurity and protects consumer data."],
        "cons": ["Government regulation may slow technological progress.", "Compliance costs could burden smaller companies."],
    },
    "infrastructure": {
        "pros": ["Invests in critical infrastructure and creates jobs.", "Improves transportation safety and efficiency."],
        "cons": ["Increases federal spending and the national debt.", "May fund programs with limited oversight or accountability."],
    },
    "agriculture": {
        "pros": ["Supports American farmers and rural communities.", "Promotes agricultural innovation and food security."],
        "cons": ["Could distort agricultural markets with subsidies.", "May have unintended environmental consequences."],
    },
    "small_business": {
        "pros": ["Helps small businesses grow and create jobs.", "Reduces regulatory burdens on entrepreneurs."],
        "cons": ["Could reduce consumer protections and labor standards.", "Benefits may not reach the smallest businesses."],
    },
    "native_americans": {
        "pros": ["Honors treaty obligations to Native American tribes.", "Supports tribal sovereignty and economic development."],
        "cons": ["Could create complex jurisdictional disputes.", "Funding may not be sufficient to meet long-term needs."],
    },
    "social_security": {
        "pros": ["Protects retirement security for seniors.", "Ensures Social Security remains solvent for future generations."],
        "cons": ["Could reduce benefits for current or future retirees.", "May increase payroll taxes on workers."],
    },
    "budget_spending": {
        "pros": ["Promotes fiscal responsibility and reduces wasteful spending.", "Increases transparency in government budgeting."],
        "cons": ["Could defund essential programs and services.", "May limit government's ability to respond to crises."],
    },
    "civil_rights_voting": {
        "pros": ["Protects voting rights and strengthens election integrity.", "Upholds constitutional freedoms and civil liberties."],
        "cons": ["Could restrict access to the ballot for some voters.", "May increase partisan influence in election administration."],
    },
    "abortion": {
        "pros": ["Protects the sanctity of human life at all stages.", "Supports the constitutional right to bodily autonomy."],
        "cons": ["Could restrict access to essential healthcare services.", "Limits women's reproductive freedom and medical choice."],
    },
    "keystone_pipeline": {
        "pros": ["Supports energy independence through cross-border pipeline infrastructure.", "Creates construction jobs and boosts oil supply from Canada."],
        "cons": ["Risks oil spills and environmental damage along the pipeline route.", "May undermine efforts to transition to cleaner energy sources."],
    },
    "congressional_approval_disapproval": {
        "pros": ["Provides congressional oversight of executive branch actions.", "Preserves the legislative branch's constitutional check on power."],
        "cons": ["Could create delays in implementing important regulations.", "May politicize routine administrative decisions."],
    },
    "disapproval_pipeline": {
        "pros": ["Upholds congressional authority over cross-border infrastructure projects.", "Provides a check on executive branch permitting decisions."],
        "cons": ["Could delay energy infrastructure projects and create uncertainty.", "May discourage private investment in major energy initiatives."],
    },
    "commemorative_coin": {
        "pros": ["Honors an important historical event or cultural landmark.", "Raises funds for related preservation and education efforts."],
        "cons": ["Adds to the proliferation of commemorative coin programs.", "May generate limited net revenue after production costs."],
    },
    "constitutional_amendment": {
        "pros": ["Strengthens constitutional protections for fundamental rights.", "Ensures lasting change that cannot be easily reversed."],
        "cons": ["The amendment process is lengthy and uncertain to succeed.", "Could have unintended legal consequences when interpreted by courts."],
    },
    "congressional_gold_medal": {
        "pros": ["Recognizes extraordinary acts of heroism and public service.", "Provides a lasting tribute to individuals who serve the nation."],
        "cons": ["Adds to the number of Congressional Gold Medals awarded.", "Could set a precedent for additional medal designations."],
    },
    "water_rights": {
        "pros": ["Settles long-standing water rights disputes and provides certainty.", "Supports infrastructure for clean water in communities."],
        "cons": ["Could be costly to implement the settlements and infrastructure.", "May set precedents affecting other water rights negotiations."],
    },
    "national_park_designation": {
        "pros": ["Preserves natural and cultural resources for future generations.", "Boosts local tourism and economic activity."],
        "cons": ["May restrict land use and economic development opportunities.", "Creates ongoing federal maintenance and management costs."],
    },
    "firearms_rights": {
        "pros": ["Protects the Second Amendment rights of law-abiding citizens.", "Ensures veterans and others retain their constitutional rights."],
        "cons": ["Could make it easier for individuals with mental health issues to access guns.", "May undermine efforts to reduce gun violence."],
    },
    "whales_marine_life": {
        "pros": ["Protects endangered marine species and biodiversity.", "Promotes sustainable fishing and ocean conservation practices."],
        "cons": ["Could impose restrictions on commercial shipping and fishing industries.", "May increase costs for maritime businesses."],
    },
    "mental_health": {
        "pros": ["Expands access to mental health services and support.", "Reduces stigma around mental health treatment."],
        "cons": ["Adds to federal healthcare spending without dedicated funding.", "May strain existing mental health provider networks."],
    },
    "national_emergency": {
        "pros": ["Reasserts congressional authority over national emergency declarations.", "Prevents indefinite emergency powers without legislative review."],
        "cons": ["Could hamper the executive branch's ability to respond to crises.", "May create uncertainty for ongoing national security operations."],
    },
    "compact_of_free_association": {
        "pros": ["Strengthens strategic partnerships in the Indo-Pacific region.", "Supports economic development in freely associated states."],
        "cons": ["Increases U.S. financial commitments to Pacific island nations.", "May not address long-term sustainability of these agreements."],
    },
    "balance_budget": {
        "pros": ["Requires the federal government to live within its means.", "Prevents excessive national debt accumulation."],
        "cons": ["Could force cuts to essential programs during economic downturns.", "Limits fiscal flexibility in times of national crisis."],
    },
    "parental_rights": {
        "pros": ["Protects the rights of parents in education and healthcare decisions.", "Increases transparency in school curricula and policies."],
        "cons": ["Could undermine inclusive educational environments.", "May create legal conflicts between parental and student rights."],
    },
    "cybersecurity": {
        "pros": ["Strengthens protection of critical infrastructure against cyber threats.", "Enhances information sharing between government and private sector."],
        "cons": ["Could impose costly compliance requirements on businesses.", "May raise privacy concerns about government data monitoring."],
    },
    "climate_resilience": {
        "pros": ["Prepares communities for the impacts of climate change.", "Invests in infrastructure that can withstand extreme weather."],
        "cons": ["Increases federal spending without immediate economic returns.", "May not adequately address the root causes of climate change."],
    },
    "housing_vouchers": {
        "pros": ["Helps low-income families afford stable housing.", "Reduces homelessness and housing insecurity for vulnerable populations."],
        "cons": ["Could increase federal rental assistance spending significantly.", "May not address the underlying shortage of affordable housing units."],
    },
    "energy_independence": {
        "pros": ["Reduces reliance on foreign energy sources and strengthens security.", "Supports domestic energy production and American energy jobs."],
        "cons": ["May have negative environmental impacts from increased production.", "Could slow the transition to renewable energy sources."],
    },
    "general": {
        "pros": ["Addresses an important policy issue needing legislative action.", "Provides a targeted solution to a specific problem."],
        "cons": ["May have unintended economic consequences across sectors.", "Lacks sufficient detail to fully assess its impact."],
    },
}

def classify_bill_precise(title, summary):
    """More precise classification for each bill."""
    t = (title + " " + summary).lower()
    
    # Check for very specific categories first
    if any(w in t for w in ["keystone", "keystone xl", "pipeline permit", "presidential permit"]):
        return ["keystone_pipeline"]
    if any(w in t for w in ["congressional gold medal", "gold medal act"]):
        return ["congressional_gold_medal"]
    if any(w in t for w in ["commemorative coin"]):
        return ["commemorative_coin"]
    if any(w in t for w in ["balance budget amendment", "balanced budget"]):
        return ["balance_budget"]
    if any(w in t for w in ["compact of free association"]):
        return ["compact_of_free_association"]
    if any(w in t for w in ["parental rights", "women's bill of rights", "parental"]):
        return ["parental_rights"]
    if any(w in t for w in ["whale", "marine mammal", "endangered species", "save oak flat"]):
        return ["whales_marine_life", "environment"]
    if any(w in t for w in ["national park", "chiricahua"]):
        return ["national_park_designation", "environment"]
    if any(w in t for w in ["constitutional amendment", "amend the constitution", "proposing an amendment"]):
        return ["constitutional_amendment", "civil_rights_voting"]
    if any(w in t for w in ["national emergency", "relating to a national emergency"]):
        return ["national_emergency"]
    if any(w in t for w in ["water right", "water settlement", "indian water", "navajo water", "drought resilient"]):
        return ["water_rights", "environment"]
    if any(w in t for w in ["firearm", "second amendment", "2nd amendment", "gun", "ammunition"]):
        return ["firearms_rights", "crime_guns"]
    if any(w in t for w in ["mental health", "mental"]):
        return ["mental_health", "healthcare"]
    if any(w in t for w in ["expressed disapproval", "disapproval of", "providing for congressional disapproval"]):
        return ["congressional_approval_disapproval"]
    if any(w in t for w in ["cyber", "cybersecurity", "data security"]):
        return ["cybersecurity", "technology"]
    if any(w in t for w in ["climate", "resilien", "extreme heat", "drought"]):
        return ["climate_resilience", "environment"]
    if any(w in t for w in ["housing voucher", "voucher", "affordable housing", "rent", "homebuyer", "first-time"]):
        return ["housing_vouchers", "housing"]
    if any(w in t for w in ["energy independence", "domestic production", "american energy"]):
        return ["energy_independence", "energy"]
    if any(w in t for w in ["social security", "retirement", "colas for seniors", "benefit"]):
        return ["social_security"]
    if any(w in t for w in ["veteran", "va ", "veterans"]):
        return ["veterans"]
    if any(w in t for w in ["abortion", "reproductive", "pro-life", "pregnancy", "pregnant", "unborn"]):
        return ["abortion"]
    
    # Broader categories
    cats = []
    if any(w in t for w in ["tax", "deduction", "irs", "internal revenue", "tax credit", "taxpayer"]):
        cats.append("tax")
    if any(w in t for w in ["health", "medicare", "medicaid", "hospital", "drug", "pharmacy", "prescription", "patient", "doctor"]):
        cats.append("healthcare")
    if any(w in t for w in ["border", "immigration", "migrant", "asylum", "visa", "deport", "citizenship"]):
        cats.append("immigration_border")
    if any(w in t for w in ["environment", "carbon", "emission", "pollution", "renewable", "clean energy", "conservation", "natural resource", "public land", "wildfire", "forest", "ecosystem"]):
        cats.append("environment")
    if any(w in t for w in ["defense", "military", "armed forces", "national security", "terror", "intelligence"]):
        cats.append("defense_security")
    if any(w in t for w in ["education", "school", "student", "teacher", "college"]):
        cats.append("education")
    if any(w in t for w in ["energy", "electric", "solar", "wind", "power plant", "grid", "utility"]):
        cats.append("energy")
    if any(w in t for w in ["crime", "drug", "fentanyl", "law enforcement", "police", "sentenc", "prison", "violence", "criminal"]):
        cats.append("crime_guns")
    if any(w in t for w in ["china", "taiwan", "tariff", "trade", "sanction"]):
        cats.append("trade_china")
    if any(w in t for w in ["technology", "internet", "data privacy", "ai ", "artificial intelligence", "computer", "chip", "semiconductor"]):
        cats.append("technology")
    if any(w in t for w in ["infrastructure", "highway", "bridge", "road", "transport", "rail"]):
        cats.append("infrastructure")
    if any(w in t for w in ["agriculture", "farm", "crop", "farmer", "rural", "food", "rice", "ranch", "duck"]):
        cats.append("agriculture")
    if any(w in t for w in ["native american", "indian", "tribal", "tribe", "reservation"]):
        cats.append("native_americans")
    if any(w in t for w in ["voting", "election", "ballot", "voter"]):
        cats.append("civil_rights_voting")
    if any(w in t for w in ["budget", "spending", "appropriation", "funding", "deficit", "debt"]):
        cats.append("budget_spending")
    if any(w in t for w in ["small business", "entrepreneur", "sba"]):
        cats.append("small_business")
    
    if not cats:
        cats.append("general")
    return cats

def generate_pros_cons(title, summary, policy_area=""):
    cats = classify_bill_precise(title, summary)
    
    # Also try policy_area
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
    
    # Fallback
    if len(pros) < 2:
        pros = PROS_CONS["general"]["pros"]
    if len(cons) < 2:
        cons = PROS_CONS["general"]["cons"]
    
    return pros[:2], cons[:2]

def main():
    print("=" * 60)
    print("Regenerating pros/cons with improved classification + commit")
    print("=" * 60)
    
    with open(CACHE_FILE) as f:
        cache = json.load(f)
    
    # Find entries without sponsor_name or our new entries
    # Actually, find all entries with congress field (our new ones)
    count = 0
    for key, val in list(cache.items()):
        if not isinstance(val, dict):
            continue
        if val.get("congress"):
            # This is one of our new entries - regenerate with better classification
            title = val.get("title", "")
            summary = val.get("summary", "")
            policy_area = val.get("policy_area", "")
            
            pros, cons = generate_pros_cons(title, summary, policy_area)
            cache[key]["pros"] = pros
            cache[key]["cons"] = cons
            count += 1
    
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=2)
    
    print(f"Regenerated pros/cons for {count} entries")
    
    # Show improved results  
    for key in sorted(cache.keys()):
        val = cache[key]
        if isinstance(val, dict) and val.get("congress"):
            title_short = val.get("title", "")[:60]
            pros = val.get("pros", [])
            cons = val.get("cons", [])
            print(f"\n  {key}")
            print(f"    Title: {title_short}")
            print(f"    Pros: {' | '.join(pros)}")
            print(f"    Cons: {' | '.join(cons)}")
    
    print(f"\n{'='*60}")
    print(f"Total cache: {len(cache)} entries")
    print(f"Member-sponsored bills with improved pros/cons: {count}")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
