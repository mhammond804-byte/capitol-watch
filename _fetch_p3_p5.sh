#!/bin/bash
# Fetch additional pages for high-volume members
# Members with 50+ bills: T000278(309), C001095(566), B001236(401),
# P000609(111), S001185(123), A000055(103), R000575(110),
# C001087(143), H001072(148), W000821(92)

for bid in T000278 C001095 B001236 P000609 S001185 A000055 R000575 C001087 H001072 W000821; do
  for page in 3 4 5; do
    offset=$(( (page - 1) * 20 ))
    echo "Fetching $bid page $page (offset=$offset)..."
    curl -s -H "User-Agent: Mozilla/5.0" -o "/tmp/member_${bid}_p${page}.json" "https://capitolwatch.us/api/member/${bid}?offset=${offset}"
    sleep 0.25
  done
done

echo "Done fetching pages 3-5."
