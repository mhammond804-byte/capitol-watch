#!/usr/bin/env python3
"""
Step 1: For each member, fetch their sponsored bills from capitolwatch.us
Only fetch bills that are 119th Congress (current).
"""
import json, sys, os, time

CACHE_FILE = os.path.expanduser("~/Desktop/capitol-watch/bill-analysis.json")

# Load bill cache keys
with open(CACHE_FILE) as f:
    bill_cache = json.load(f)
cached_keys = set(bill_cache.keys())
print(f"Cache has {len(cached_keys)} entries", flush=True)

# Load bioguides
for state in ['MD', 'ME']:
    with open(f'/tmp/cw_{state.lower()}_bioguides.json') as f:
        bioguides = json.load(f)
    
    print(f"\n=== Processing {state}: {len(bioguides)} members ===", flush=True)
    
    for bg in bioguides:
        url = f"https://capitolwatch.us/api/member/{bg}"
        import subprocess
        r = subprocess.run(["curl", "-s", "--max-time", "15", url], capture_output=True, text=True, timeout=20)
        if r.returncode != 0:
            print(f"  ERROR fetching {bg}: curl failed", flush=True)
            continue
        
        try:
            member_data = json.loads(r.stdout)
        except json.JSONDecodeError:
            print(f"  ERROR: bad JSON for {bg}", flush=True)
            continue
        
        # Get sponsored legislation
        sponsored = member_data.get('sponsoredLegislation', {})
        bills = sponsored.get('bill', [])
        
        print(f"  {bg}: {len(bills)} sponsored bills", flush=True)
        
        uncached = []
        for bill in bills:
            congress = str(bill.get('congress', ''))
            bill_type = bill.get('type', '').lower()
            bill_number = str(bill.get('number', ''))
            
            if congress != '119':
                continue
            
            if not bill_type or not bill_number or not congress:
                continue
            
            cache_key = f"{congress}/{bill_type}/{bill_number}"
            
            if cache_key not in cached_keys:
                uncached.append({
                    'cache_key': cache_key,
                    'congress': congress,
                    'type': bill_type,
                    'number': bill_number,
                    'title': bill.get('title', ''),
                    'sponsor_name': member_data.get('name', ''),
                    'sponsor_bioguide': bg,
                    'url': bill.get('url', ''),
                    'state': state
                })
        
        print(f"    -> {len(uncached)} uncached 119th bills", flush=True)
        
        if uncached:
            # Save per-state results
            outfile = f"/tmp/cw_{state.lower()}_uncached.json"
            existing = []
            if os.path.exists(outfile):
                with open(outfile) as f:
                    existing = json.load(f)
            existing.extend(uncached)
            with open(outfile, 'w') as f:
                json.dump(existing, f)
        
        time.sleep(0.5)  # Rate limiting
    
    # Read back and count
    with open(f'/tmp/cw_{state.lower()}_uncached.json') as f:
        all_uncached = json.load(f)
    print(f"  Total uncached for {state}: {len(all_uncached)}", flush=True)
