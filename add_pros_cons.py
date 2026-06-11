#!/usr/bin/env python3
"""Fetch summary for bill 119/s/4687 and generate pros/cons, then merge into cache."""
import json, subprocess, os, re
from datetime import datetime

CACHE_PATH = os.path.expanduser("~/Desktop/capitol-watch/bill-analysis.json")
API_KEY = "xH3oHkvJab5BzhnVvJ5zXk3bHK5fPqHZ263Asebc"

# Load cache
with open(CACHE_PATH) as f:
    cache = json.load(f)

# Fetch summary from Congress.gov
url = "https://api.congress.gov/v3/bill/119/s/4687/summaries?format=json"
out = subprocess.run(["curl", "-s", "-H", f"X-Api-Key: {API_KEY}", url], capture_output=True, text=True, timeout=15)
summary_text = "[No summary available - using bill title]"

try:
    data = json.loads(out.stdout)
    summaries = data.get("summaries", [])
    if summaries:
        summary_text = summaries[0].get("text", "")
        # Trim to 300 chars
        if len(summary_text) > 300:
            summary_text = summary_text[:297] + "..."
    else:
        summary_text = "[No summary available - using bill title]"
except:
    summary_text = "[No summary available using Congress.gov API]"

print(f"Summary: {summary_text[:300]}")

# Bill title: "A bill to designate Tiananmen Square Memorial Boulevard in Washington, District of Columbia, and for other purposes."
bill_title = "A bill to designate Tiananmen Square Memorial Boulevard in Washington, District of Columbia, and for other purposes."

# Generate pros and cons based on bill content
pros = [
    "Honors victims of Tiananmen Square by memorializing their struggle for democracy.",
    "Promotes human rights awareness and keeps international attention on China's repression."
]
cons = [
    "May strain diplomatic relations between the U.S. and China.",
    "Symbolic gestures do not change the political situation in China."
]

# Validate character limits
for p in pros:
    assert len(p) <= 120, f"Pro too long: {len(p)} chars - {p}"
for c in cons:
    assert len(c) <= 120, f"Con too long: {len(c)} chars - {c}"

entry = {
    "119/s/4687": {
        "pros": pros,
        "cons": cons,
        "summary": summary_text[:300]
    }
}

# Merge - never overwrite
before = len(cache)
cache.update(entry)
after = len(cache)

print(f"Before: {before}, After: {after}, Added: {after - before}")

# Write back
with open(CACHE_PATH, "w") as f:
    json.dump(cache, f, indent=2)

print("Written to bill-analysis.json")

# Update states tracker
states_log = os.path.expanduser("~/.hermes/logs/capitol_watch_states_done.json")
os.makedirs(os.path.dirname(states_log), exist_ok=True)
with open(states_log, "w") as f:
    json.dump({
        "states": ["DE", "FL"],
        "timestamp": datetime.now().strftime("%Y-%m-%d"),
        "bills_added": after - before,
        "note": f"DE (3 current members) and FL (27 current House + 1 Senator) processed. 1 uncached bill out of 474 total sponsored."
    }, f, indent=2)
print("States tracker updated")
