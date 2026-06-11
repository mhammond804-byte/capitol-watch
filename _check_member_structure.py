import json, subprocess

# Check full response structure for a member
r = subprocess.run(["curl", "-s", "--max-time", "15", "https://capitolwatch.us/api/member/C001095"],
                   capture_output=True, text=True)
d = json.loads(r.stdout)
print("Top level keys:", list(d.keys()))
print("sponsored count:", len(d.get("sponsored", [])))
print("sponsored type:", type(d.get("sponsored")))
if isinstance(d.get("sponsored"), dict):
    print("Keys:", list(d["sponsored"].keys()))
elif isinstance(d.get("sponsored"), list):
    print("First item keys:", list(d["sponsored"][0].keys()) if d["sponsored"] else "empty")
    # Check for pagination-like fields
    for k in d:
        if k != "sponsored" and k != "member":
            print(f"  Other key '{k}': {json.dumps(d[k])[:200]}")

# Also check if there's a pagenated endpoint
r2 = subprocess.run(["curl", "-s", "--max-time", "15", "https://capitolwatch.us/api/member/C001095?limit=100"],
                    capture_output=True, text=True)
d2 = json.loads(r2.stdout)
print(f"\nWith limit=100: sponsored count = {len(d2.get('sponsored', []))}")
