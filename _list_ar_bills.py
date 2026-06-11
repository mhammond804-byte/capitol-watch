import json, subprocess
# Get ALL sponsored bills for AR members
members_ar = ["W000821","H001072","W000809","C001087","C001095","B001236"]
all_bills_ar = []

for mid in members_ar:
    r = subprocess.run(["curl", "-s", "--max-time", "15", f"https://capitolwatch.us/api/member/{mid}"],
                       capture_output=True, text=True)
    d = json.loads(r.stdout)
    sponsored = d.get("sponsored", [])
    all_bills_ar.extend(sponsored)
    print(f"{mid}: {len(sponsored)} bills")

print(f"\nTotal AR bills: {len(all_bills_ar)}")

# Print all congress/type/number combos
for b in all_bills_ar:
    c = b.get("congress","?")
    t_raw = b.get("type")
    if t_raw is None:
        t = "?"
    else:
        t = str(t_raw).lower()
    n = b.get("number","?")
    key = f"{c}/{t}/{n}".lower()
    print(f"  {key}")
