import json, sys

filename = sys.argv[1]
with open(filename) as f:
    data = json.load(f)

# Try 'house' and 'senate' keys
all_members = []
for chamber in ['house', 'senate']:
    for m in data.get(chamber, []):
        bid = m.get('bioguideId')
        if bid:
            all_members.append(bid)

print(f'Members: {len(all_members)}')
for b in all_members:
    print(b)
