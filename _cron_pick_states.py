import json

# All 50 US state codes + DC alphabetically
all_states = ["AK", "AL", "AR", "AZ", "CA", "CO", "CT", "DC", "DE", "FL", "GA", "HI", "IA", "ID", "IL", "IN", "KS", "KY", "LA", "MA", "MD", "ME", "MI", "MN", "MO", "MS", "MT", "NC", "ND", "NE", "NH", "NJ", "NM", "NV", "NY", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VA", "VT", "WA", "WI", "WV", "WY"]

# Last processed: MD and ME
# Find MD and ME positions
print(f"MD at index: {all_states.index('MD')}")
print(f"ME at index: {all_states.index('ME')}")

# The last processed pair was MD/ME. 
# Find the next 2 states after ME alphabetically
me_idx = all_states.index('ME')
if me_idx + 2 < len(all_states):
    next_states = all_states[me_idx+1:me_idx+3]
    print(f"Next 2 states: {next_states}")
else:
    print("Wrapping around to start")
    next_states = all_states[0:2]
    print(f"Next 2 states: {next_states}")
