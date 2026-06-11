#!/usr/bin/env python3
"""Fetch all sponsored bills for DE + FL members and find uncached ones."""
import json, subprocess, os, re, sys

CACHE_PATH = os.path.expanduser("~/Desktop/capitol-watch/bill-analysis.json")

# Load cache
with open(CACHE_PATH) as f:
    cache = json.load(f)

print(f"Cache loaded: {len(cache)} entries")

# Map all cached keys (lowercase) for fast lookup
cached_keys = set(cache.keys())

# All current members for DE (3) and FL (27 house + 1 senator)
members = {
    # DE
    "M001238": "McBride, Sarah (DE-House)",
    "C001088": "Coons, Christopher A. (DE-Senate)",
    "B001303": "Blunt Rochester, Lisa (DE-Senate)",
    # FL House
    "B001314": "Bean, Aaron (FL-House)",
    "B001257": "Bilirakis, Gus M. (FL-House)",
    "B001260": "Buchanan, Vern (FL-House)",
    "C001039": "Cammack, Kat (FL-House)",
    "C001066": "Castor, Kathy (FL-House)",
    "D000600": "Diaz-Balart, Mario (FL-House)",
    "D000032": "Donalds, Byron (FL-House)",
    "D000628": "Dunn, Neal P. (FL-House)",
    "F000484": "Fine, Randy (FL-House)",
    "F000462": "Frankel, Lois (FL-House)",
    "F000472": "Franklin, Scott (FL-House)",
    "F000476": "Frost, Maxwell (FL-House)",
    "G000593": "Gimenez, Carlos A. (FL-House)",
    "H001099": "Haridopolos, Mike (FL-House)",
    "L000597": "Lee, Laurel M. (FL-House)",
    "L000596": "Luna, Anna Paulina (FL-House)",
    "M001199": "Mast, Brian J. (FL-House)",
    "M001216": "Mills, Cory (FL-House)",
    "M001217": "Moskowitz, Jared (FL-House)",
    "P000622": "Patronis, Jimmy (FL-House)",
    "R000609": "Rutherford, John H. (FL-House)",
    "S000168": "Salazar, Maria Elvira (FL-House)",
    "S001200": "Soto, Darren (FL-House)",
    "S001214": "Steube, W. Gregory (FL-House)",
    "W000797": "Wasserman Schultz, Debbie (FL-House)",
    "W000806": "Webster, Daniel (FL-House)",
    "W000808": "Wilson, Frederica S. (FL-House)",
    # FL Senator
    "S001217": "Scott, Rick (FL-Senate)",
}

all_uncached = []
total_bills = 0

for bioguide, name in sorted(members.items()):
    url = f"https://capitolwatch.us/api/member/{bioguide}"
    out = subprocess.run(["curl", "-s", url], capture_output=True, text=True, timeout=15)
    try:
        data = json.loads(out.stdout)
    except:
        print(f"  ERROR parsing response for {bioguide} ({name})")
        continue

    sponsored = data.get("sponsored", [])
    member_bills = 0
    member_uncached = 0
    
    for bill in sponsored:
        congress = bill.get("congress")
        bill_type = bill.get("type")
        number = bill.get("number")
        
        # Skip amendments (type is None)
        if bill_type is None:
            continue
        
        # Only care about 119th Congress bills
        if congress != 119:
            continue
            
        total_bills += 1
        member_bills += 1
        
        key = f"{congress}/{bill_type.lower()}/{number}"
        if key not in cached_keys:
            all_uncached.append({
                "key": key,
                "congress": congress,
                "type": bill_type.lower(),
                "number": number,
                "title": bill.get("title", ""),
                "sponsor": name,
                "bioguide": bioguide
            })
            member_uncached += 1
    
    print(f"  {bioguide} ({name}): {member_bills} bills, {member_uncached} uncached")

print(f"\nTotal: {total_bills} bills, {len(all_uncached)} uncached")

# Save uncached list to a temp file
with open("/tmp/uncached_bills.json", "w") as f:
    json.dump(all_uncached, f, indent=2)

print(f"Saved {len(all_uncached)} uncached bills to /tmp/uncached_bills.json")

# Show first 30 keys
print("\nFirst 30 uncached keys:")
for b in all_uncached[:30]:
    print(f"  {b['key']} - {b['title'][:80]}...")
