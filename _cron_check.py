import json
cache = json.load(open('bill-analysis.json'))
print(f'Cache: {len(cache)} entries')
congress119 = [k for k in cache if k.startswith('119/')]
print(f'119th Congress entries: {len(congress119)}')
# Show sample 119th entries
for k in congress119[:5]:
    print(f'  {k}')
# Count entries by bill type for 119th
from collections import Counter
types = Counter()
for k in congress119:
    parts = k.split('/')
    if len(parts) >= 2:
        types[parts[1]] += 1
for t, c in types.most_common(10):
    print(f'  type {t}: {c}')
