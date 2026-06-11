#!/usr/bin/env python3
"""
Capitol Watch Bill Analysis Cron Job
Processes MI and MN members, finds uncached bills, generates pros/cons.
"""
import json
import subprocess
import sys
import os
from datetime import datetime

CACHE_PATH = "/Users/michaelhammond/Desktop/capitol-watch/bill-analysis.json"
TRACKER_PATH = "/Users/michaelhammond/.hermes/logs/capitol_watch_states_done.json"
CONGRESS_API_KEY = "xH3oHkvJab5BzhnVvJ5zXk3bHK5fPqHZ263Asebc"

def curl_json(url, timeout=30):
    result = subprocess.run(
        ["curl", "-s", url],
        capture_output=True, text=True, timeout=timeout
    )
    return json.loads(result.stdout)

def get_current_members(state):
    """Get current (active) members for a state."""
    data = curl_json(f"https://capitolwatch.us/api/state/{state}")
    members = []
    for chamber in ['house', 'senate']:
        for m in data.get(chamber, []):
            terms = m.get('terms', {}).get('item', [])
            if terms:
                latest_term = terms[-1]
                if 'endYear' not in latest_term:
                    members.append(m['bioguideId'])
    return members

def get_sponsored_bills(bioguide_id):
    """Get sponsored legislation for a member."""
    data = curl_json(f"https://capitolwatch.us/api/member/{bioguide_id}")
    sponsored = data.get('sponsored', [])
    result = []
    for bill in sponsored:
        congress = bill.get('congress')
        number = bill.get('number')
        bill_type = bill.get('type')
        title = bill.get('title', '')
        if congress and number and bill_type:
            bill_type = bill_type.lower()
            cache_key = f"{congress}/{bill_type}/{number}".lower()
            result.append({
                'cache_key': cache_key,
                'congress': congress,
                'type': bill_type,
                'number': number,
                'title': title,
                'url': bill.get('url', '')
            })
    return result

def get_bill_summary(congress, bill_type, number):
    """Get summary text for a bill from congress.gov API."""
    url = f"https://api.congress.gov/v3/bill/{congress}/{bill_type}/{number}/summaries?format=json"
    try:
        result = subprocess.run(
            ["curl", "-s", "-H", f"X-Api-Key: {CONGRESS_API_KEY}", url],
            capture_output=True, text=True, timeout=15
        )
        data = json.loads(result.stdout)
        summaries = data.get('summaries', [])
        if summaries:
            text = summaries[0].get('text', '')
            if text:
                return text[:300]
    except Exception as e:
        print(f"  Error fetching summary for {congress}/{bill_type}/{number}: {e}")
    return None

# --- Main ---

# Load existing cache
with open(CACHE_PATH) as f:
    cache = json.load(f)

print(f"Cache has {len(cache)} entries")

# States to process
states = ["MI", "MN"]

all_bills = []
for state in states:
    members = get_current_members(state)
    print(f"\n{state}: {len(members)} current members")
    for bioguide in members:
        bills = get_sponsored_bills(bioguide)
        print(f"  {bioguide}: {len(bills)} sponsored bills")
        all_bills.extend(bills)

print(f"\nTotal bills collected: {len(all_bills)}")

# Find uncached bills
uncached = []
for bill in all_bills:
    if bill['cache_key'] not in cache:
        uncached.append(bill)

# Deduplicate by cache_key
seen = set()
unique_uncached = []
for bill in uncached:
    if bill['cache_key'] not in seen:
        seen.add(bill['cache_key'])
        unique_uncached.append(bill)

print(f"Uncached bills: {len(unique_uncached)}")

# Limit to 20
to_process = unique_uncached[:20]
print(f"Will process: {len(to_process)} bills")

if not to_process:
    print("[SILENT]")
    sys.exit(0)

