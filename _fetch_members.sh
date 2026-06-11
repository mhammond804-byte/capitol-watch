#!/bin/bash
# Fetch member data for all AL and AR members
MEMBERS=("F000481" "M001212" "S001220" "P000609" "S001185" "A000055" "R000575" "T000278" "B001319" "C001087" "W000821" "H001072" "W000809" "C001095" "B001236")

for bid in "${MEMBERS[@]}"; do
  echo "Fetching $bid..."
  curl -s -H "User-Agent: Mozilla/5.0" -o "/tmp/member_${bid}.json" "https://capitolwatch.us/api/member/${bid}"
  sleep 0.2
done

echo "Done fetching all members."
