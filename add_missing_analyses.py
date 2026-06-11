import json

with open('/Users/michaelhammond/Desktop/capitol-watch/bill-analysis.json') as f:
    cache = json.load(f)

new_entries = {}

# SRES 12
new_entries["119/sres/12"] = {
    "pros": ["• Notifies the President that the Senate has elected a Sergeant at Arms and Doorkeeper, ensuring the Senate\'s internal leadership is properly communicated to the executive branch.", "• This is a routine procedural step that keeps the legislative and executive branches coordinated on Senate administration."],
    "cons": ["• This is a purely administrative resolution with no direct impact on legislation or public policy.", "• Does not address any substantive policy issue affecting constituents."]
}
new_entries["119/sres/11"] = {
    "pros": ["• Elects Jennifer A. Hemingway as Sergeant at Arms and Doorkeeper, providing the Senate with a key security and administrative leader.", "• A permanent Sergeant at Arms ensures continuity of Senate security operations and building management."],
    "cons": ["• This is a procedural personnel resolution with no direct legislative impact.", "• Does not address any policy issues or constituent concerns."]
}
new_entries["119/sres/9"] = {
    "pros": ["• Notifies the President of the election of a Secretary of the Senate, ensuring proper communication between legislative and executive branches.", "• The Secretary of the Senate is a key administrative role responsible for records, payroll, and daily operations."],
    "cons": ["• Purely procedural resolution with no policy substance or legislative impact.", "• Does not address constituent needs or national issues."]
}
new_entries["119/sres/8"] = {
    "pros": ["• Elects Jackie Barber as Secretary of the Senate, filling an essential administrative leadership position.", "• A permanent Secretary of the Senate provides stability for Senate record-keeping and administrative functions."],
    "cons": ["• This is a personnel resolution with no direct impact on legislation or public policy.", "• Does not address any substantive policy matters."]
}
new_entries["119/sres/7"] = {
    "pros": ["• Sets a fixed daily meeting time for the Senate, providing predictability for senators, staff, and the public.", "• A consistent schedule helps the public know when to expect Senate proceedings and floor votes."],
    "cons": ["• This is an internal procedural resolution on scheduling, not a policy measure.", "• A fixed meeting time may not accommodate the flexible schedules needed for complex legislative negotiations."]
}
new_entries["119/sres/6"] = {
    "pros": ["• Recognizes Senator Patty Murray\'s service as President pro tempore, honoring a career of public service.", "• Such resolutions promote bipartisan goodwill and acknowledge the contributions of elected officials."],
    "cons": ["• This is a ceremonial resolution with no legislative or policy effect.", "• Does not address any specific constituent needs or national issues."]
}
new_entries["119/sres/4"] = {
    "pros": ["• Formally notifies the President of the election of a President pro tempore, ensuring proper inter-branch communication.", "• The President pro tempore is a constitutionally recognized role that provides Senate leadership continuity."],
    "cons": ["• This is a procedural notification resolution with no policy substance.", "• Does not affect legislation or address public needs."]
}
new_entries["119/sres/3"] = {
    "pros": ["• Elects Senator Charles E. Grassley as President pro tempore, bringing decades of institutional experience to the role.", "• The President pro tempore is third in the presidential line of succession, making this an important constitutional function."],
    "cons": ["• This is a personnel election resolution with no direct legislative or policy impact.", "• Does not address any substantive issues facing constituents."]
}
new_entries["119/sres/13"] = {
    "pros": ["• Notifies the House of Representatives of the Senate\'s election of a Sergeant at Arms, ensuring inter-chamber communication.", "• Proper coordination between the House and Senate on leadership positions supports smooth legislative operations."],
    "cons": ["• This is an inter-chamber notification resolution with no policy substance.", "• Does not affect legislation or address public concerns."]
}
new_entries["119/sres/10"] = {
    "pros": ["• Notifies the House of Representatives of the election of a Secretary of the Senate, maintaining proper communication between chambers.", "• Inter-chamber coordination on administrative appointments helps both bodies function smoothly."],
    "cons": ["• This is a procedural notification with no policy content.", "• Does not address constituent needs or national issues."]
}
new_entries["119/sres/5"] = {
    "pros": ["• Notifies the House of Representatives of the election of a President pro tempore, ensuring proper inter-chamber communication.", "• Keeps the House informed of Senate leadership to facilitate joint legislative activities."],
    "cons": ["• This is a procedural notification resolution with no substantive policy impact.", "• Does not affect legislation or public policy."]
}
new_entries["119/sres/2"] = {
    "pros": ["• Formally informs the House of Representatives that a quorum of the Senate is assembled, a constitutional requirement for conducting business.", "• This resolution is part of the procedural foundation that allows the Senate to begin its legislative work."],
    "cons": ["• This is an administrative procedural resolution required for the Senate to organize, with no policy content.", "• Does not address any legislative issues or constituent concerns."]
}
new_entries["119/hres/14"] = {
    "pros": ["• Appoints members to House standing committees, which is essential for the committee system to function and legislation to be properly reviewed.", "• Committee assignments determine which members will specialize in specific policy areas, improving the quality of legislative oversight."],
    "cons": ["• This is an internal organizational resolution with no direct policy impact.", "• Committee assignments are often based on party leadership decisions rather than merit or expertise."]
}
new_entries["119/hr/215"] = {
    "pros": ["• Aims to improve the adoption process, potentially reducing wait times and bureaucratic hurdles for families seeking to adopt.", "• Helps find permanent homes for children in foster care, improving outcomes for vulnerable youth."],
    "cons": ["• May impose new federal requirements on state adoption systems without providing additional funding to implement them.", "• Federal involvement in adoption could create conflicts with state family law and existing adoption procedures."]
}
new_entries["119/hres/15"] = {
    "pros": ["• Rescinds subpoenas from the January 6th Select Committee, which some argue exceeded their authority or were politically motivated.", "• Protects individuals from potential overreach by congressional investigative committees."],
    "cons": ["• Could hinder ongoing investigations into the January 6th Capitol breach and efforts to prevent future attacks on democratic institutions.", "• Rescinding subpoenas may set a precedent that makes it harder for future congressional investigations to compel testimony."]
}
new_entries["119/hjres/12"] = {
    "pros": ["• Would establish term limits for Supreme Court justices, ensuring regular turnover and preventing any single president from shaping the court for decades.", "• Regular appointments could make the confirmation process less politically charged by reducing the stakes of each nomination."],
    "cons": ["• Amending the Constitution is an extremely difficult process requiring two-thirds of both chambers and three-fourths of states.", "• Term limits could reduce judicial independence by making justices worry about post-court career prospects."]
}
new_entries["119/hr/214"] = {
    "pros": ["• Returns greater autonomy to the District of Columbia over its local laws and governance, reflecting principles of democratic self-rule.", "• D.C. residents pay federal taxes but lack full voting representation in Congress — this bill addresses that imbalance."],
    "cons": ["• The Constitution gives Congress authority over the federal district — critics argue D.C. home rule requires a constitutional amendment.", "• Could create conflicts between D.C. laws and federal interests in the nation\'s capital."]
}
new_entries["119/hr/212"] = {
    "pros": ["• Honors the history and significance of the U.S. Capitol building, preserving its legacy for future generations.", "• Supports educational programs and commemorative activities that strengthen civic understanding of American democracy."],
    "cons": ["• May authorize federal spending for commemorative activities that some consider non-essential.", "• Could overlap with existing preservation and educational programs already run by the Architect of the Capitol."]
}
new_entries["119/hres/16"] = {
    "pros": ["• Sends a clear diplomatic message that the United States condemns Russia\'s actions in Ukraine as genocide, putting moral pressure on the international community.", "• Recognizes the severity of atrocities committed during the war, affirming support for the Ukrainian people."],
    "cons": ["• This is a non-binding resolution with no legal force — it expresses congressional opinion but does not change policy or funding.", "• Labeling the conflict a genocide could complicate future diplomatic negotiations to end the war."]
}
new_entries["119/hres/13"] = {
    "pros": ["• Appoints members to House committees, enabling the committee system to review legislation and conduct oversight.", "• Committee assignments allow representatives to develop expertise in specific policy areas, benefiting the legislative process."],
    "cons": ["• This is an internal organizational resolution with no direct policy or legislative effect.", "• Committee assignments may be influenced more by party loyalty than individual expertise."]
}
new_entries["119/hr/213"] = {
    "pros": ["• Prohibits federal funding for a specific high-speed rail project, preventing what some view as wasteful government spending.", "• Redirects federal dollars away from a project that critics argue has questionable economic viability."],
    "cons": ["• Restricting federal funding for specific infrastructure projects limits the ability of states and regions to develop modern transportation systems.", "• High-speed rail could provide long-term economic and environmental benefits that outweigh initial costs."]
}
new_entries["119/hr/233"] = {
    "pros": ["• Helps pets and their owners access veterinary care and support services, improving animal welfare and public health.", "• Supports pet ownership, which has been shown to provide mental and physical health benefits for people."],
    "cons": ["• May create new federal programs or mandates that could be costly without clear federal responsibility for pet welfare.", "• Could overlap with existing state and local animal welfare programs."]
}
new_entries["119/hr/221"] = {
    "pros": ["• Eliminates the Bureau of Alcohol, Tobacco, Firearms and Explosives (ATF), which critics argue has overstepped its authority and infringed on Second Amendment rights.", "• Reduces the size of the federal bureaucracy and potentially saves taxpayer money."],
    "cons": ["• The ATF plays a crucial role in enforcing federal firearms laws, combating gun trafficking, and investigating explosives-related crimes.", "• Abolishing the ATF without a replacement agency could create gaps in federal law enforcement that impact public safety."]
}
new_entries["119/hres/20"] = {
    "pros": ["• Creates a select committee focused on electoral reform, which could address concerns about voting access, election security, and campaign finance.", "• A dedicated committee allows Congress to study election issues in depth and develop bipartisan reform proposals."],
    "cons": ["• Select committees can become partisan battlegrounds rather than productive reform vehicles.", "• Could duplicate the work of existing committees like House Administration that already oversee elections."]
}
new_entries["119/hr/237"] = {
    "pros": ["• Protects pets and animals from harm by strengthening penalties for animal cruelty or improving animal welfare standards.", "• Addresses growing public concern about animal welfare and pet safety."],
    "cons": ["• Federal animal welfare legislation may overlap with existing state laws, creating enforcement confusion.", "• Could impose regulatory burdens on pet owners, breeders, or animal businesses."]
}
new_entries["119/s/5"] = {
    "pros": ["• Named after Laken Riley, this bill strengthens immigration enforcement by requiring detention of undocumented immigrants charged with certain crimes.", "• Aims to prevent violent crimes by ensuring individuals accused of theft and other offenses are held pending proceedings."],
    "cons": ["• Mandatory detention could lead to overcrowding in immigration facilities and increase costs for the immigration system.", "• May apply to individuals who have not been convicted of a crime, raising due process concerns."]
}
new_entries["119/hr/211"] = {
    "pros": ["• Ensures women veterans have access to contraception through the VA, addressing a specific healthcare need for the growing female veteran population.", "• Improves comprehensive healthcare for veterans by covering reproductive health services."],
    "cons": ["• May increase VA healthcare costs that need to be funded through additional appropriations.", "• Some argue contraception coverage should be handled through private insurance rather than the VA system."]
}
new_entries["119/hr/219"] = {
    "pros": ["• Addresses a specific healthcare gap for women veterans by improving menopause care through the VA healthcare system.", "• Recognizes that the veteran population is increasingly female and requires targeted healthcare services."],
    "cons": ["• Expanding VA healthcare services for specific conditions requires additional funding that may not be appropriated.", "• Could create an uneven standard of care between male and female veterans for gender-specific health issues."]
}
new_entries["119/hr/224"] = {
    "pros": ["• Helps disabled veterans afford housing by providing additional support and benefits, addressing homelessness and housing instability among veterans.", "• Recognizes the sacrifices of disabled veterans by ensuring they have access to stable, accessible housing."],
    "cons": ["• Housing support programs require sustained federal funding that may not be guaranteed in future budgets.", "• Could overlap with existing VA housing assistance programs, creating administrative complexity."]
}
new_entries["119/hr/210"] = {
    "pros": ["• Provides dental care benefits to veterans through the VA, addressing a significant gap in current veteran healthcare coverage.", "• Dental health is linked to overall health — poor dental care can lead to serious medical conditions."],
    "cons": ["• Adding dental benefits to VA healthcare would require substantial new funding that Congress would need to appropriate.", "• Could increase wait times for other VA medical services if resources are stretched."]
}

# Merge new entries
count = 0
for key, value in new_entries.items():
    if key not in cache:
        cache[key] = value
        count += 1

with open('/Users/michaelhammond/Desktop/capitol-watch/bill-analysis.json', 'w') as f:
    json.dump(cache, f, indent=2, ensure_ascii=False)

print(f"Added {count} new bill analyses")
print(f"Total in cache now: {len(cache)}")

with open('/Users/michaelhammond/Desktop/capitol-watch/public/index.html', 'r') as f:
    html = f.read()

# Check if the server needs restarting to pick up changes (it reloads every 5 min)
print("Server reloads cache every 5 minutes (setInterval 300000ms)")
print("Changes will be visible within 5 minutes")
