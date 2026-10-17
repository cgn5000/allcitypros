"""Editorial content for the city x service guides.

Rules for this file (keep it honest):
- Cost figures are NATIONAL ballparks, labelled as such on every page. Never present them as local quotes.
- No ratings, review counts, business names, or claims about specific companies.
- No claims about incentives that change often (e.g. solar credits) -- point readers to current sources.
"""

# climate region by state (coarse; used only for general seasonal guidance)
REGION = {}
for s in "FL LA MS AL GA SC TX AR HI".split(): REGION[s] = "hot_humid"
for s in "NC VA MD DE DC KY TN OK MO KS WV".split(): REGION[s] = "mixed"
for s in "AZ NV NM".split(): REGION[s] = "hot_dry"
for s in "WA OR CA".split(): REGION[s] = "mild"
for s in ("MN WI MI ND SD NE IA IL IN OH PA NY NJ CT MA RI VT NH ME MT WY CO ID UT AK").split(): REGION[s] = "cold"

STATE_NAMES = {
 "AL":"Alabama","AK":"Alaska","AZ":"Arizona","AR":"Arkansas","CA":"California","CO":"Colorado","CT":"Connecticut",
 "DE":"Delaware","DC":"Washington, D.C.","FL":"Florida","GA":"Georgia","HI":"Hawaii","ID":"Idaho","IL":"Illinois",
 "IN":"Indiana","IA":"Iowa","KS":"Kansas","KY":"Kentucky","LA":"Louisiana","ME":"Maine","MD":"Maryland",
 "MA":"Massachusetts","MI":"Michigan","MN":"Minnesota","MS":"Mississippi","MO":"Missouri","MT":"Montana",
 "NE":"Nebraska","NV":"Nevada","NH":"New Hampshire","NJ":"New Jersey","NM":"New Mexico","NY":"New York",
 "NC":"North Carolina","ND":"North Dakota","OH":"Ohio","OK":"Oklahoma","OR":"Oregon","PA":"Pennsylvania",
 "RI":"Rhode Island","SC":"South Carolina","SD":"South Dakota","TN":"Tennessee","TX":"Texas","UT":"Utah",
 "VT":"Vermont","VA":"Virginia","WA":"Washington","WV":"West Virginia","WI":"Wisconsin","WY":"Wyoming",
}
NO_WAGE_TAX = {"AK","FL","NV","SD","TN","TX","WA","WY","NH"}

REGION_LABEL = {
 "hot_humid": "hot, humid summers and mild winters",
 "mixed": "four distinct seasons with hot, humid summers and cool winters",
 "hot_dry": "very hot, dry summers and mild winters",
 "mild": "a mild climate, with hotter summers inland",
 "cold": "cold winters, snow or hard freezes, and warm summers",
}

