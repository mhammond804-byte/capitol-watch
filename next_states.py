#!/usr/bin/env python3
"""Find next 2 states alphabetically after the ones already done."""
import json, os

states = ['AK','AL','AR','AZ','CA','CO','CT','DE','FL','GA','HI','IA','ID','IL','IN','KS','KY','LA','MA','MD','ME','MI','MN','MO','MS','MT','NC','ND','NE','NH','NJ','NM','NV','NY','OH','OK','OR','PA','RI','SC','SD','TN','TX','UT','VA','VT','WA','WI','WV','WY']

log_path = os.path.expanduser('~/.hermes/logs/capitol_watch_states_done.json')
if os.path.exists(log_path):
    with open(log_path) as f:
        log = json.load(f)
else:
    log = {"states": []}

done = log.get("states", [])
print(f"Previously done: {done}")

# Find the last done state's position in the alphabetical list
last_done_idx = -1
for s in done:
    if s in states:
        idx = states.index(s)
        if idx > last_done_idx:
            last_done_idx = idx

print(f"Last done state index: {last_done_idx} ({states[last_done_idx] if last_done_idx >= 0 else 'none'})")

# Next 2 states after the last done one
start = last_done_idx + 1
if start >= len(states):
    start = 0  # wrap around

next_two = states[start:start+2]
if len(next_two) < 2:
    # Wrap around
    next_two = states[start:] + states[:2 - len(next_two)]

print(f"Next 2: {next_two}")
