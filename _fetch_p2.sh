#!/bin/bash
# Fetch additional pages for members with many sponsored bills
# Members with total > 20: M001212(65), S001220(29), P000609(111), S001185(123),
# A000055(103), R000575(110), T000278(309), B001319(54),
# C001087(143), W000821(92), H001072(148), W000809(61),
# C001095(566), B001236(401)

# Offset=20 gets page 2 (items 21-40)
for bid in M001212 S001220 P000609 S001185 A000055 R000575 T000278 B001319 C001087 W000821 H001072 W000809 C001095 B001236; do
  echo "Fetching page 2 for $bid..."
  curl -s -H "User-Agent: Mozilla/5.0" -o "/tmp/member_${bid}_p2.json" "https://capitolwatch.us/api/member/${bid}?offset=20"
  sleep 0.2
done

echo "Done fetching page 2."