# climate-specific local notes, by category key then region
CLIMATE = {
 "hvac": {
  "hot_humid": "Air conditioning runs most of the year in {state}'s climate, so cooling capacity, humidity control and condensate drain maintenance matter more than heating. Ask any installer for a load calculation (Manual J) rather than sizing by square footage alone.",
  "mixed": "{state} homes need both a dependable air conditioner and a heating system. Heat pumps are a common option in this climate; ask installers to compare a heat pump with a conventional furnace and AC for your home.",
  "hot_dry": "Cooling dominates in {state}: dust, extreme heat and long run-times shorten equipment life. Ask about filter changes, coil cleaning and whether the system is rated for high outdoor temperatures.",
  "mild": "With a milder climate, many {state} homes run heating and cooling less often, which makes efficiency upgrades slower to pay back. Heat pumps and ductless systems are worth pricing alongside traditional equipment.",
  "cold": "Heating reliability is the priority in {state}. Schedule furnace or boiler service before the first hard freeze, and ask about sizing, venting and backup options if your system fails in a cold snap.",
 },
 "plumbing": {
  "hot_humid": "Warm, humid conditions in {state} can speed corrosion and encourage slow leaks under sinks and around water heaters. A yearly look at supply lines and the water heater is cheap insurance.",
  "mixed": "Occasional hard freezes in {state} can burst exposed pipes. Insulate outdoor spigots and pipes in unheated spaces and know where your main shutoff is.",
  "hot_dry": "Hard water is common in dry climates and builds scale in water heaters and fixtures. Ask a plumber about softening or periodic water-heater flushing.",
  "mild": "Milder weather in {state} means fewer freeze-related breaks, but older homes may still have aging galvanized or polybutylene pipe worth having inspected.",
  "cold": "Frozen and burst pipes are the signature plumbing risk in {state}. Insulate exposed lines, disconnect hoses before winter and keep your main shutoff easy to reach.",
 },
 "electrical": {
  "hot_humid": "Storms and humidity in {state} put surge protection, GFCI protection and weatherproof outdoor wiring near the top of the list.",
  "mixed": "Older {state} homes often have outdated panels or ungrounded outlets. A licensed electrician can inspect the panel and recommend upgrades before you add big loads like an EV charger.",
  "hot_dry": "Heavy air-conditioning load strains older panels in {state}. If breakers trip in summer, ask for a load assessment.",
  "mild": "Many {state} homeowners are adding EV chargers, heat pumps or solar, which can require a panel upgrade. Get a load calculation before buying equipment.",
  "cold": "Heating loads, space heaters and holiday lighting raise winter demand in {state}. Have the panel inspected if breakers trip or lights flicker.",
 },
 "roofing": {
  "hot_humid": "Intense sun, heavy rain and wind-driven storms are the main stressors on {state} roofs. Ask about wind-rated shingles, proper underlayment and ventilation, and photograph storm damage before calling your insurer.",
  "mixed": "{state} roofs see hail, wind, heat and freeze-thaw cycles. After a storm, get an independent inspection before signing anything with a contractor who knocked on your door.",
  "hot_dry": "Heat and UV are brutal on roofing in {state}. Ask about reflective or tile/metal options and how the contractor handles ventilation and underlayment in extreme heat.",
  "mild": "Rain, moss and algae are common roof issues in parts of {state}; inland areas add heat stress. Ask about moss-resistant materials and proper flashing and drainage.",
  "cold": "Snow load, ice dams and freeze-thaw damage drive roofing work in {state}. Attic insulation and ventilation are as important as the shingles themselves.",
 },
 "landscaping": {
  "hot_humid": "Warm-season grasses, heavy summer rain and a long growing season shape lawn care in {state}. Ask about turf varieties suited to your area, drainage and irrigation scheduling.",
  "mixed": "{state} lawns often use cool- and warm-season grasses depending on the region. Fall is a strong time for overseeding and planting.",
  "hot_dry": "Water is the central issue in {state}. Ask about drought-tolerant plantings, drip irrigation and local watering restrictions.",
  "mild": "Plant choices in {state} vary widely between coastal and inland areas. Ask about native, low-water plants and local irrigation rules.",
  "cold": "Short growing seasons and winter damage shape landscaping in {state}. Ask about hardy plant selections, snow-removal plans and spring and fall cleanups.",
 },
 "painting": {
  "hot_humid": "Humidity and strong sun in {state} affect how exterior paint cures and lasts. Ask about mildew-resistant primers, surface prep and painting during lower-humidity windows.",
  "mixed": "Exterior painting in {state} is best scheduled for stable spring or fall weather, when temperatures stay within the paint manufacturer's range.",
  "hot_dry": "Intense sun and heat in {state} fade and crack paint quickly. Ask about UV-resistant finishes and avoiding application on hot surfaces.",
  "mild": "Damp conditions in parts of {state} make surface prep and moisture control essential for exterior paint that lasts.",
  "cold": "Painting seasons are short in {state}. Exterior work needs a stretch of warm, dry days, so book early for summer.",
 },
 "flooring": {
  "hot_humid": "Humidity in {state} can cause solid hardwood to cup or swell. Many homeowners choose luxury vinyl plank, tile or engineered wood and ask installers about moisture testing.",
  "mixed": "Seasonal humidity swings in {state} move wood floors. Ask installers about acclimation time and subfloor moisture checks.",
  "hot_dry": "Tile and hard-surface floors are popular in {state}'s heat. Ask about subfloor prep and expansion gaps for large rooms.",
  "mild": "Moisture control and subfloor condition matter for flooring in many {state} homes. Ask for a moisture reading before installation.",
  "cold": "Dry indoor winter air in {state} can shrink wood flooring and open gaps. Ask about humidity control, and consider heated-floor-compatible products if you want radiant heat.",
 },
 "pool_spa": {
  "hot_humid": "Pools in {state} can be used much of the year, but heat, rain and algae mean steady chemical balancing and filter care.",
  "mixed": "Pool season in {state} is limited, so opening and closing services matter. Ask what is included in each and how winterizing is handled.",
  "hot_dry": "Evaporation and heat in {state} make water balance and equipment efficiency important. Ask about variable-speed pumps and covers.",
  "mild": "Many {state} pools run for a long season; ask about leaf and debris management and water-use rules.",
  "cold": "Short pool seasons in {state} mean opening, closing and winterizing are the key service calls. Improper winterizing can crack plumbing and equipment.",
 },
 "pest_control": {
  "hot_humid": "Warm, humid conditions in {state} favor termites, ants, roaches and mosquitoes nearly year-round. Ask about a termite inspection and a recurring plan rather than one-off sprays.",
  "mixed": "Pest pressure in {state} follows the seasons: ants and termites in spring, rodents when it cools. Ask for a plan that matches the season.",
  "hot_dry": "Scorpions, ants and roaches are common concerns in dry climates like {state}'s. Ask which pests the company actually treats and how often.",
  "mild": "Damp conditions in parts of {state} attract ants, termites and rodents. Moisture control around the home reduces pest pressure.",
  "cold": "Rodents and overwintering insects move indoors as {state} temperatures fall. Seal entry points before the first freeze.",
 },
 "solar_energy": {
  "hot_humid": "Strong sun makes solar attractive in {state}, but summer storms and heat affect system design. Ask about roof condition, wind ratings and how net metering works with your utility.",
  "mixed": "Solar economics in {state} depend heavily on your utility's net-metering rules and your roof. Get multiple proposals and compare the same assumptions across each.",
  "hot_dry": "Abundant sunshine in {state} helps production, while high heat slightly lowers panel efficiency. Compare proposals on production estimates and utility rate structure.",
  "mild": "Solar value in {state} depends on your utility's rates and export rules. Ask each installer to explain how credits for excess power are calculated.",
  "cold": "Panels still produce in cold weather, and snow usually slides off tilted arrays. The key variables in {state} are roof orientation, utility rules and shading.",
 },
 "moving": {
  "hot_humid": "Summer moves in {state} mean heat and humidity; book early morning slots and ask how the crew protects furniture and electronics from heat and moisture.",
  "mixed": "Peak moving season in {state} runs late spring through summer. Booking several weeks ahead usually gives better dates and pricing.",
  "hot_dry": "Extreme midday heat in {state} makes early-morning moves safer and more comfortable. Ask about moving fragile items like electronics and candles in the heat.",
  "mild": "Moving in {state} is feasible most of the year, though rain can matter on the coast. Ask how crews protect belongings in wet weather.",
  "cold": "Winter moves in {state} can mean snow and ice. Ask about weather policies, and book early for summer when demand peaks.",
 },
 "home_security": {
  "hot_humid": "Storm-related power and internet outages are common in {state}. Ask whether your system has battery and cellular backup.",
  "mixed": "Compare wired and wireless systems for your home. Ask about cellular backup so the system keeps working if internet service drops.",
  "hot_dry": "Extreme heat can affect outdoor cameras and batteries. Ask about operating temperature ratings and wired options.",
  "mild": "Many {state} households choose DIY or hybrid systems. Compare monitoring contracts, equipment ownership and cancellation terms.",
  "cold": "Cold weather drains batteries in outdoor devices. Ask about low-temperature ratings and wired power for exterior cameras in {state}.",
 },
 "handyman": {
  "hot_humid": "Humidity-related repairs are common in {state}: caulking, sticking doors, mildew and soft trim. A handyman can handle many of these, but wiring, gas and structural work need a licensed trade.",
  "mixed": "Seasonal wear shows up in weatherstripping, gutters and exterior trim in {state}. Ask what a handyman is permitted to do in your area.",
  "hot_dry": "Sun and dryness crack caulk, trim and weatherstripping in {state}. Regular exterior touch-ups prevent bigger repairs.",
  "mild": "Moisture around windows and exterior trim is the usual culprit for repairs in much of {state}. Fix small leaks early.",
  "cold": "Winter damage to doors, windows and weatherstripping drives spring repair lists in {state}. Seasonal checkups save energy and repairs.",
 },
 "general_contracting": {
  "hot_humid": "Moisture control, ventilation and storm-resistant construction matter for remodels in {state}. Ask how the contractor manages permits and inspections.",
  "mixed": "Remodeling in {state} typically involves local permits and inspections. Ask the contractor to pull permits in their own name.",
  "hot_dry": "Heat affects scheduling and materials in {state}; ask how the crew plans exterior work during extreme temperatures.",
  "mild": "Permit and inspection timelines in {state} vary by city. Ask how long permits currently take before you set a schedule.",
  "cold": "Construction seasons in {state} are shaped by winter. Ask how weather delays are handled in the contract.",
 },
}

# categories that use state-based (not climate) local notes
def local_note(key, city, state_abbr):
    st = STATE_NAMES[state_abbr]
    if key == "accounting":
        if state_abbr in NO_WAGE_TAX:
            return f"{st} does not tax wage income at the state level, so many individual returns are simpler, but business, sales-tax and local filings can still apply. Confirm what your situation requires."
        return f"{st} levies a state income tax, so most returns involve both federal and {st} filings. Ask any preparer how they handle state and local returns, and whether they are comfortable with multi-state situations."
    if key == "legal":
        return f"Attorneys practicing in {st} must be licensed by {st}. Check the lawyer's status with the {st} state bar or the state's attorney-lookup tool before you hire, and ask whether they regularly handle your type of matter in {city}-area courts."
    if key == "mortgage":
        return f"Property taxes, insurance costs and closing costs vary across {st} and even between counties around {city}. Ask each lender to estimate escrow for the specific property and compare written Loan Estimates side by side."
    if key == "digital_marketing":
        return f"For a {city} business, local visibility (Google Business Profile, local citations and reviews) often matters more than national SEO. Ask any agency to show results for businesses in {city}-sized markets and to explain exactly what they will do each month."
    if key == "it_services":
        return f"Ask whether a provider can offer on-site support in the {city} area when remote fixes are not enough, and how quickly they respond. Compare their backup, security and recovery practices, not just the monthly price."
    if key == "tutoring":
        return f"Students in {st} follow state academic standards and often take state assessments. Ask tutors about their experience with {st} standards and with your child's specific course or test."
    if key == "pet_services":
        return f"Pet licensing, vaccination and leash rules vary by city and county. Check with {city} animal services for local requirements, and ask providers about vaccination requirements and emergency plans."
    if key == "personal_training":
        return f"{city} offers options from gyms to outdoor and in-home training. Ask trainers about their certification, their experience with your goals and how they handle injuries and progress tracking."
    if key == "auto_repair":
        return f"Vehicle inspection and emissions rules differ across {st}, and sometimes by county. Check what applies to your vehicle, and ask shops whether they perform required inspections and provide written estimates first."
    if key == "residential_cleaning":
        return f"Ask any {city} cleaning company whether its cleaners are employees or contractors, what insurance it carries and what is included in a standard visit versus a deep clean. Scope differences explain most price differences."
    return ""

