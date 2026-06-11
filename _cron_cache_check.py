import json

with open('/Users/michaelhammond/Desktop/capitol-watch/bill-analysis.json') as f:
    data = json.load(f)
total = len(data)
keys = list(data.keys())
print(f"TOTAL_ENTRIES:{total}")
print(f"FIRST_KEYS:{keys[:5]}")
print(f"LAST_KEYS:{keys[-5:]}")
for k in keys[:3]:
    entry = data[k]
    print(f"SAMPLE_KEY:{k}|pros:{len(entry.get('pros',[]))}|cons:{len(entry.get('cons',[]))}")