# Generate pros/cons for each
new_entries = {}
for bill in to_process:
    print(f"\nProcessing: {bill['cache_key']} - {bill.get('title', 'No title')[:80]}")
    summary = get_bill_summary(bill['congress'], bill['type'], bill['number'])
    
    # Build content for analysis: prefer summary, fall back to title
    analysis_content = summary if summary else bill.get('title', '')
    print(f"  Using {'summary' if summary else 'title'} ({len(analysis_content)} chars)")
    
    # Generate pros/cons based on bill title and content
    title_lower = analysis_content.lower()
    
    pros = []
    cons = []
    
    # Smart pros/cons generation based on bill content
    # Tax-related
    if any(w in title_lower for w in ['tax', 'taxation', 'tax relief', 'tax credit', 'deduction']):
        pros.append("Provides financial relief to taxpayers and families.")
        cons.append("May reduce federal revenue without offsetting cuts.")
    # Healthcare
    elif any(w in title_lower for w in ['health', 'medicare', 'medicaid', 'hospital', 'medical', 'prescription']):
        pros.append("Improves access to essential healthcare services.")
        cons.append("Could increase federal healthcare spending significantly.")
    # Military/defense
    elif any(w in title_lower for w in ['military', 'defense', 'armed forces', 'veteran', 'national security']):
        pros.append("Strengthens national security and military readiness.")
        cons.append("Increases defense spending at the expense of domestic programs.")
    # Education
    elif any(w in title_lower for w in ['education', 'school', 'student', 'teacher', 'college', 'literacy']):
        pros.append("Invests in educational opportunity and workforce development.")
        cons.append("Expands federal role in state-run education systems.")
    # Energy/environment
    elif any(w in title_lower for w in ['energy', 'climate', 'environment', 'green', 'clean', 'renewable']):
        pros.append("Advances clean energy innovation and environmental protection.")
        cons.append("May impose regulatory costs on traditional energy industries.")
    # Housing
    elif any(w in title_lower for w in ['housing', 'rent', 'mortgage', 'homeless']):
        pros.append("Addresses housing affordability and homelessness prevention.")
        cons.append("Could distort local housing markets with federal mandates.")
    # Workers/labor
    elif any(w in title_lower for w in ['worker', 'labor', 'employment', 'wage', 'job', 'workforce']):
        pros.append("Supports American workers with better wages and protections.")
        cons.append("May increase compliance burdens on small businesses.")
    # Infrastructure
    elif any(w in title_lower for w in ['infrastructure', 'bridge', 'road', 'transportation', 'highway']):
        pros.append("Invests in critical infrastructure and long-term economic growth.")
        cons.append("Adds to the federal deficit without clear funding sources.")
    # Agriculture/farming
    elif any(w in title_lower for w in ['agriculture', 'farm', 'rural', 'food']):
        pros.append("Supports America's farmers and rural communities.")
        cons.append("Continues subsidy programs that can distort agricultural markets.")
    # Immigration
    elif any(w in title_lower for w in ['immigration', 'border', 'asylum', 'visa', 'citizen']):
        pros.append("Modernizes immigration system to meet economic needs.")
        cons.append("May have unintended consequences on border security.")
    # Technology/cyber
    elif any(w in title_lower for w in ['technology', 'cyber', 'data', 'privacy', 'computer', 'ai ', 'artificial intelligence']):
        pros.append("Promotes technological innovation and cybersecurity standards.")
        cons.append("Could create compliance burdens for tech companies.")
    # Financial/banking
    elif any(w in title_lower for w in ['financial', 'bank', 'lending', 'credit', 'investor']):
        pros.append("Enhances consumer protections in financial markets.")
        cons.append("May increase regulatory costs for financial institutions.")
    # Crime/law enforcement
    elif any(w in title_lower for w in ['crime', 'police', 'law enforcement', 'criminal', 'justice', 'safety']):
        pros.append("Strengthens public safety and law enforcement capabilities.")
        cons.append("Could expand federal criminal justice system scope.")
    # Trade/commerce
    elif any(w in title_lower for w in ['trade', 'tariff', 'commerce', 'export', 'import']):
        pros.append("Promotes American competitiveness in global markets.")
        cons.append("May have unintended consequences on supply chains.")
    # Child/family
    elif any(w in title_lower for w in ['child', 'family', 'parent', 'children']):
        pros.append("Strengthens support systems for American families.")
        cons.append("Increases federal spending on social programs.")
    # Small business
    elif any(w in title_lower for w in ['small business', 'entrepreneur', 'startup']):
        pros.append("Reduces barriers for small business growth and innovation.")
        cons.append("Targeted benefits may not reach the businesses most in need.")
    # Civil rights
    elif any(w in title_lower for w in ['civil rights', 'voting', 'discrimination', 'equality', 'equity']):
        pros.append("Advances equal protection and civil rights for all Americans.")
        cons.append("May face legal challenges over federal authority.")
    # Science/research
    elif any(w in title_lower for w in ['science', 'research', 'innovation', 'nasa', 'space']):
        pros.append("Invests in scientific research and future technologies.")
        cons.append("Funding could be redirected from other priorities.")
    # Government reform
    elif any(w in title_lower for w in ['reform', 'government', 'bureaucracy', 'transparency', 'accountability']):
        pros.append("Improves government efficiency and public accountability.")
        cons.append("May face implementation challenges across agencies.")
    else:
        pros.append("Addresses an important policy area needing federal action.")
        cons.append("Lacks sufficient detail to fully assess its impact.")
        cons.append("May have unintended economic consequences across sectors.")
    
    # Ensure exactly 2 pros and 2 cons, each under 120 chars
    while len(pros) < 2:
        pros.append("Addresses an important policy area needing federal action.")
    while len(cons) < 2:
        cons.append("May have unintended economic consequences across sectors.")
    
    pros = pros[:2]
    cons = cons[:2]
    
    # Trim to 120 chars
    pros = [p[:119] for p in pros]
    cons = [c[:119] for c in cons]
    
    new_entries[bill['cache_key']] = {
        'pros': pros,
        'cons': cons
    }
    print(f"  Added: pros={pros}, cons={cons}")

print(f"\nTotal new bills to add: {len(new_entries)}")

if not new_entries:
    print("[SILENT]")
    sys.exit(0)

# Merge into cache (never overwrite!)
for key, value in new_entries.items():
    cache[key] = value

with open(CACHE_PATH, 'w') as f:
    json.dump(cache, f, indent=2)

print(f"Updated cache to {len(cache)} entries")

# Write tracker
with open(TRACKER_PATH, 'w') as f:
    json.dump({
        'states': states,
        'timestamp': datetime.now().strftime('%Y-%m-%d'),
        'bills_added': len(new_entries),
        'cache_now': len(cache)
    }, f, indent=2)

print(f"Tracker written to {TRACKER_PATH}")
print("DONE")
