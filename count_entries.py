import json
with open("/Users/michaelhammond/Desktop/capitol-watch/bill-analysis.json") as f:
    data = json.load(f)
print(f"Cache entries: {len(data)}")
