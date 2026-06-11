import json, subprocess
r = subprocess.run(["curl", "-s", "--max-time", "15", "-H", "X-Api-Key: xH3oHkvJab5BzhnVvJ5zXk3bHK5fPqHZ263Asebc",
                    "https://api.congress.gov/v3/bill/119/hr/9170?format=json"],
                   capture_output=True, text=True)
d = json.loads(r.stdout)
bill = d.get("bill", {})
print("Title:", bill.get("title", "N/A"))
print("Short Title:", bill.get("shortTitle", "N/A"))
print("Origin Chamber:", bill.get("originChamber", "N/A"))
