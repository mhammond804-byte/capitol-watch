#!/usr/bin/env python3
"""Split bills into 3 batches for parallel pros/cons generation."""
import json

with open("/tmp/ready_for_pros_cons.json") as f:
    data = json.load(f)

summaries = data["summaries"]
keys = sorted(summaries.keys())

batches = [keys[i:i+20] for i in range(0, len(keys), 20)]
for i, batch in enumerate(batches):
    batch_data = {k: summaries[k] for k in batch}
    path = f"/tmp/pros_cons_batch_{i}.json"
    with open(path, "w") as f:
        json.dump(batch_data, f, indent=2)
    print(f"Batch {i}: {len(batch)} bills -> {path}")
