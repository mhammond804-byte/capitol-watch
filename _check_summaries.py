import json

# Check summaries
for fname, label in [('/tmp/summary_119_s_4692.json', '119/s/4692'), ('/tmp/summary_119_s_4673.json', '119/s/4673')]:
    with open(fname) as f:
        data = json.load(f)
    summaries = data.get('summaries', [])
    print(f"\n=== {label} ===")
    print(f"Number of summaries: {len(summaries)}")
    if summaries:
        for s in summaries:
            text = s.get('text', '')
            action = s.get('actionType', '')
            print(f"  Action: {action}")
            print(f"  Text: {text[:300]}")
            print()
    else:
        # Check structure
        print(f"  Keys: {list(data.keys())}")
        for k, v in data.items():
            if isinstance(v, dict):
                print(f"  {k}: {list(v.keys())}")
            elif isinstance(v, list):
                print(f"  {k}: {len(v)} items")
            else:
                print(f"  {k}: {v}")
