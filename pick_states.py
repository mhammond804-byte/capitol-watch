#!/usr/bin/env python3
"""Find next 2 states after MT and NC alphabetically"""
states = ['AL','AK','AZ','AR','CA','CO','CT','DE','FL','GA','HI','ID','IL','IN','IA','KS','KY','LA','ME','MD','MA','MI','MN','MS','MO','MT','NE','NV','NH','NJ','NM','NY','NC','ND','OH','OK','OR','PA','RI','SC','SD','TN','TX','UT','VT','VA','WA','WV','WI','WY']
sorted_states = sorted(states)
mt_idx = sorted_states.index('MT')
nc_idx = sorted_states.index('NC')
print(f"Sorted states: {sorted_states}")
print(f"MT at index {mt_idx}, NC at index {nc_idx}")
# Next 2 that haven't been done
done = {'MT', 'NC'}
remaining = [s for s in sorted_states if s not in done]
print(f"Next 2: {remaining[:2]}")
