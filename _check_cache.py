import json

# Load cache
with open('/Users/michaelhammond/Desktop/capitol-watch/bill-analysis.json') as f:
    cache = json.load(f)

# Check some keys from AR bills
ar_bill_keys = [
    "119/hr/8840", "119/hres/1173", "119/hr/7081",
    "119/hres/821", "119/hr/4776", "119/hres/289",
    "119/hr/1897", "119/hr/1275", "119/hres/90",
    "119/hr/471", "118/hr/10409", "118/hr/9938"
]

for k in ar_bill_keys:
    found = k in cache
    print(f"{k}: {'CACHED' if found else 'UNCACHED'}")

# What about the weird keys - check some that might be in cache
# Look for "118/hr/" patterns
count_118 = sum(1 for k in cache if k.startswith("118/"))
count_119 = sum(1 for k in cache if k.startswith("119/"))
count_100 = sum(1 for k in cache if k.startswith("100/"))
count_99 = sum(1 for k in cache if k.startswith("99/"))
print(f"\nCache breakdown: 100={count_100} 99={count_99} 118={count_118} 119={count_119}")
