import json
with open("/Users/michaelhammond/Desktop/capitol-watch/bill-analysis.json") as f:
    d = json.load(f)
print(f"Total keys: {len(d)}")
c = sum(1 for v in d.values() if isinstance(v, dict) and ("pros" in v or "cons" in v) and (v.get("pros") or v.get("cons")))
print(f"With pros/cons: {c}")
