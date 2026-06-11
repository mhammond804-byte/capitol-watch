import json, subprocess

# Check who sponsored this bill and when
r = subprocess.run(["curl", "-s", "--max-time", "15", "-H", "X-Api-Key: xH3oHkvJab5BzhnVvJ5zXk3bHK5fPqHZ263Asebc",
                    "https://api.congress.gov/v3/bill/119/hr/9170?format=json"],
                   capture_output=True, text=True)
d = json.loads(r.stdout)
bill = d.get("bill", {})
print("Introduced:", bill.get("introducedDate"))
print("Sponsor:", bill.get("sponsors", [{}])[0].get("fullName"))
print("Title:", bill.get("title"))

# Check latest bills from the capitolwatch API for a couple members
# to see if there are bills more recent than what's cached
members = ["C001095", "W000821", "A000055", "R000575"]
for mid in members:
    r = subprocess.run(["curl", "-s", "--max-time", "15", f"https://capitolwatch.us/api/member/{mid}"],
                       capture_output=True, text=True)
    d = json.loads(r.stdout)
    sponsored = d.get("sponsored", [])
    # Sort by introducedDate desc
    dates = sorted([b.get("introducedDate", "0000") for b in sponsored if b.get("introducedDate")], reverse=True)
    print(f"\n{mid}: latest bills = {dates[:3]}")
