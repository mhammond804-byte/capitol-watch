import json
import subprocess

# Check the full API response for total counts
for bid, name in [('S001198','Sullivan'), ('M001153','Murkowski'), ('T000278','Tuberville')]:
    result = subprocess.run(['curl', '-s', f'https://capitolwatch.us/api/member/{bid}'], capture_output=True, text=True, timeout=15)
    d = json.loads(result.stdout)
    sponsored = d.get('sponsored', [])
    # Check if there's a member object with count
    member = d.get('member', {})
    leg = member.get('sponsoredLegislation', {})
    count = leg.get('count', 'N/A')
    url = leg.get('url', 'N/A')
    print(f"{name} ({bid}): API returns {len(sponsored)} bills, member count={count}")
    print(f"  Full URL for all bills: {url}")
    
    # Try to get more bills from congress.gov API
    if url and url != 'N/A':
        r2 = subprocess.run(['curl', '-s', url, '-H', 'X-Api-Key: xH3oHkvJab5BzhnVvJ5zXk3bHK5fPqHZ263Asebc'], capture_output=True, text=True, timeout=15)
        try:
            d2 = json.loads(r2.stdout)
            print(f"  Congress.gov total count: {d2}")
        except:
            print(f"  Congress.gov raw: {r2.stdout[:500]}")
