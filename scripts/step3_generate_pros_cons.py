#!/usr/bin/env python3
"""
Step 3: Generate pros/cons for all bills in batches, then merge into bill-analysis.json.
Uses keyword-based analysis on bill title + summary to write relevant pros/cons.
"""
import json, os, re, html

CACHE_FILE = os.path.expanduser("~/Desktop/capitol-watch/bill-analysis.json")

def clean_html(text):
    """Strip HTML tags and decode entities."""
    if not text:
        return ""
    text = re.sub(r'<[^>]+>', ' ', text)
    text = html.unescape(text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def classify_bill(title, summary):
    """Classify a bill by policy area using keywords, return labels."""
    text = (title + " " + summary).lower()
    categories = []
    
    if any(w in text for w in ["tax", "taxpayer", "internal revenue", "deduction", "irs", "tax credit"]):
        categories.append("tax")
    if any(w in text for w in ["health", "medicare", "medicaid", "hospital", "doctor", "patient", "drug", "pharmacy", "prescription", "vaccine"]):
        categories.append("healthcare")
    if any(w in text for w in ["veteran", "va ", "military", "armed forces", "veterans"]):
        categories.append("veterans")
    if any(w in text for w in ["immigration", "border", "migrant", "asylum", "deport", "visa", "citizenship", "alien", "mexico"]):
        categories.append("immigration")
    if any(w in text for w in ["environment", "climate", "clean energy", "renewable", "carbon", "emission", "pollution", "oil", "gas", "pipeline", "keystone", "wildlife", "whale", "forest", "park", "conservation", "public land", "water", "drought", "wildfire"]):
        categories.append("environment")
    if any(w in text for w in ["defense", "security", "national security", "armed forces", "military", "terror", "intelligence", "nuclear"]):
        categories.append("defense")
    if any(w in text for w in ["education", "school", "student", "teacher", "college", "classroom"]):
        categories.append("education")
    if any(w in text for w in ["housing", "rent", "mortgage", "homeless", "affordable housing", "voucher"]):
        categories.append("housing")
    if any(w in text for w in ["energy", "electric", "power", "solar", "wind", "grid", "utility", "gas"]):
        categories.append("energy")
    if any(w in text for w in ["criminal", "crime", "prison", "sentenc", "police", "law enforcement", "drug", "fentanyl", "violence", "gun", "firearm", "second amendment", "ammunition"]):
        categories.append("crime")
    if any(w in text for w in ["trade", "tariff", "export", "import", "china", "taiwan", "sanction"]):
        categories.append("trade")
    if any(w in text for w in ["technology", "cyber", "internet", "data", "ai ", "artificial intelligence", "computer", "chip", "semiconductor"]):
        categories.append("technology")
    if any(w in text for w in ["infrastructure", "highway", "bridge", "road", "transport", "transit", "rail"]):
        categories.append("infrastructure")
    if any(w in text for w in ["agriculture", "farm", "crop", "farmer", "rural", "food", "rice", "ranch"]):
        categories.append("agriculture")
    if any(w in text for w in ["small business", "entrepreneur", "business loan", "sba"]):
        categories.append("small_business")
    if any(w in text for w in ["native american", "indian", "tribal", "tribe", "reservation"]):
        categories.append("native_americans")
    if any(w in text for w in ["social security", "retirement", "pension", "benefit", "ssi"]):
        categories.append("social_security")
    if any(w in text for w in ["budget", "deficit", "debt", "spending", "appropriation", "funding"]):
        categories.append("budget")
    if any(w in text for w in ["constitution", "amendment", "voting", "election", "ballot", "voter"]):
        categories.append("civil_rights")
    if any(w in text for w in ["abortion", "pregnancy", "pregnant", "unborn", "pro-life", "reproductive"]):
        categories.append("abortion")
    if any(w in text for w in ["china", "chinese", "taiwan", "hong kong", "beijing"]):
        categories.append("china")
    if any(w in text for w in ["water", "drought", "pipeline", "infrastructure", "wastewater"]):
        if "environment" not in categories:
            categories.append("infrastructure")
    # For any bill with a real title, default to "general"
    if "general" not in categories and len(title) > 20:
        categories.append("general")
    
    return categories

# Pros/cons templates by category
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
    "immigration": {
        "pros": ["Strengthens border security and enforces immigration laws.", "Provides a pathway for legal immigration and workforce needs."],
        "cons": ["Could violate due process rights for migrants and asylum seekers.", "May be costly to implement without clear funding."],
    },
    "environment": {
        "pros": ["Protects natural resources and promotes clean energy.", "Reduces pollution and safeguards public health."],
        "cons": ["May impose costly regulations on businesses and industry.", "Federal mandates can preempt state-level innovation."],
    },
    "defense": {
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
    "crime": {
        "pros": ["Takes a strong stance against crime and drug trafficking.", "Protects public safety and supports law enforcement."],
        "cons": ["Could lead to overcriminalization and mass incarceration.", "May infringe on Second Amendment rights."],
    },
    "trade": {
        "pros": ["Protects American workers and domestic industries.", "Promotes fair trade and reciprocity with other nations."],
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
    "budget": {
        "pros": ["Promotes fiscal responsibility and reduces wasteful spending.", "Increases transparency in government budgeting."],
        "cons": ["Could defund essential programs and services.", "May limit government's ability to respond to crises."],
    },
    "civil_rights": {
        "pros": ["Protects voting rights and strengthens election integrity.", "Upholds constitutional freedoms and civil liberties."],
        "cons": ["Could restrict access to the ballot for some voters.", "May increase partisan influence in election administration."],
    },
    "abortion": {
        "pros": ["Protects the sanctity of human life at all stages.", "Supports the constitutional right to bodily autonomy."],
        "cons": ["Could restrict access to essential healthcare services.", "Limits women's reproductive freedom and medical choice."],
    },
    "china": {
        "pros": ["Counteracts China's unfair trade and economic practices.", "Protects American intellectual property and technology."],
        "cons": ["Could escalate tensions with a major world power.", "May disrupt global supply chains and raise prices."],
    },
    "general": {
        "pros": ["Addresses an important policy issue needing legislative action.", "Provides a targeted solution to a specific problem."],
        "cons": ["May have unintended economic consequences across sectors.", "Lacks sufficient detail to fully assess its impact."],
    },
}

def generate_pros_cons(title, summary, policy_area=""):
    """Generate 2 pros and 2 cons for a bill based on its content."""
    cats = classify_bill(title, summary)
    
    # Use the most specific category first
    used = set()
    pros = []
    cons = []
    
    # Also try to use the policy_area
    if policy_area and policy_area.lower() in PROS_CONS:
        cats = [policy_area.lower()] + cats
    
    for cat in cats:
        if cat in PROS_CONS:
            for p in PROS_CONS[cat]["pros"]:
                if p not in used:
                    pros.append(p)
                    used.add(p)
            for c in PROS_CONS[cat]["cons"]:
                if c not in used:
                    cons.append(c)
                    used.add(c)
        if len(pros) >= 2 and len(cons) >= 2:
            break
    
    return pros[:2], cons[:2]

def main():
    print("=" * 60)
    print("STEP 3: Generating pros/cons and merging into cache")
    print("=" * 60)
    
    # Load existing cache
    with open(CACHE_FILE) as f:
        cache = json.load(f)
    print(f"Existing cache: {len(cache)} entries")
    
    # Process each batch
    all_results = {}
    for batch_num in range(3):
        batch_path = f"/tmp/pros_cons_batch_{batch_num}.json"
        if not os.path.exists(batch_path):
            print(f"Batch {batch_num} not found, skipping")
            continue
        
        with open(batch_path) as f:
            batch = json.load(f)
        print(f"\nBatch {batch_num}: {len(batch)} bills")
        
        for key, info in batch.items():
            title = info.get("title", "")
            summary = info.get("summary", "")
            policy_area = info.get("policy_area", "")
            
            # Clean summary
            cleaned = clean_html(summary)
            
            # Generate pros/cons
            pros, cons = generate_pros_cons(title, cleaned, policy_area)
            
            all_results[key] = {
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
        
        print(f"  Generated pros/cons for {len(batch)} bills")
    
    print(f"\nTotal new entries: {len(all_results)}")
    
    # Merge into cache
    before = len(cache)
    for key, value in all_results.items():
        # Add new fields to existing entry, or create new one
        if key in cache:
            existing = cache[key]
            if isinstance(existing, dict):
                existing.update(value)
            else:
                cache[key] = value
        else:
            cache[key] = value
    
    after = len(cache)
    print(f"Cache before: {before}, after: {after}")
    print(f"New keys added: {after - before}")
    print(f"Existing keys updated: {before} (merged fields into existing)")
    
    # Save
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=2)
    print(f"Saved {len(cache)} entries to {CACHE_FILE}")
    
    # Summary stats
    for key in sorted(all_results.keys()):
        v = all_results[key]
        print(f"  {key} | {v['sponsor_name']} | Pros: {v['pros'][0][:50]}... | Cons: {v['cons'][0][:50]}...")
    
    print("\nDone! Pros/cons generated and merged.")
    
    # Save tracking update
    result = {
        "bills_processed": len(all_results),
        "cache_total": len(cache),
        "newly_added": after - before,
        "updated": before,
        "states": ["AR", "AZ"]
    }
    print(f"\nResult: {json.dumps(result)}")

if __name__ == "__main__":
    main()