CATS = {
 "hvac": dict(label="HVAC", noun="HVAC contractor", cost=[
   ("Seasonal tune-up / inspection","$80 – $200"),("Typical AC or heating repair","$150 – $650"),
   ("Central AC replacement","$5,000 – $12,000"),("Furnace or heat pump replacement","$3,500 – $10,000"),
   ("Ductwork repair or sealing","$300 – $2,000")],
   intro="Heating and cooling is one of the biggest systems — and expenses — in any home. This guide explains what HVAC work typically costs, how to compare contractors in {city}, and what to ask before you sign.",
   steps=["Describe the problem clearly (no cooling, short-cycling, uneven rooms, high bills) and note the age and brand of your equipment.","Get at least three written estimates. For replacements, insist on a load calculation, not a rule-of-thumb size.","Compare equipment model numbers, efficiency ratings (SEER2/AFUE), warranty terms and what is included (permits, disposal, thermostat, duct work).","Verify license, insurance and, for refrigerant work, EPA 608 technician certification.","Get everything in writing, including start date, payment schedule and warranty, before work begins."],
   questions=["Will you perform a load calculation (Manual J) for my home?","Are you licensed in {state}, and can I see proof of insurance?","Which parts and labor are covered by warranty, and for how long?","Are permits included in the price?","Can you quote repair versus replace so I can compare?"],
   red=["Pressure to decide today or 'special pricing' that expires immediately.","A replacement quote with no load calculation or equipment model numbers.","Large cash deposits or payment demanded up front in full.","No license number or proof of insurance when asked."],
   lic="Most states and many cities license HVAC contractors, and technicians who handle refrigerant must hold EPA Section 608 certification. Verify the contractor's license with the {state} licensing authority before work begins.",
   timing="Book tune-ups in spring (cooling) and fall (heating). Replacements are easier to schedule and negotiate in shoulder seasons than during a heat wave or cold snap.",
   faq=[("How much does HVAC repair cost?","Minor repairs such as a capacitor or refrigerant top-up commonly run a few hundred dollars, while compressor or coil replacements can exceed $1,500. Get a written estimate and compare it to the age of the system."),
        ("How often should I service my system?","Many manufacturers recommend a professional check once or twice a year — cooling in spring, heating in fall — plus regular filter changes."),
        ("When should I replace instead of repair?","If equipment is past about 15 years old and needs a major repair, replacement is often worth pricing. Ask the contractor to quote both so you can compare.")]),
 "plumbing": dict(label="Plumbing", noun="plumber", cost=[
   ("Drain cleaning","$100 – $300"),("Faucet or toilet repair","$150 – $400"),("Water heater replacement","$1,200 – $3,500"),
   ("Sewer line repair","$1,500 – $8,000+"),("Whole-house repipe","$4,000 – $15,000")],
   intro="Plumbing problems rarely wait, which is exactly when homeowners overpay. Use this guide to understand typical costs, vet plumbers in {city} before you need one, and avoid the most common surprises.",
   steps=["Shut off water at the fixture or main if there is active leaking, and take photos for your records.","Call at least two or three licensed plumbers and ask for an estimate or diagnostic fee up front.","For larger jobs (repipes, sewer lines, water heaters), request a written scope with materials and warranty.","Ask whether permits are required and who pulls them.","Confirm payment terms before work starts, and keep paperwork for warranty claims."],
   questions=["Are you licensed and insured in {state}?","Is the diagnostic fee applied to the repair?","Is this a flat-rate quote or hourly, and what could change the price?","What is the warranty on parts and labor?","Do you pull permits, and does the price include them?"],
   red=["Quotes only by phone for complicated jobs, with no site visit.","Unusually low prices followed by add-ons once work starts.","Refusal to show a license or insurance.","Pressure to replace everything when a repair would do."],
   lic="Most states and many cities require plumbers to be licensed, and permits are often required for water heaters, gas lines and repipes. Confirm the license with the {state} licensing authority or {city} building department.",
   timing="Have a plumber you trust identified before an emergency. Schedule water-heater replacement when the old unit shows age (typically 10+ years) rather than waiting for it to fail.",
   faq=[("What does a plumber charge per hour?","Hourly rates vary by market and job type; many plumbers instead quote flat rates for common jobs. Ask which method applies and what is included."),
        ("Do I need a permit for plumbing work?","Many replacements and new installations (water heaters, gas lines, repipes) require permits. Ask your plumber and check with the local building department."),
        ("How do I know if a quote is fair?","Compare at least three written quotes with the same scope, and ask each plumber to explain differences in materials and warranty.")]),
 "electrical": dict(label="Electrical", noun="electrician", cost=[
   ("Outlet or switch replacement","$100 – $300"),("Ceiling fan or light fixture install","$150 – $500"),("EV charger installation","$500 – $2,500"),
   ("Electrical panel upgrade","$1,500 – $4,500"),("Whole-home rewiring","$8,000 – $20,000+")],
   intro="Electrical work is one area where cutting corners is a safety risk, not just a quality problem. This guide covers typical costs, licensing and what to ask any electrician in {city}.",
   steps=["Write down symptoms (tripping breakers, flickering lights, warm outlets) and the age of your panel.","Get two or three written estimates from licensed electricians.","Ask whether the job requires a permit and inspection.","Compare scope: materials, breaker and panel brand, and whether drywall repair is included.","Keep the permit and inspection sign-off for resale and insurance."],
   questions=["Are you licensed in {state} and insured?","Will you pull the permit and arrange the inspection?","What brand and capacity of panel or equipment will you install?","Is drywall repair or patching included?","What warranty covers the work?"],
   red=["No license, or reluctance to pull a permit.","A quote that skips the load calculation for a big new load (EV charger, heat pump).","Pressure to replace the whole panel without explaining why.","Cash-only discounts that skip permits."],
   lic="Electricians are licensed at the state or local level in most places, and many jobs require permits and inspections. Check the electrician's license with the {state} licensing authority or {city} building department.",
   timing="Schedule non-urgent upgrades (panel, EV charger, whole-home surge protection) in off-peak periods, and ask about lead times for equipment.",
   faq=[("Do I need a licensed electrician?","For anything beyond very simple tasks, yes. Licensing and permitting rules vary, but unlicensed work can void insurance and create safety hazards."),
        ("How do I know if my panel needs an upgrade?","Frequent tripped breakers, no room for new circuits, or adding big loads like an EV charger are common reasons. An electrician can run a load calculation."),
        ("What should an estimate include?","The scope of work, materials, permit costs, timeline and warranty — in writing.")]),
 "roofing": dict(label="Roofing", noun="roofing contractor", cost=[
   ("Roof inspection","Free – $300"),("Minor roof repair","$300 – $1,500"),("Asphalt shingle replacement (typical home)","$7,000 – $16,000"),
   ("Metal roof (typical home)","$15,000 – $40,000"),("Gutter replacement","$1,000 – $3,500")],
   intro="A roof is a large, high-stakes purchase, and roofing is also one of the most common targets for storm-chasers and high-pressure sales. This guide helps {city} homeowners compare roofers and protect themselves.",
   steps=["Have the roof inspected, ideally by someone who is not selling you the replacement, and photograph any damage.","If there is storm damage, contact your insurer before signing a contract.","Get at least three written bids with the same scope: materials, underlayment, flashing, ventilation, tear-off and disposal.","Check license, insurance and local references; ask for recently completed roofs you can see.","Use a written contract with start and completion dates, payment schedule and workmanship warranty."],
   questions=["Are you licensed in {state} and covered by general liability and workers' comp?","Will you remove the old roof or install over it?","Which manufacturer warranty applies, and who backs the workmanship warranty?","How do you handle rain delays and protect landscaping and the interior?","Can I see addresses of recent roofs you installed nearby?"],
   red=["Door-to-door pitches after a storm, especially with 'insurance will cover everything.'","Large deposits before materials are ordered.","Bids that don't specify materials or brand.","No physical business address or local references."],
   lic="Roofing license requirements vary widely: some states license roofers, others leave it to local rules, and permits are commonly required for replacements. Verify the contractor with the {state} licensing authority and {city} building department.",
   timing="Schedule replacements in dry shoulder seasons when possible. After storms demand spikes, so avoid rushed decisions and get an independent inspection first.",
   faq=[("How long does a roof last?","Asphalt shingles commonly last roughly 20–30 years depending on climate and installation quality; metal and tile can last longer."),
        ("Should I repair or replace?","Isolated damage on a roof with plenty of life left is usually repaired. Widespread wear or multiple leaks often points to replacement. Get a second opinion."),
        ("Will insurance cover my roof?","It depends on the policy and the cause of damage. Document the damage and contact your insurer before signing a contractor agreement.")]),
 "general_contracting": dict(label="General Contracting", noun="general contractor", cost=[
   ("Bathroom remodel","$8,000 – $30,000"),("Kitchen remodel","$15,000 – $60,000+"),("Room addition","$80 – $200+ per sq ft"),
   ("Basement finishing","$20 – $50 per sq ft"),("Contractor management fee","Often 10% – 20% of project cost")],
   intro="A remodel is likely to be one of the largest checks you write for your home. This guide explains how to scope a project, compare general contractors in {city} and keep the job on budget.",
   steps=["Define the scope and budget, including a contingency of 10–20% for surprises.","Collect three or more detailed bids with itemized costs and clear allowances.","Check license, insurance, references and recent project photos.","Confirm who pulls permits, and the schedule for inspections.","Use a written contract with a payment schedule tied to completed work, not dates."],
   questions=["Are you licensed in {state} and insured?","Who is on site day-to-day, and how often will you update me?","What is included in each allowance, and how are overages handled?","How are change orders priced and approved?","Will you provide lien waivers as you are paid?"],
   red=["A large up-front payment far beyond a modest deposit.","No written contract or vague scope.","No permits for work that requires them.","Reluctance to provide references or insurance."],
   lic="Contractor licensing is handled at the state level in many states and locally in others, and permits are generally required for structural, electrical and plumbing work. Verify with the {state} licensing authority and the {city} building department.",
   timing="Good contractors book out weeks or months. Start planning and collecting bids well before you want work to begin.",
   faq=[("How much should I put down?","Many states cap deposits; ask your state's rules and tie later payments to progress. Avoid paying the majority up front."),
        ("What is a change order?","A written modification to the scope and price. Insist that all changes be agreed in writing before work proceeds."),
        ("Do I need permits?","Many remodels do. A reputable contractor will pull permits in their own name and schedule inspections.")]),
 "landscaping": dict(label="Landscaping", noun="landscaper", cost=[
   ("Lawn mowing (per visit)","$30 – $80"),("Seasonal cleanup","$200 – $700"),("Sod installation","$1 – $2+ per sq ft"),
   ("Tree trimming","$300 – $1,500"),("Irrigation system install","$2,500 – $6,000")],
   intro="Landscaping covers everything from weekly mowing to complete redesigns. This guide helps {city} homeowners understand typical costs, choose between maintenance and design providers, and avoid mismatched expectations.",
   steps=["Decide whether you need ongoing maintenance, a one-time project or a full design.","Get two or three written quotes with clear scope, frequency and what's excluded.","For design/build, ask for a plan, plant list and timeline.","Check insurance and, for tree work or chemical application, required licenses or certifications.","Confirm payment terms and what happens if plants fail within the first season."],
   questions=["Is your crew insured?","What is included in a standard visit?","Do you use subcontractors for tree work or irrigation?","What is the plant warranty, if any?","Are fertilizer and pesticide applications performed by licensed applicators?"],
   red=["No insurance, especially for tree work.","Quotes with no scope or plant list.","Demands for full payment before starting a large project.","Unlicensed pesticide application where licensing is required."],
   lic="Basic lawn care usually needs only a business license, but pesticide application, irrigation and tree work are often regulated. Check requirements with the {state} department that licenses applicators and with {city}.",
   timing="Plan big planting and seeding projects for the best local planting windows, and book design/build work early in the season.",
   faq=[("How much does lawn care cost?","Per-visit mowing for an average yard often runs between $30 and $80, depending on size and market. Ask about seasonal contracts."),
        ("When should I plant?","The best windows depend on plant type and climate. A local landscaper can advise on timing for your yard."),
        ("What's the difference between maintenance and design/build?","Maintenance is recurring upkeep; design/build is a project with a plan and installation. Some companies do both.")]),
 "painting": dict(label="Painting", noun="painter", cost=[
   ("Single room (interior)","$300 – $900"),("Whole-house interior","$2,500 – $7,000"),("Exterior (typical home)","$3,000 – $10,000"),
   ("Cabinet refinishing","$3,000 – $10,000"),("Deck or fence staining","$500 – $3,000")],
   intro="Painting results depend more on preparation than on the paint. This guide shows {city} homeowners what typical projects cost and how to compare painter proposals fairly.",
   steps=["Decide the scope: rooms, trim, ceilings, exterior surfaces and any repairs.","Get three written proposals that list prep work, number of coats and the paint brand and line.","Ask how the crew protects floors and furniture and how they handle lead-safe practices in older homes.","Check insurance and references, and ask to see recent work.","Agree on the color, finish and schedule in writing."],
   questions=["What prep work is included (scraping, sanding, caulking, priming)?","Which paint brand and product line will you use?","How many coats are included?","Do you follow lead-safe work practices for homes built before 1978?","What does your workmanship warranty cover?"],
   red=["Proposals that don't mention prep or paint brand.","Very low bids that cut coats or prep.","Large deposits before any work.","No insurance or references."],
   lic="Painting requirements vary: some states license painters or require certification for lead-safe renovation (EPA RRP) in pre-1978 homes. Check with the {state} licensing authority.",
   timing="Interior painting can happen year-round; exterior projects need suitable weather, so book ahead for the best seasons.",
   faq=[("How long does exterior paint last?","Quality exterior paint and good prep can last many years, though sun, moisture and surface condition all matter."),
        ("Do I need to buy the paint?","Usually the painter supplies it, but you can specify brand and color. Make sure the proposal states what is included."),
        ("What's the cheapest way to save money?","Do simple prep (moving furniture, removing wall hangings) yourself and consolidate trim and ceiling work into a single project.")]),
 "flooring": dict(label="Flooring", noun="flooring installer", cost=[
   ("Carpet installed","$3 – $11 per sq ft"),("Luxury vinyl plank installed","$3 – $12 per sq ft"),("Hardwood installed","$8 – $25 per sq ft"),
   ("Tile installed","$7 – $25 per sq ft"),("Floor refinishing (hardwood)","$3 – $8 per sq ft")],
   intro="Flooring is both a major cost and a daily-use surface, so material choice and installation quality matter. This guide gives {city} homeowners a framework for comparing materials and installers.",
   steps=["Choose a material that fits your use, moisture exposure and budget.","Measure carefully and ask installers to confirm measurements; order overage for waste.","Get written quotes that separate material, labor, removal of old flooring and subfloor prep.","Ask about moisture testing and acclimation for wood products.","Plan for moving furniture and a few days of disruption."],
   questions=["Do you test subfloor flatness and moisture?","Is old flooring removal and disposal included?","What is the labor warranty?","Who handles manufacturer warranty claims?","How much overage do you recommend ordering?"],
   red=["Quotes that exclude subfloor prep until after work begins.","No written scope or warranty.","Pressure to buy materials only through the installer.","Cash-only deals with no contract."],
   lic="Flooring installers are not licensed everywhere, but contractors doing structural or tile work may be. Check requirements with the {state} licensing authority and verify insurance.",
   timing="Order materials early because lead times vary, and let wood and some other products acclimate before installation.",
   faq=[("Which flooring is most durable?","Tile and luxury vinyl are popular for durability and moisture resistance; hardwood is durable and refinishable but sensitive to moisture."),
        ("How much extra material should I order?","Installers commonly recommend ordering roughly 5–15% extra depending on material and layout."),
        ("Can I install flooring myself?","Some floating floors are DIY-friendly. Tile, hardwood and complex layouts are usually worth a professional.")]),
 "pool_spa": dict(label="Pool & Spa", noun="pool service company", cost=[
   ("Weekly pool service (monthly)","$100 – $250"),("Pool opening or closing","$150 – $600"),("Pump or filter replacement","$600 – $2,500"),
   ("Pool resurfacing","$5,000 – $15,000"),("New in-ground pool","$35,000 – $100,000+")],
   intro="Pool ownership is a recurring commitment. This guide explains typical service costs, what to look for in {city} pool companies and how to avoid common surprises.",
   steps=["Decide whether you want weekly service, a one-time repair or a build or renovation.","Get quotes that spell out chemicals, visit frequency and what's excluded.","For builds and renovations, request a detailed contract, drawings and a payment schedule.","Check licensing and insurance, and ask for local references.","Confirm who handles permits, fencing and safety requirements."],
   questions=["Are chemicals included in the monthly price?","How often will you visit, and do you test water each time?","Are you licensed and insured in {state}?","How are repairs quoted and approved?","Who handles permits and safety barriers for new pools?"],
   red=["No written service agreement.","Payment for a large build mostly up front.","Unlicensed work on electrical or gas equipment.","Vague pricing for 'extras.'"],
   lic="Pool contractors are often licensed at the state or local level, and building a pool typically requires permits and safety barriers. Verify with the {state} licensing authority and {city} building department.",
   timing="Book openings and major repairs ahead of the swim season; off-season is often a good time for renovation scheduling.",
   faq=[("How much does pool maintenance cost?","Full-service weekly maintenance often runs between $100 and $250 per month depending on pool size and market. Chemicals may be extra."),
        ("Should I service the pool myself?","Many owners do basic skimming and testing, but chemical balance and equipment checks are good jobs for a professional."),
        ("What safety rules apply?","Most places require barriers or fencing for pools. Check local requirements before building.")]),
 "pest_control": dict(label="Pest Control", noun="pest control company", cost=[
   ("One-time treatment","$150 – $400"),("Quarterly service plan (per visit)","$100 – $300"),("Monthly plan","$40 – $90"),
   ("Termite treatment","$500 – $2,500+"),("Bed bug treatment","$1,000 – $3,500+")],
   intro="Pest problems usually grow if ignored, but overpaying for unnecessary treatments is common. This guide helps {city} homeowners understand typical costs and choose a reputable provider.",
   steps=["Identify the pest if you can, and photograph it or save a sample.","Ask for an inspection and a written treatment plan that names the pest and treatment method.","Compare one-time treatment versus a recurring plan.","Check licensing and insurance, and ask which products will be used around kids and pets.","Confirm re-treatment and warranty terms in writing."],
   questions=["What pest is this, and how do you know?","Which products will you use, and are they safe for children and pets?","What is covered if pests return, and for how long?","Is the plan recurring, and can I cancel without a penalty?","Are your technicians licensed in {state}?"],
   red=["Pressure to sign long contracts on the first visit.","No inspection before quoting.","Unwillingness to name the products used.","Guarantees that sound too good to be true."],
   lic="Pest control companies and technicians are typically licensed or certified at the state level. Check with the {state} agency that regulates pesticide applicators.",
   timing="Schedule termite inspections annually and prevention plans before peak pest seasons.",
   faq=[("How often should I have pest control?","Many homeowners use quarterly service for general prevention, with extra visits as needed for specific infestations."),
        ("Is pest control safe for pets?","Ask which products are used and the recommended re-entry time. Many companies offer pet-safe options."),
        ("Do I need a termite inspection?","In termite-prone areas, annual inspections are common, and lenders sometimes require them when buying a home.")]),
 "residential_cleaning": dict(label="Residential Cleaning", noun="cleaning service", cost=[
   ("Standard cleaning (average home)","$120 – $300"),("Deep clean","$200 – $500"),("Move-out clean","$250 – $600"),
   ("Hourly (per cleaner)","$25 – $60"),("Recurring weekly/biweekly","Often discounted vs one-time")],
   intro="Cleaning services range from solo cleaners to large franchises. This guide helps {city} households compare options, understand pricing and set clear expectations.",
   steps=["Decide whether you need recurring service, a one-time deep clean or a move-in/out clean.","Ask for a written checklist so you know what's included.","Compare pricing by flat rate versus hourly, and clarify supplies.","Ask about insurance, background checks and whether cleaners are employees.","Start with a trial visit and give feedback quickly."],
   questions=["Are cleaners employees or contractors, and are they insured and bonded?","What is included in a standard visit?","Do you bring your own supplies and equipment?","What is your cancellation and satisfaction policy?","How do you handle breakage or damage?"],
   red=["No insurance or background checks.","Vague checklists that cause disputes.","Large up-front payments for recurring service.","Pressure to sign long contracts."],
   lic="Cleaning services typically need a general business license rather than a trade license, but rules vary by city. Check requirements with {city} and confirm the company carries liability insurance.",
   timing="Book recurring slots early for popular days, and schedule move-out cleans for when the property is empty.",
   faq=[("How much does a house cleaning cost?","Standard cleans for an average home often fall in the $120–$300 range, with deep cleans costing more. Size, condition and market affect price."),
        ("Do I need to be home?","Not necessarily. Many households give access by key or code once they trust the provider."),
        ("What's the difference between standard and deep cleaning?","A standard clean covers regular surface cleaning; a deep clean adds detailed work like baseboards, inside appliances and built-up grime.")]),
 "handyman": dict(label="Handyman", noun="handyman", cost=[
   ("Hourly rate","$50 – $130"),("Minimum service call","1 – 2 hours is common"),("Door or fixture install","$100 – $300"),
   ("Drywall patch","$100 – $400"),("Furniture assembly / mounting","$60 – $200")],
   intro="A good handyman can tackle a long to-do list in one visit. This guide explains typical rates, what handymen can and can't do, and how to hire one in {city}.",
   steps=["Make a written list of every task and group them into one visit.","Ask for an hourly rate and any minimum, or a flat price for the full list.","Confirm the handyman is insured and clarify what is outside their scope.","Ask whether materials are included.","Pay when work is completed to your satisfaction."],
   questions=["Are you insured?","Do you charge hourly or per job, and is there a minimum?","Are materials included?","Which jobs do you not take on (electrical, plumbing, structural)?","Can you provide recent references?"],
   red=["No insurance.","Taking on licensed-trade work that requires a license.","Large up-front payments.","Refusing a written estimate."],
   lic="Handymen are often limited to small jobs under a dollar limit set by the state. Work involving licensed trades (electrical, plumbing, HVAC) should go to a licensed contractor. Check {state} rules.",
   timing="Batch tasks into one visit and avoid peak seasons like early spring and fall when homeowners schedule repairs.",
   faq=[("How much does a handyman cost?","Hourly rates commonly run about $50–$130 depending on market and skill, often with a one- to two-hour minimum."),
        ("What can a handyman do?","Typically small repairs and installs: patching drywall, hanging doors, mounting TVs, minor carpentry and assembly."),
        ("When should I hire a licensed contractor instead?","For electrical, plumbing, HVAC, structural or large remodeling work, hire a licensed contractor.")]),
 "moving": dict(label="Moving", noun="moving company", cost=[
   ("Local move (2–3 movers, hourly)","$100 – $250 per hour"),("Typical local move","$400 – $2,500"),("Long-distance move","$2,500 – $8,000+"),
   ("Packing services","$300 – $1,500+"),("Short-term storage","$50 – $300 per month")],
   intro="Moving is stressful and a common source of consumer complaints. This guide explains typical costs, how to verify a mover and how to protect your belongings when moving from or within {city}.",
   steps=["Take inventory and decide what you will pack yourself.","Get in-home or video estimates from at least three licensed movers.","Compare binding versus non-binding estimates and what's included.","Verify registration: interstate movers must have a USDOT number, and many states regulate local movers.","Review the valuation (insurance) options and get everything in writing."],
   questions=["Are you licensed and registered, and what is your USDOT number?","Is the estimate binding, not-to-exceed or hourly?","What valuation (insurance) coverage is included?","Are fuel, stairs, long carry or packing materials extra?","How do you handle delays and damage claims?"],
   red=["Large deposits or cash-only demands.","Phone-only quotes without an inventory.","No company name on trucks or paperwork.","Estimates far below others."],
   lic="Interstate movers must be registered with the Federal Motor Carrier Safety Administration and hold a USDOT number. Local moves are regulated by {state} in many states. Verify both before you book.",
   timing="Book several weeks ahead; late spring through summer and end-of-month dates are busiest and most expensive.",
   faq=[("How much do movers cost?","Local moves are commonly priced hourly and can range from a few hundred to a few thousand dollars; long-distance moves cost more. Always compare written estimates."),
        ("How do I check that a moving company is legitimate?","Look up their USDOT number for interstate moves, check state registration, and read recent customer reviews."),
        ("Do I need moving insurance?","Basic carrier liability is limited. Ask about full-value protection or third-party coverage for valuable items.")]),
 "home_security": dict(label="Home Security", noun="security provider", cost=[
   ("Equipment (starter system)","$0 – $600"),("Professional installation","$100 – $300"),("Monitoring (per month)","$20 – $60"),
   ("Video doorbell / camera","$100 – $300 each"),("Contract length","Often 1 – 3 years")],
   intro="Home security systems vary from DIY kits to professionally monitored packages. This guide helps {city} homeowners compare equipment, monitoring and contract terms.",
   steps=["Decide what you want to protect: entry points, cameras, smoke/CO and environmental sensors.","Compare DIY, professionally installed and hybrid options.","Read contract terms carefully: length, equipment ownership and cancellation fees.","Ask about cellular backup and power outage behavior.","Check whether your city requires an alarm permit."],
   questions=["Do I own or lease the equipment?","What are the contract length and early cancellation fees?","Does monitoring continue during internet or power outages?","Are there permit or false-alarm fees in my city?","What happens to my data and video footage?"],
   red=["Door-to-door pushy sales without credentials.","Contracts that auto-renew without clear notice.","Promises of 'free' equipment hiding long contracts.","No clear cancellation terms."],
   lic="Alarm companies and installers are licensed in many states and some cities. Check with the {state} licensing authority and {city} for alarm-permit requirements.",
   timing="Install before travel seasons and after any move. Look for promotions at slower times of year.",
   faq=[("Do I need professional monitoring?","It depends on your risk tolerance and budget. Monitoring can dispatch help when you're away; self-monitored systems alert you only."),
        ("What's the difference between DIY and professional installation?","DIY kits are cheaper and flexible; professional installation includes setup and often warranty. Compare long-term costs."),
        ("Can I take my system when I move?","Some systems are portable, some are not. Check before signing.")]),
 "solar_energy": dict(label="Solar Energy", noun="solar installer", cost=[
   ("Typical residential system (6–10 kW) before incentives","$15,000 – $30,000"),("Price per watt (installed)","$2.50 – $3.50"),("Battery storage add-on","$9,000 – $20,000"),
   ("Roof repair before install (if needed)","$500 – $5,000+"),("Panel cleaning/inspection","$100 – $400")],
   intro="Solar can lower electricity costs for some homes, but the economics depend on your roof, your utility's rates and current incentives. This guide helps {city} homeowners compare solar installers and proposals.",
   steps=["Review recent electric bills to understand your usage and rates.","Have your roof's age and condition assessed before installing panels.","Get at least three proposals and compare them on a cost-per-watt and expected-production basis.","Understand financing: cash purchase, loan, lease or power purchase agreement (PPA).","Check which incentives currently apply — these change often — and how your utility credits excess power."],
   questions=["What is the total installed cost and cost per watt?","What production does the proposal assume, and how was it estimated?","Is this a purchase, loan, lease or PPA, and what are the escalators?","What are the warranties on panels, inverter and workmanship?","How does my utility credit excess power, and what could change?"],
   red=["Claims of 'free solar' or guaranteed savings.","High-pressure same-day sign-up deals.","Proposals without production estimates.","Financing terms that aren't disclosed clearly."],
   lic="Solar installers are generally required to hold appropriate contractor and electrical licenses, and systems need permits and utility interconnection approval. Verify with the {state} licensing authority. Incentives change often, so confirm current federal, state and utility programs from official sources.",
   timing="Allow several weeks to months for design, permitting and utility approval. Start before the season when you expect the highest usage.",
   faq=[("Is solar worth it?","It depends on your electricity rates, sun exposure, roof and available incentives. Compare multiple proposals and run the numbers on your own bills."),
        ("Should I buy, lease or sign a PPA?","Purchasing usually has the best long-term return but requires upfront capital or a loan; leases and PPAs reduce upfront costs but have escalators and contract terms to review."),
        ("What happens if I sell my house?","Owned systems can add value; leases and PPAs usually need to be transferred. Ask each provider how they handle this.")]),
 "auto_repair": dict(label="Auto Repair", noun="auto repair shop", cost=[
   ("Oil change","$50 – $130"),("Diagnostic fee","$90 – $200"),("Brake pads (per axle)","$150 – $500"),
   ("Battery replacement","$150 – $400"),("Transmission repair","$1,500 – $5,000+")],
   intro="Finding a trustworthy repair shop saves money for the life of your car. This guide helps {city} drivers compare shops, understand typical repair costs and avoid unnecessary work.",
   steps=["Describe symptoms precisely and note when they occur.","Ask for a written estimate that breaks out parts and labor before approving work.","For larger repairs, get a second opinion.","Ask about parts (OEM versus aftermarket) and warranty.","Keep records of repairs for resale and warranty claims."],
   questions=["Will you provide a written estimate and call me before extra work?","Do you use OEM or aftermarket parts, and what's the warranty?","Is the diagnostic fee applied to the repair?","Are your technicians ASE-certified?","Can I see the old parts?"],
   red=["Refusing written estimates.","Pressure to approve a long list of 'urgent' repairs.","Unclear charges for diagnostics.","No warranty on repairs."],
   lic="Auto repair shops may need business and, in some states, registration with a consumer-protection agency. Technicians can hold ASE certification. Check with the {state} agency that regulates repair shops.",
   timing="Handle routine maintenance on schedule to avoid breakdowns; get a second opinion before big repairs.",
   faq=[("How do I find a trustworthy mechanic?","Ask for recommendations, check certifications and reviews, and start with a small job to evaluate communication and pricing."),
        ("Should I use dealer or independent shops?","Dealers specialize in your make and may handle warranty work; independents can offer lower prices. Compare estimates."),
        ("What if the repair doesn't fix the problem?","Ask about the shop's warranty and re-diagnosis policy before approving work.")]),
 "pet_services": dict(label="Pet Services", noun="pet service provider", cost=[
   ("Grooming","$50 – $120"),("Boarding (per night)","$40 – $100"),("Dog walking (per walk)","$15 – $30"),
   ("Pet sitting (per visit)","$20 – $40"),("Training (per session)","$50 – $150")],
   intro="Choosing someone to care for your pet is a trust decision as much as a pricing one. This guide helps {city} pet owners compare groomers, boarders, walkers and trainers.",
   steps=["Decide what service you need and how often.","Ask for a meet-and-greet or facility tour before booking.","Check vaccination requirements, emergency policies and staff experience.","Confirm insurance and bonding for in-home services.","Start with a short trial before longer stays."],
   questions=["What vaccinations do you require?","What is your emergency and veterinary plan?","Are you insured and bonded?","How many pets are in your care at once?","How will you update me while I'm away?"],
   red=["Unwillingness to show the facility.","No vaccination or emergency policy.","Cash-only with no written agreement.","Overcrowded or unsupervised play areas."],
   lic="Pet service rules vary by city and state; boarding and grooming facilities may require business or kennel licenses. Check with {city} animal services.",
   timing="Book holiday boarding and sitting weeks or months in advance.",
   faq=[("How much does dog boarding cost?","Boarding commonly runs from about $40 to $100 per night depending on market and services."),
        ("What should I ask a pet sitter?","Ask about experience, insurance, emergency plans and how they handle medications and updates."),
        ("Do groomers require vaccinations?","Most do. Confirm requirements before your appointment.")]),
 "personal_training": dict(label="Personal Training", noun="personal trainer", cost=[
   ("One-on-one session","$50 – $150"),("Small-group session","$20 – $60"),("Online coaching (monthly)","$100 – $400"),
   ("Initial assessment","Free – $100"),("Gym membership (monthly)","$10 – $100+")],
   intro="A good trainer helps with accountability, safe technique and progress. This guide helps {city} residents compare trainers and understand typical pricing.",
   steps=["Clarify your goal, schedule and budget.","Look for trainers with recognized certifications and relevant experience.","Book an intro session to test communication and style.","Discuss injuries and medical conditions before starting.","Agree on session packages, cancellation and progress tracking."],
   questions=["Which certifications do you hold?","What experience do you have with my goals or injuries?","How do you track progress?","What are your cancellation and package policies?","Do you carry liability insurance?"],
   red=["No certification or insurance.","Pushing extreme diets or supplements.","Ignoring injuries or medical limits.","Aggressive package upsells."],
   lic="Personal training is generally not state-licensed, but reputable trainers hold certifications from organizations such as NASM, ACE, ACSM or NSCA. Verify the certification directly with the issuer.",
   timing="Pick a start date you can sustain, and commit to a schedule for at least a few weeks to judge results.",
   faq=[("How much does a personal trainer cost?","One-on-one sessions often range from $50 to $150 depending on market, experience and location."),
        ("How often should I train with a trainer?","Many clients meet one to three times a week and follow a plan on their own days."),
        ("Is online training effective?","It can be, especially for self-motivated clients, and is often less expensive.")]),
 "tutoring": dict(label="Tutoring", noun="tutor", cost=[
   ("Private tutor (per hour)","$30 – $100"),("Test prep (per hour)","$50 – $150+"),("Learning center (monthly)","$150 – $500"),
   ("Online tutoring platform (per hour)","$20 – $80"),("Group class (per session)","$15 – $50")],
   intro="The right tutor can change a student's confidence as well as grades. This guide helps {city} families compare options, ask the right questions and set goals.",
   steps=["Clarify the goal: homework help, a specific course, test prep or enrichment.","Decide between one-on-one, group, in-person or online.","Interview two or three tutors and ask for a trial session.","Share the student's current materials, grades and teacher feedback.","Set milestones and review progress after a month."],
   questions=["What is your experience with this subject and grade level?","How do you assess a student's needs?","How will you communicate progress to parents?","What is your cancellation policy?","Can I see references or sample plans?"],
   red=["Guarantees of specific grade or score improvements.","No assessment before starting.","Long prepaid packages without a trial.","No communication with parents or teachers."],
   lic="Private tutoring is generally unlicensed, though school-based tutors may need certification. Ask about background checks and verify credentials when relevant.",
   timing="Start before exams or at the beginning of a term rather than after grades have slipped.",
   faq=[("How much does a tutor cost?","Private tutoring often ranges from $30 to $100 per hour depending on subject, level and market."),
        ("How long before we see results?","Many families see better confidence in weeks, with grade changes taking a few months; consistency matters."),
        ("Online or in-person?","Online is flexible and often cheaper; in-person can help younger students stay focused.")]),
 "accounting": dict(label="Accounting", noun="accountant", cost=[
   ("Individual tax return","$200 – $600+"),("Small business tax return","$500 – $2,500"),("Monthly bookkeeping (small business)","$300 – $2,000"),
   ("Payroll service (monthly)","$50 – $300"),("CPA advisory (hourly)","$150 – $400")],
   intro="Accounting needs range from a yearly tax return to full-service bookkeeping. This guide helps {city} individuals and small businesses compare preparers, CPAs and bookkeepers.",
   steps=["Decide what you need: tax prep, bookkeeping, payroll, advisory or all of the above.","Compare credentials: CPA, enrolled agent (EA), bookkeeper or preparer.","Ask for a written engagement letter with scope and pricing.","Confirm they are comfortable with your situation (self-employment, multi-state, rental property).","Keep organized records and ask about their document process."],
   questions=["What credentials do you hold?","Will you sign the return with your PTIN?","What software do you use and how will I share documents?","How do you charge: flat fee, hourly or monthly?","Who represents me if I'm audited?"],
   red=["Preparers who won't sign the return.","Promises of unusually large refunds.","Fees based on a percentage of the refund.","No engagement letter."],
   lic="CPAs are licensed by state boards of accountancy; enrolled agents are federally licensed by the IRS; paid preparers need a PTIN. Verify with the {state} board of accountancy or the IRS directory.",
   timing="Start tax preparation early and avoid the rush near the filing deadline. For bookkeeping, set up monthly routines from day one.",
   faq=[("What's the difference between a CPA and an enrolled agent?","Both can represent you before the IRS; CPAs are licensed by states and broader in scope, while EAs focus on taxation."),
        ("How much should bookkeeping cost?","It depends on volume and complexity; many small businesses pay several hundred to a couple thousand dollars a month."),
        ("What should I bring to my tax appointment?","Income documents (W-2, 1099), deduction records, prior-year return and identification.")]),
 "legal": dict(label="Legal", noun="attorney", cost=[
   ("Initial consultation","Free – $300"),("Hourly rate","$150 – $500+"),("Simple will or estate plan","$500 – $2,500"),
   ("Uncontested divorce","$1,000 – $5,000"),("Contingency fee (injury cases)","Commonly a percentage of recovery")],
   intro="Hiring an attorney can be intimidating. This guide helps {city} residents understand how lawyers charge, what to ask in a consultation and how to compare firms. It is general information, not legal advice.",
   steps=["Identify the type of legal issue and gather documents.","Search for attorneys who focus on that area; verify licensing and discipline history.","Use initial consultations to compare approach, communication and fees.","Review the fee agreement carefully: hourly, flat fee or contingency, plus costs.","Keep communication in writing and ask about updates and timelines."],
   questions=["How much of your practice involves my type of case?","How will you charge, and what costs are extra?","Who will actually work on my matter?","What is a realistic timeline and range of outcomes?","How will we communicate and how quickly do you respond?"],
   red=["Guarantees of outcomes.","No written fee agreement.","Pressure to sign immediately.","Unwillingness to explain fees or strategy."],
   lic="Attorneys must be licensed by the state where they practice. Check the lawyer's license and discipline record with the {state} state bar.",
   timing="Contact a lawyer early — deadlines for legal claims can be short, and early advice often costs less than fixing problems later.",
   faq=[("How much does a lawyer cost?","It varies widely by case type and market; fees can be hourly, flat or contingent. Ask for a written fee agreement."),
        ("What is a retainer?","An upfront deposit against future fees. Ask how it is held and billed."),
        ("Is the first consultation free?","Some attorneys offer free consultations, others charge. Ask when you call.")]),
 "mortgage": dict(label="Mortgage", noun="mortgage lender", cost=[
   ("Closing costs","Commonly 2% – 5% of loan amount"),("Origination / lender fees","Varies; compare Loan Estimates"),("Appraisal","$400 – $800"),
   ("Down payment (conventional)","As low as 3% – 5% for some programs; 20% avoids PMI"),("Rate difference of 0.25%","Can mean thousands over the loan term")],
   intro="A mortgage is likely the biggest financial product you'll ever buy, and small differences in rate and fees add up. This guide helps {city} buyers and refinancers compare lenders. It is general education, not financial advice.",
   steps=["Check your credit reports and understand your budget before applying.","Get Loan Estimates from at least three lenders on the same day or within a short window.","Compare rate, points, lender fees and closing costs on the Loan Estimate form.","Ask about loan programs (conventional, FHA, VA, USDA) and which you qualify for.","Lock your rate when you're comfortable, and understand lock period and fees."],
   questions=["What is your NMLS ID?","What is the interest rate, APR and total closing cost?","Are there prepayment penalties?","How long is the rate lock and what does extending cost?","Who services the loan after closing?"],
   red=["Pressure to lock or apply immediately.","Refusing to provide a Loan Estimate.","Fees that change significantly without explanation.","Guaranteed approval claims."],
   lic="Mortgage loan originators must be licensed and have an NMLS ID. Verify the lender and individual originator using the NMLS Consumer Access website and check {state} regulator records.",
   timing="Shop within a short window so inquiries count together, and avoid opening new credit before closing.",
   faq=[("How many lenders should I compare?","Getting at least three Loan Estimates helps you spot differences in rates and fees."),
        ("What is PMI?","Private mortgage insurance, typically required on conventional loans with less than 20% down."),
        ("Should I pay points?","Points lower the rate in exchange for upfront cost. Compare how long it takes to break even.")]),
 "digital_marketing": dict(label="Digital Marketing", noun="marketing agency", cost=[
   ("SEO retainer (monthly)","$1,000 – $5,000+"),("Paid ads management (monthly)","10% – 20% of spend or $500 – $3,000+"),("Website design","$2,000 – $15,000+"),
   ("Social media management (monthly)","$500 – $3,000"),("Consulting (hourly)","$100 – $250")],
   intro="Marketing agencies vary wildly in quality and transparency. This guide helps {city} business owners compare agencies, understand what they should deliver and avoid common traps.",
   steps=["Define the goal: leads, sales, calls or brand awareness — and a budget.","Ask agencies for case studies in similar businesses and markets.","Request a written scope listing monthly deliverables and reporting.","Clarify who owns accounts, ad spend and creative.","Agree on how success will be measured and reviewed."],
   questions=["What exactly will you do each month?","Who owns the ad accounts, website and analytics?","How will you report results?","What are the contract length and cancellation terms?","Can I speak to a current client?"],
   red=["Guarantees of #1 rankings.","Long contracts with no performance review.","Agency owns your accounts or data.","Vague deliverables and 'proprietary methods.'"],
   lic="Marketing is not licensed, so due diligence matters. Ask for references and review contracts carefully; if the agency handles regulated claims (for example legal, financial or health), confirm compliance practices.",
   timing="SEO often takes months to show results; paid ads can produce faster signals. Plan for a trial period of at least a few months.",
   faq=[("How long does SEO take?","Typically several months before meaningful gains, depending on competition and site condition."),
        ("How much should I spend on marketing?","It depends on your margins and goals. Start with a budget you can sustain and measure results."),
        ("Should I pay by retainer or per project?","Ongoing channels (SEO, ads) often suit retainers; one-off builds suit projects.")]),
 "it_services": dict(label="IT Services", noun="IT provider", cost=[
   ("Break-fix support (hourly)","$100 – $200"),("Managed IT (per user, monthly)","$100 – $250"),("Network setup","$500 – $5,000+"),
   ("Cybersecurity assessment","$2,000 – $15,000+"),("Cloud migration","$3,000 – $50,000+")],
   intro="Reliable IT keeps a business running; unreliable IT quietly costs money every day. This guide helps {city} businesses compare managed IT providers and understand pricing models.",
   steps=["List your systems, users and critical applications.","Decide between break-fix support and a managed services agreement.","Request proposals that define response times, coverage hours and what's excluded.","Ask about backup, security, monitoring and disaster recovery.","Review the contract term, exit rights and who owns administrator credentials."],
   questions=["What are your response and resolution times?","How do you handle backups and recovery testing?","What security tools and practices are included?","Who holds admin credentials and documentation?","Can I see a sample report and speak to a client?"],
   red=["No clear service-level agreement.","Provider holds all admin credentials.","Vague security answers.","Long auto-renewing contracts without review."],
   lic="IT services are not generally licensed, though providers may hold vendor certifications. Ask about relevant security certifications and insurance (including cyber liability).",
   timing="Review your IT setup before growth, relocation or compliance deadlines.",
   faq=[("What is managed IT?","A provider monitors and supports your systems for a recurring monthly fee, usually per user or per device."),
        ("How much does IT support cost?","Many small businesses pay roughly $100–$250 per user per month for managed services, depending on scope."),
        ("Do I need cybersecurity services?","Most businesses do. At minimum, ask about backups, multi-factor authentication, patching and employee training.")]),
}
