"""
Generate styled index pages for every city and styled detail pages for every business.
Run from the repo root: python3 scripts/generate_all.py

Impact affiliate links:
  Once you join Impact.com programs, set IMPACT_PUBLISHER_ID to your numeric publisher ID.
  Then replace the placeholder URLs in IMPACT_AFFILIATES with your real Impact tracking links.
  Each link follows: https://<brand>.sjv.io/c/<publisher_id>/<offer_id>/<media_id>
"""

import os
import re
import math

DOMAIN = "https://allcitypros.com"

# ── Impact affiliate config ────────────────────────────────────────────────────
# Replace "YOUR_IMPACT_ID" with your numeric Impact.com publisher ID.
# Then update each URL with your real offer/media IDs from the Impact dashboard.
IMPACT_PUBLISHER_ID = "YOUR_IMPACT_ID"

IMPACT_AFFILIATES = {
    # Angi (HomeAdvisor) — home services marketplace
    "HVAC":             f"https://angi.sjv.io/c/{IMPACT_PUBLISHER_ID}/1073438/15832?subId1=hvac",
    "Cleaning":         f"https://angi.sjv.io/c/{IMPACT_PUBLISHER_ID}/1073438/15832?subId1=cleaning",
    "Contracting":      f"https://angi.sjv.io/c/{IMPACT_PUBLISHER_ID}/1073438/15832?subId1=contracting",
    "Plumbing":         f"https://angi.sjv.io/c/{IMPACT_PUBLISHER_ID}/1073438/15832?subId1=plumbing",
    "Landscaping":      f"https://angi.sjv.io/c/{IMPACT_PUBLISHER_ID}/1073438/15832?subId1=landscaping",
    "Roofing":          f"https://angi.sjv.io/c/{IMPACT_PUBLISHER_ID}/1073438/15832?subId1=roofing",
    "Electrical":       f"https://angi.sjv.io/c/{IMPACT_PUBLISHER_ID}/1073438/15832?subId1=electrical",
    "Pest Control":     f"https://angi.sjv.io/c/{IMPACT_PUBLISHER_ID}/1073438/15832?subId1=pest",
    "Painting":         f"https://angi.sjv.io/c/{IMPACT_PUBLISHER_ID}/1073438/15832?subId1=painting",
    "Flooring":         f"https://angi.sjv.io/c/{IMPACT_PUBLISHER_ID}/1073438/15832?subId1=flooring",
    "Pool & Spa":       f"https://angi.sjv.io/c/{IMPACT_PUBLISHER_ID}/1073438/15832?subId1=pool",
    "Handyman":         f"https://angi.sjv.io/c/{IMPACT_PUBLISHER_ID}/1073438/15832?subId1=handyman",
    # LegalZoom — online legal services
    "Legal":            f"https://legalzoom.sjv.io/c/{IMPACT_PUBLISHER_ID}/226657/4245?subId1=legal",
    # Bench — online accounting & bookkeeping
    "Accounting":       f"https://bench.sjv.io/c/{IMPACT_PUBLISHER_ID}/1047236/9787?subId1=accounting",
    # LendingTree — mortgage & lending marketplace
    "Mortgage":         f"https://lendingtree.sjv.io/c/{IMPACT_PUBLISHER_ID}/1202385/8619?subId1=mortgage",
    # Clutch — B2B service marketplace (digital marketing & IT)
    "Digital Marketing":f"https://clutch.sjv.io/c/{IMPACT_PUBLISHER_ID}/1234567/9999?subId1=marketing",
    "IT Services":      f"https://clutch.sjv.io/c/{IMPACT_PUBLISHER_ID}/1234567/9999?subId1=it",
    # Moving.com — moving services marketplace
    "Moving":           f"https://moving.sjv.io/c/{IMPACT_PUBLISHER_ID}/1112233/7788?subId1=moving",
    # ADT — home security
    "Home Security":    f"https://adt.sjv.io/c/{IMPACT_PUBLISHER_ID}/998877/5566?subId1=security",
    # Palmetto Solar — residential solar
    "Solar Energy":     f"https://palmetto.sjv.io/c/{IMPACT_PUBLISHER_ID}/774455/3322?subId1=solar",
    # Rover — pet services
    "Pet Services":     f"https://rover.sjv.io/c/{IMPACT_PUBLISHER_ID}/556677/4433?subId1=pets",
    # ClassPass — fitness & personal training
    "Personal Training":f"https://classpass.sjv.io/c/{IMPACT_PUBLISHER_ID}/223344/1122?subId1=fitness",
    # Wyzant — tutoring marketplace
    "Tutoring":         f"https://wyzant.sjv.io/c/{IMPACT_PUBLISHER_ID}/441122/2211?subId1=tutoring",
    # RepairPal — auto repair
    "Auto Repair":      f"https://repairpal.sjv.io/c/{IMPACT_PUBLISHER_ID}/667788/5544?subId1=auto",
}
IMPACT_FALLBACK = f"https://angi.sjv.io/c/{IMPACT_PUBLISHER_ID}/1073438/15832"

# ── Category map ──────────────────────────────────────────────────────────────
CATEGORY_MAP = {
    # Longer/more-specific keywords first to avoid false matches
    "it_services":          {"label": "IT Services",        "emoji": "💻",  "css": "cat-it",          "keywords": ["it_services", "it_support", "managed_it", "computer", "network", "tech_support"]},
    "pest_control":         {"label": "Pest Control",       "emoji": "🐛",  "css": "cat-pest",        "keywords": ["pest_control", "pest", "exterminator", "termite", "rodent"]},
    "general_contracting":  {"label": "Contracting",        "emoji": "🔨",  "css": "cat-contracting", "keywords": ["general_contracting", "contracting", "builders", "construction", "build"]},
    "digital_marketing":    {"label": "Digital Marketing",  "emoji": "📈",  "css": "cat-marketing",   "keywords": ["digital_marketing", "digital", "marketing", "growth", "agency", "seo"]},
    "residential_cleaning": {"label": "Cleaning",           "emoji": "🧹",  "css": "cat-cleaning",    "keywords": ["residential_cleaning", "elite_clean", "sparkle", "cleaning"]},
    "personal_training":    {"label": "Personal Training",  "emoji": "💪",  "css": "cat-fitness",     "keywords": ["personal_training", "fitness", "trainer", "gym", "workout"]},
    "home_security":        {"label": "Home Security",      "emoji": "🔒",  "css": "cat-security",    "keywords": ["home_security", "security", "alarm", "surveillance", "locksmith"]},
    "pool_spa":             {"label": "Pool & Spa",         "emoji": "🏊",  "css": "cat-pool",        "keywords": ["pool_spa", "pool", "spa", "hot_tub", "swimming"]},
    "auto_repair":          {"label": "Auto Repair",        "emoji": "🚗",  "css": "cat-auto",        "keywords": ["auto_repair", "auto", "mechanic", "automotive", "car_repair"]},
    "pet_services":         {"label": "Pet Services",       "emoji": "🐾",  "css": "cat-pets",        "keywords": ["pet_services", "pet", "grooming", "boarding", "veterinary"]},
    "solar_energy":         {"label": "Solar Energy",       "emoji": "☀️",  "css": "cat-solar",       "keywords": ["solar_energy", "solar", "panels", "renewable", "energy"]},
    "moving":               {"label": "Moving",             "emoji": "🚛",  "css": "cat-moving",      "keywords": ["moving", "movers", "relocation", "storage", "packing"]},
    "painting":             {"label": "Painting",           "emoji": "🎨",  "css": "cat-painting",    "keywords": ["painting", "painter", "interior", "exterior", "refinishing"]},
    "flooring":             {"label": "Flooring",           "emoji": "🪵",  "css": "cat-flooring",    "keywords": ["flooring", "floor", "hardwood", "tile", "carpet"]},
    "mortgage":             {"label": "Mortgage",           "emoji": "🏡",  "css": "cat-mortgage",    "keywords": ["mortgage", "lending", "refinance", "loan", "realty"]},
    "tutoring":             {"label": "Tutoring",           "emoji": "📚",  "css": "cat-tutoring",    "keywords": ["tutoring", "tutor", "education", "academic", "learning"]},
    "handyman":             {"label": "Handyman",           "emoji": "🛠️", "css": "cat-handyman",    "keywords": ["handyman", "repairs", "maintenance", "fix", "honey_do"]},
    "hvac":                 {"label": "HVAC",               "emoji": "❄️",  "css": "cat-hvac",        "keywords": ["hvac", "cooling", "heating", "climate", "comfort_systems", "air"]},
    "legal":                {"label": "Legal",              "emoji": "⚖️",  "css": "cat-legal",       "keywords": ["legal", "law", "justice", "attorney"]},
    "accounting":           {"label": "Accounting",         "emoji": "📊",  "css": "cat-accounting",  "keywords": ["accounting", "bookkeeping", "cpa", "tax", "finance"]},
    "plumbing":             {"label": "Plumbing",           "emoji": "🔧",  "css": "cat-plumbing",    "keywords": ["plumbing", "plumber", "drain", "pipe"]},
    "landscaping":          {"label": "Landscaping",        "emoji": "🌿",  "css": "cat-landscaping", "keywords": ["landscaping", "lawn", "garden", "yard"]},
    "roofing":              {"label": "Roofing",            "emoji": "🏠",  "css": "cat-roofing",     "keywords": ["roofing", "roof", "gutter", "shingle"]},
    "electrical":           {"label": "Electrical",         "emoji": "⚡",  "css": "cat-electrical",  "keywords": ["electrical", "electrician", "wiring"]},
}

# ── Ordered category slugs for even numbered-file distribution ────────────────
CATEGORY_SLUGS = list(CATEGORY_MAP.keys())

# ── Business name templates (20+ per category for 200-listing variety) ────────
CITY_BIZ_NAMES = {
    "hvac": [
        "{city} Climate Control", "{city} Air Experts", "{city} Comfort Systems",
        "Premier HVAC {city}", "{city} Heating & Cooling", "Arctic Air {city}",
        "{city} HVAC Solutions", "ThermalPro {city}", "{city} AC Masters",
        "CoolBreeze {city}", "{city} Air Pros", "BlueFlame Heating {city}",
        "{city} Indoor Comfort", "AirRight {city}", "PolarPro HVAC {city}",
        "{city} Energy Solutions", "Comfort Zone {city}", "AirFlow Experts {city}",
        "{city} Mechanical Services", "TempMaster {city}",
    ],
    "legal": [
        "{city} Law Group", "{city} Legal Partners", "The {city} Attorneys",
        "{city} Justice Law", "Premier Legal {city}", "{city} Counsel Group",
        "Meridian Law {city}", "{city} Advocacy Group", "Apex Attorneys {city}",
        "{city} Legal Associates", "Liberty Law {city}", "{city} Trial Lawyers",
        "Summit Law {city}", "{city} Legal Defense", "Shield Legal {city}",
        "Citywide Attorneys {city}", "{city} Law Office", "Prestige Legal {city}",
        "{city} Rights Law Firm", "Cornerstone Attorneys {city}",
    ],
    "residential_cleaning": [
        "Sparkle {city} Cleaning", "{city} Elite Clean", "Fresh Start {city}",
        "{city} Shine Services", "Pro Clean {city}", "Crystal Clear {city}",
        "{city} Maid Brigade", "Gleam Team {city}", "{city} Pristine Cleaning",
        "TidyHome {city}", "{city} Deep Clean Co.", "Radiant Clean {city}",
        "SmartMaids {city}", "{city} Home Sparkle", "CleanSweep {city}",
        "Luminous Clean {city}", "{city} White Glove Cleaning", "FreshHaven {city}",
        "{city} Premier Maid Service", "SpotlessHome {city}",
    ],
    "general_contracting": [
        "{city} Prime Contracting", "{city} Builders", "Metro Contractors {city}",
        "{city} Construction Group", "Premier Build {city}", "Keystone Builders {city}",
        "{city} Master Craftsmen", "Solid Ground Contracting {city}", "Apex Builders {city}",
        "{city} Pro Builders", "Heritage Construction {city}", "{city} Quality Build Co.",
        "Summit Contractors {city}", "{city} Renovation Pros", "Blueprint Builders {city}",
        "CraftWorks {city}", "{city} General Contractors", "Pioneer Build {city}",
        "{city} Home Improvements", "StrongBuild {city}",
    ],
    "digital_marketing": [
        "{city} Growth Agency", "{city} Digital Co.", "Metro Marketing {city}",
        "{city} SEO Pros", "Elevate Digital {city}", "{city} Click Lab",
        "Ignite Media {city}", "{city} Brand Builders", "ROI Agency {city}",
        "Pixel & Pulse {city}", "{city} Lead Gen Pros", "UpRank Digital {city}",
        "LaunchPad Marketing {city}", "{city} Content Studio", "Visible {city}",
        "Momentum Digital {city}", "{city} Conversion Lab", "BrightReach {city}",
        "{city} Online Authority", "ScaleUp Agency {city}",
    ],
    "accounting": [
        "{city} Accounting Group", "{city} CPA Partners", "Premier Books {city}",
        "{city} Tax Pros", "Clarity Accounting {city}", "Ledger Pro {city}",
        "{city} Financial Services", "TrueNumber CPA {city}", "BookRight {city}",
        "{city} Smart Books", "Pinnacle Accounting {city}", "{city} Tax Solutions",
        "Balanced Books {city}", "{city} CPA Advisors", "ProLedger {city}",
        "{city} Financial Group", "Accurate Accounting {city}", "TaxRight {city}",
        "{city} Business Finance", "NumberCrunchers {city}",
    ],
    "it_services": [
        "{city} Tech Solutions", "{city} IT Pros", "Premier IT {city}",
        "{city} Managed Tech", "NetSure {city}", "TechGuard {city}",
        "{city} Network Solutions", "DataShield IT {city}", "CloudBridge {city}",
        "{city} CyberPros", "SysOps {city}", "{city} IT Management",
        "TechEdge {city}", "{city} Managed Services", "DigitalCore IT {city}",
        "InfraPro {city}", "{city} IT Consultants", "SecureTech {city}",
        "{city} IT Help Desk", "ConnectPro IT {city}",
    ],
    "pest_control": [
        "Shield Pest {city}", "{city} Pest Pros", "Premier Pest {city}",
        "Bug Guard {city}", "{city} Exterminators", "CleanSlate Pest {city}",
        "{city} Pest Defense", "SafeHome Pest {city}", "BugBusters {city}",
        "{city} Pest Masters", "TerraFirma Pest {city}", "Guardian Pest {city}",
        "{city} Termite & Pest", "ZeroBug {city}", "AllClear Pest {city}",
        "NatureSafe Pest {city}", "{city} Pest Patrol", "Precision Pest {city}",
        "{city} Bug Eliminators", "TrueShield Pest {city}",
    ],
    "plumbing": [
        "{city} Plumbing Pros", "Premier Plumbers {city}", "FlowFix {city}",
        "{city} Drain Masters", "Quick Plumb {city}", "PipeLine {city}",
        "{city} Water Works", "ClearDrain {city}", "TrustFlow Plumbing {city}",
        "{city} Pipe Pros", "AquaPro {city}", "MasterFlow {city}",
        "{city} Plumbing Solutions", "FastFlow {city}", "RootOut Plumbing {city}",
        "ProPipe {city}", "{city} Leak Stoppers", "DrainRight {city}",
        "{city} Expert Plumbers", "SureFlo {city}",
    ],
    "landscaping": [
        "{city} Lawn & Land", "Green Thumb {city}", "Premier Landscapes {city}",
        "{city} Yard Pros", "Bloom {city}", "TurfMaster {city}",
        "{city} Curb Appeal Co.", "GreenScape {city}", "LawnPerfect {city}",
        "{city} Garden Pros", "EdenScapes {city}", "NatureScape {city}",
        "{city} Outdoor Living", "GrassRoots {city}", "ProTurf {city}",
        "LandCraft {city}", "{city} Lawn Care Experts", "YardWorks {city}",
        "{city} Green Services", "SproutScapes {city}",
    ],
    "roofing": [
        "{city} Roofing Pros", "Peak Roofing {city}", "Premier Roof {city}",
        "SkyShield {city}", "{city} Roof Masters", "TopDeck Roofing {city}",
        "{city} Storm Shield", "ApexRoof {city}", "CrestLine Roofing {city}",
        "{city} Roof Experts", "ProTech Roofing {city}", "EagleRoof {city}",
        "{city} Shingle Pros", "TrueRoof {city}", "SafeHarbor Roofing {city}",
        "PinnaclePro Roofing {city}", "{city} Roof & Gutter", "CoverPro {city}",
        "{city} WeatherSeal Roofing", "SummitRoof {city}",
    ],
    "electrical": [
        "{city} Electric Co.", "Premier Electric {city}", "Volt Pros {city}",
        "{city} Electricians", "PowerUp {city}", "BrightWire {city}",
        "{city} PowerPros", "AmperePro {city}", "{city} Electric Masters",
        "CircuitPro {city}", "WattWise {city}", "{city} Electrical Solutions",
        "Spark Electric {city}", "ElectraServ {city}", "{city} Power Systems",
        "LiveWire Electric {city}", "{city} Electrical Group", "GridPro {city}",
        "{city} Certified Electricians", "VoltEdge {city}",
    ],
    "moving": [
        "{city} Movers", "SwiftMove {city}", "{city} Relocation Pros",
        "TrustMove {city}", "{city} Moving Co.", "EasyMove {city}",
        "CityHaul {city}", "{city} Pro Movers", "Gentle Giant {city}",
        "AllState Moving {city}", "{city} Van Lines", "QuickShift {city}",
        "MetroMove {city}", "{city} Labor Movers", "StarMoving {city}",
        "SafeHaul {city}", "{city} Full-Service Movers", "ProPack {city}",
        "LoadRight {city}", "{city} Moving & Storage",
    ],
    "painting": [
        "{city} Paint Pros", "Premier Painters {city}", "BrushMasters {city}",
        "{city} Color Crew", "FreshCoat {city}", "ProFinish Painting {city}",
        "{city} Interior Painters", "TrueColor {city}", "CleanLine Painting {city}",
        "Vivid Paint {city}", "{city} Painting Co.", "PerfectFinish {city}",
        "RollRight {city}", "{city} House Painters", "TopCoat {city}",
        "SureStroke {city}", "{city} Painting Experts", "ColorCraft {city}",
        "ArtisanPainting {city}", "{city} Premier Coatings",
    ],
    "flooring": [
        "{city} Flooring Pros", "Premier Floors {city}", "HardwoodPro {city}",
        "{city} Floor Masters", "TileRight {city}", "FloorCraft {city}",
        "{city} Carpet & Floors", "SmoothStep {city}", "GrainLine Flooring {city}",
        "{city} LVP Experts", "ClearSpan Flooring {city}", "TruPlank {city}",
        "FloorWise {city}", "{city} Flooring Solutions", "CraftFloor {city}",
        "EliteFloors {city}", "{city} Hardwood Specialists", "ProTile {city}",
        "LevelUp Flooring {city}", "{city} Floor Design Co.",
    ],
    "home_security": [
        "{city} Security Systems", "ShieldHome {city}", "SafeWatch {city}",
        "{city} Alarm Pros", "SecureNow {city}", "Guardian Security {city}",
        "{city} SmartHome Security", "LockSolid {city}", "VigilPro {city}",
        "TrueShield Security {city}", "{city} Home Alarm Co.", "SentinelSec {city}",
        "FortiFy {city}", "{city} Camera & Alarm", "SafeHaven Security {city}",
        "WatchGuard {city}", "{city} Monitored Security", "AlarmRight {city}",
        "ProtectPro {city}", "{city} Security Solutions",
    ],
    "solar_energy": [
        "{city} Solar Pros", "SunPower {city}", "{city} Solar Solutions",
        "BrightSolar {city}", "{city} Green Energy", "SolarFirst {city}",
        "CleanEnergy {city}", "{city} Photovoltaic Co.", "SunHarvest {city}",
        "EcoVolt {city}", "{city} Solar Installers", "SolarWise {city}",
        "SunBridge {city}", "{city} Renewable Energy", "PanelPro {city}",
        "GreenGrid {city}", "{city} Solar Electric", "LumaEnergy {city}",
        "SolarEdge {city}", "{city} Sun & Save",
    ],
    "pool_spa": [
        "{city} Pool Pros", "AquaBlue {city}", "{city} Pool & Spa",
        "ClearWater Pools {city}", "SplashPro {city}", "{city} Pool Service",
        "WavePool {city}", "TrueBlue Pools {city}", "{city} Pool Masters",
        "AquaCraft {city}", "PoolRight {city}", "{city} Spa & Pool Co.",
        "BlueWave {city}", "{city} Pool Cleaning", "CrystalPool {city}",
        "ShorelinePools {city}", "{city} Pool Builders", "HydroFix {city}",
        "PoolPerfect {city}", "{city} Aquatic Services",
    ],
    "auto_repair": [
        "{city} Auto Repair", "TrustMech {city}", "{city} Car Care Center",
        "ProAuto {city}", "{city} Automotive", "SpeedFix Auto {city}",
        "{city} Mechanic Shop", "RoadReady {city}", "MasterTech Auto {city}",
        "AutoMedic {city}", "{city} Engine Experts", "DriveFit {city}",
        "WrenchPro {city}", "{city} Complete Auto Care", "PitStop Auto {city}",
        "QuickFix Auto {city}", "{city} Certified Mechanics", "AutoWorks {city}",
        "CarCure {city}", "{city} Transmission & Auto",
    ],
    "pet_services": [
        "{city} Pet Pros", "FurEver {city}", "{city} Pet Care",
        "TailWag {city}", "PawPerfect {city}", "{city} Dog & Cat Salon",
        "HappyPaws {city}", "PetBliss {city}", "{city} Pet Grooming",
        "WoofWash {city}", "PurePet {city}", "{city} Animal Care",
        "PetSpa {city}", "FurFriends {city}", "{city} Dog Boarding",
        "TenderPaws {city}", "{city} Pet Resort", "ZenPet {city}",
        "NaturalPet {city}", "{city} Critter Care",
    ],
    "personal_training": [
        "{city} Fitness Pros", "IronBody {city}", "{city} Personal Trainers",
        "EliteFit {city}", "{city} Strength & Conditioning", "PeakForm {city}",
        "CoreFit {city}", "{city} Athletic Training", "FitForce {city}",
        "BodyRight {city}", "{city} Wellness Coaches", "LiftPro {city}",
        "PrimalFit {city}", "{city} Transformation Studio", "BurnBright {city}",
        "FitHaven {city}", "{city} Certified Trainers", "AthletePro {city}",
        "MaxFit {city}", "{city} Results Training",
    ],
    "tutoring": [
        "{city} Tutoring Pros", "BrightMind {city}", "{city} Academic Center",
        "LearnRight {city}", "{city} Learning Studio", "TopGrade {city}",
        "ScholarPro {city}", "{city} Math & Reading Tutors", "EduBoost {city}",
        "GradeUp {city}", "{city} Test Prep", "StudySmart {city}",
        "MindSpark {city}", "{city} Private Tutors", "ClearPath {city}",
        "AcePro {city}", "{city} Student Success", "TutorWise {city}",
        "BrainyKids {city}", "{city} Excellence Academy",
    ],
    "mortgage": [
        "{city} Mortgage Group", "HomeLoan {city}", "{city} Lending Pros",
        "RateRight {city}", "{city} Home Finance", "PrimeLend {city}",
        "TrustMortgage {city}", "{city} Realty Finance", "LoanWise {city}",
        "FundedHome {city}", "{city} Mortgage Advisors", "ClearPath Lending {city}",
        "KeyMortgage {city}", "{city} Refinance Experts", "SmarterLoan {city}",
        "HomeReady {city}", "{city} Purchase & Refi", "ProLend {city}",
        "BestRate Mortgage {city}", "{city} Home Equity Pros",
    ],
    "handyman": [
        "{city} Handyman Pros", "FixRight {city}", "{city} Home Repairs",
        "AllFix {city}", "{city} Skilled Handyman", "ProFix {city}",
        "HomeCare {city}", "TrustFix {city}", "{city} Repair Masters",
        "QuickFix Home {city}", "WrenchReady {city}", "{city} Mr. Fix-It",
        "HandyDone {city}", "{city} Home Maintenance", "FixAll {city}",
        "ServiceRight {city}", "{city} Reliable Handyman", "CraftFix {city}",
        "HouseCall {city}", "{city} Honey-Do Pros",
    ],
}

# ── City metadata ─────────────────────────────────────────────────────────────
CITY_META = {
    "albuquerque":     ("Albuquerque",    "NM", "🎈"),
    "arlington":       ("Arlington",      "TX", "🏟️"),
    "atlanta":         ("Atlanta",        "GA", "🍑"),
    "aurora":          ("Aurora",         "CO", "🌄"),
    "austin":          ("Austin",         "TX", "🎸"),
    "bakersfield":     ("Bakersfield",    "CA", "🛢️"),
    "baltimore":       ("Baltimore",      "MD", "🦀"),
    "boston":          ("Boston",         "MA", "🫘"),
    "charlotte":       ("Charlotte",      "NC", "🏦"),
    "chicago":         ("Chicago",        "IL", "🌆"),
    "coloradosprings": ("Colorado Springs","CO","⛰️"),
    "columbus":        ("Columbus",       "OH", "🏛️"),
    "dallas":          ("Dallas",         "TX", "⭐"),
    "denver":          ("Denver",         "CO", "🏔️"),
    "detroit":         ("Detroit",        "MI", "🚗"),
    "elpaso":          ("El Paso",        "TX", "🌅"),
    "fortmyers":       ("Fort Myers",     "FL", "🦈"),
    "fortworth":       ("Fort Worth",     "TX", "🤠"),
    "fresno":          ("Fresno",         "CA", "🍇"),
    "houston":         ("Houston",        "TX", "🤠"),
    "indianapolis":    ("Indianapolis",   "IN", "🏁"),
    "jacksonville":    ("Jacksonville",   "FL", "🌊"),
    "kansascity":      ("Kansas City",    "MO", "🎷"),
    "lasvegas":        ("Las Vegas",      "NV", "🎰"),
    "longbeach":       ("Long Beach",     "CA", "⚓"),
    "losangeles":      ("Los Angeles",    "CA", "🎬"),
    "louisville":      ("Louisville",     "KY", "🐎"),
    "mesa":            ("Mesa",           "AZ", "🏜️"),
    "miami":           ("Miami",          "FL", "🌊"),
    "milwaukee":       ("Milwaukee",      "WI", "🍺"),
    "minneapolis":     ("Minneapolis",    "MN", "❄️"),
    "nashville":       ("Nashville",      "TN", "🎵"),
    "newyork":         ("New York",       "NY", "🗽"),
    "oakland":         ("Oakland",        "CA", "🌉"),
    "oklahomacity":    ("Oklahoma City",  "OK", "🌪️"),
    "omaha":           ("Omaha",          "NE", "🌽"),
    "orlando":         ("Orlando",        "FL", "🎡"),
    "philadelphia":    ("Philadelphia",   "PA", "🔔"),
    "phoenix":         ("Phoenix",        "AZ", "🌵"),
    "pittsburgh":      ("Pittsburgh",     "PA", "🌉"),
    "portland":        ("Portland",       "OR", "🌲"),
    "raleigh":         ("Raleigh",        "NC", "🌿"),
    "sacramento":      ("Sacramento",     "CA", "🌾"),
    "sanantonio":      ("San Antonio",    "TX", "🌺"),
    "sandiego":        ("San Diego",      "CA", "🏄"),
    "sanfrancisco":    ("San Francisco",  "CA", "🌁"),
    "sanjose":         ("San Jose",       "CA", "💻"),
    "seattle":         ("Seattle",        "WA", "☕"),
    "tampa":           ("Tampa",          "FL", "🌴"),
    "tucson":          ("Tucson",         "AZ", "🌵"),
    "tulsa":           ("Tulsa",          "OK", "🛢️"),
    "virginiabeach":   ("Virginia Beach", "VA", "🏖️"),
    "washington":      ("Washington",     "DC", "🏛️"),
    "wichita":         ("Wichita",        "KS", "🌪️"),
    # ── 100 additional cities ──────────────────────────────────────────────
    "akron":           ("Akron",          "OH", "🏭"),
    "anaheim":         ("Anaheim",        "CA", "🎡"),
    "anchorage":       ("Anchorage",      "AK", "🐻"),
    "batonrouge":      ("Baton Rouge",    "LA", "🎭"),
    "birmingham":      ("Birmingham",     "AL", "⚙️"),
    "boise":           ("Boise",          "ID", "🏔️"),
    "buffalo":         ("Buffalo",        "NY", "🦬"),
    "capecoral":       ("Cape Coral",     "FL", "🌴"),
    "chandler":        ("Chandler",       "AZ", "🌵"),
    "chattanooga":     ("Chattanooga",    "TN", "🌉"),
    "cincinnati":      ("Cincinnati",     "OH", "🎪"),
    "clarksville":     ("Clarksville",    "TN", "🎵"),
    "clearwater":      ("Clearwater",     "FL", "🌊"),
    "cleveland":       ("Cleveland",      "OH", "🎸"),
    "columbia":        ("Columbia",       "SC", "🦅"),
    "corpuschristi":   ("Corpus Christi", "TX", "🌊"),
    "dayton":          ("Dayton",         "OH", "✈️"),
    "desmoines":       ("Des Moines",     "IA", "🌽"),
    "durham":          ("Durham",         "NC", "🐂"),
    "elkgrove":        ("Elk Grove",      "CA", "🌾"),
    "eugene":          ("Eugene",         "OR", "🌲"),
    "fayetteville":    ("Fayetteville",   "NC", "🪖"),
    "fontana":         ("Fontana",        "CA", "🏜️"),
    "fortcollins":     ("Fort Collins",   "CO", "🏔️"),
    "fremont":         ("Fremont",        "CA", "💻"),
    "frisco":          ("Frisco",         "TX", "⭐"),
    "garland":         ("Garland",        "TX", "⭐"),
    "gilbert":         ("Gilbert",        "AZ", "🌵"),
    "glendale":        ("Glendale",       "AZ", "🌵"),
    "glendaleCA":      ("Glendale",       "CA", "🎬"),
    "grandrapids":     ("Grand Rapids",   "MI", "🌷"),
    "greensboro":      ("Greensboro",     "NC", "🌿"),
    "henderson":       ("Henderson",      "NV", "🎰"),
    "hialeah":         ("Hialeah",        "FL", "🌴"),
    "honolulu":        ("Honolulu",       "HI", "🌺"),
    "huntingtonbeach": ("Huntington Beach","CA","🏄"),
    "huntsville":      ("Huntsville",     "AL", "🚀"),
    "irvine":          ("Irvine",         "CA", "🏙️"),
    "irving":          ("Irving",         "TX", "⭐"),
    "jackson":         ("Jackson",        "MS", "🎷"),
    "jerseycity":      ("Jersey City",    "NJ", "🗽"),
    "knoxville":       ("Knoxville",      "TN", "🎵"),
    "laredo":          ("Laredo",         "TX", "🌵"),
    "lexington":       ("Lexington",      "KY", "🐎"),
    "lincoln":         ("Lincoln",        "NE", "🌽"),
    "littlerock":      ("Little Rock",    "AR", "🌳"),
    "lubbock":         ("Lubbock",        "TX", "🤠"),
    "madison":         ("Madison",        "WI", "🧀"),
    "mcallen":         ("McAllen",        "TX", "🌵"),
    "modesto":         ("Modesto",        "CA", "🍇"),
    "montgomery":      ("Montgomery",     "AL", "⚙️"),
    "morenovalley":    ("Moreno Valley",  "CA", "🏜️"),
    "murfreesboro":    ("Murfreesboro",   "TN", "🎵"),
    "neworleans":      ("New Orleans",    "LA", "🎷"),
    "newportnews":     ("Newport News",   "VA", "🚢"),
    "norfolk":         ("Norfolk",        "VA", "⚓"),
    "northlasvegas":   ("North Las Vegas","NV", "🎰"),
    "oxnard":          ("Oxnard",         "CA", "🌊"),
    "palmdale":        ("Palmdale",       "CA", "🏜️"),
    "pasadena":        ("Pasadena",       "CA", "🌹"),
    "paterson":        ("Paterson",       "NJ", "🏭"),
    "peoria":          ("Peoria",         "IL", "🌊"),
    "plano":           ("Plano",          "TX", "⭐"),
    "providence":      ("Providence",     "RI", "🎓"),
    "ranchocucamonga": ("Rancho Cucamonga","CA","🍇"),
    "reno":            ("Reno",           "NV", "🎲"),
    "richmond":        ("Richmond",       "VA", "🏛️"),
    "riverside":       ("Riverside",      "CA", "🍊"),
    "rochester":       ("Rochester",      "NY", "🌸"),
    "rockford":        ("Rockford",       "IL", "🌊"),
    "saltlakecity":    ("Salt Lake City", "UT", "⛷️"),
    "santaana":        ("Santa Ana",      "CA", "🌸"),
    "santaclarita":    ("Santa Clarita",  "CA", "🎬"),
    "santarosa":       ("Santa Rosa",     "CA", "🍷"),
    "savannah":        ("Savannah",       "GA", "🌳"),
    "scottsdale":      ("Scottsdale",     "AZ", "🌵"),
    "shreveport":      ("Shreveport",     "LA", "🎭"),
    "spokane":         ("Spokane",        "WA", "☕"),
    "springfieldIL":   ("Springfield",    "IL", "🏛️"),
    "springfieldMO":   ("Springfield",    "MO", "🌿"),
    "stlouis":         ("St. Louis",      "MO", "🌉"),
    "stpaul":          ("St. Paul",       "MN", "❄️"),
    "stpetersburg":    ("St. Petersburg", "FL", "🌊"),
    "stockton":        ("Stockton",       "CA", "🌾"),
    "syracuse":        ("Syracuse",       "NY", "🏒"),
    "tacoma":          ("Tacoma",         "WA", "☕"),
    "tallahassee":     ("Tallahassee",    "FL", "🌴"),
    "tempe":           ("Tempe",          "AZ", "🌵"),
    "toledo":          ("Toledo",         "OH", "🌊"),
    "torrance":        ("Torrance",       "CA", "🌊"),
    "vancouver":       ("Vancouver",      "WA", "🌲"),
    "winstonsalem":    ("Winston-Salem",  "NC", "🌿"),
    "worcester":       ("Worcester",      "MA", "🎓"),
    "yonkers":         ("Yonkers",        "NY", "🗽"),
    "amarillo":        ("Amarillo",       "TX", "🤠"),
    "chesapeake":      ("Chesapeake",     "VA", "🦀"),
    "macon":           ("Macon",          "GA", "🍑"),
    "siouxfalls":      ("Sioux Falls",    "SD", "🌾"),
    "fortwayne":       ("Fort Wayne",     "IN", "🏭"),
    "grandprairie":    ("Grand Prairie",  "TX", "⭐"),
    "overlandpark":    ("Overland Park",  "KS", "🌪️"),
}

# ── Long descriptions per category ───────────────────────────────────────────
LONG_DESCS = {
    "HVAC": """\
{biz} has been the trusted name in heating, ventilation, and air conditioning throughout {city}, {state} for years. \
Whether you need a brand-new central AC system installed before summer, emergency repairs in the dead of winter, \
or a routine tune-up to keep your unit running at peak efficiency, our NATE-certified technicians have the training \
and tools to get the job done right the first time.

We service all major brands — Carrier, Trane, Lennox, Rheem, and more — and carry a full inventory of replacement \
parts so most repairs are completed in a single visit. Our maintenance plans include priority scheduling, discounts \
on parts, and annual inspections that catch small issues before they become expensive breakdowns.

{city} homeowners and business owners count on us for fast response times (same-day availability for emergencies), \
transparent flat-rate pricing, and workmanship backed by a 100% satisfaction guarantee. All technicians are \
background-checked, licensed, and fully insured. Call today for a free estimate or to schedule your next service appointment.""",

    "Legal": """\
{biz} is a full-service law firm proudly serving individuals, families, and businesses throughout {city}, {state}. \
Our attorneys bring decades of combined courtroom and negotiation experience across a broad range of practice areas, \
from personal injury and family law to criminal defense, civil litigation, and business contracts.

We believe quality legal representation shouldn't be reserved for the wealthy. That's why we offer free initial \
consultations for all new clients, flexible payment arrangements, and contingency-fee options for qualifying cases — \
meaning you pay nothing unless we win. Our team takes the time to understand your unique situation, explain your \
options in plain language, and build a strategy focused on achieving the best possible outcome.

Clients across {city} choose us because we're responsive, honest, and genuinely invested in their success. \
Whether you're facing a complex legal battle or simply need a contract reviewed, our doors — and phones — \
are open. Schedule your free consultation today.""",

    "Cleaning": """\
{biz} brings professional-grade cleaning to homes and businesses across {city}, {state}. Our fully insured, \
background-checked cleaning specialists use commercial-quality equipment and eco-friendly, non-toxic products \
that are safe for kids, pets, and the environment.

From weekly maintenance cleans and bi-weekly refreshes to deep cleans before a move, after construction, \
or ahead of a special event, we tailor every visit to your space and priorities. Our detailed checklist covers \
everything from baseboards and ceiling fans to inside appliances and grout lines — the areas most services skip.

Booking is easy: choose your service online, pick a time that works for you, and we'll handle the rest. \
{city} residents love our consistent quality — the same trained team returns each visit so they learn your \
home inside out. All work is backed by our re-clean guarantee: if something isn't right, we'll come back \
at no charge. Get a free instant quote on our website today.""",

    "Contracting": """\
{biz} is {city}'s premier general contracting firm, delivering high-quality construction and renovation \
services for residential and commercial clients across {state}. From full home additions and kitchen \
remodels to office build-outs and structural repairs, our licensed team handles projects of every size \
with the same attention to detail and commitment to craftsmanship.

Every project starts with a thorough on-site consultation, detailed written estimate, and clear timeline — \
no vague bids, no surprise charges. We coordinate all subcontractors, pull all required permits, and \
manage every phase of construction so you can stay focused on your life or business.

{city} homeowners and property managers trust us because we show up on time, communicate proactively, \
and stand behind every nail and beam we place. Our portfolio spans hundreds of completed projects \
throughout the {city} area. All work is fully bonded, insured, and backed by a written warranty. \
Call today for your free, no-obligation estimate.""",

    "Digital Marketing": """\
{biz} is a results-driven digital marketing agency helping {city} businesses compete and grow online. \
We specialize in search engine optimization (SEO), Google and Meta paid advertising, social media management, \
email marketing, and conversion-focused website design — the full stack of tools modern businesses need \
to attract and retain customers.

What sets us apart is our obsession with measurable outcomes. We don't run campaigns and hope for the best — \
every strategy we build is tied to clear KPIs: more qualified leads, lower cost-per-acquisition, higher \
return on ad spend. Monthly reporting keeps you fully informed, and our team is always one call away \
to answer questions or adjust tactics based on what the data is telling us.

Whether you're a local {city} shop looking to dominate Google Maps or a regional company scaling into \
new markets, we build a strategy that fits your budget and goals. Reach out today for a free audit \
of your current online presence.""",

    "Accounting": """\
{biz} provides accurate, reliable accounting and financial services to individuals and businesses \
throughout {city}, {state}. Our licensed CPAs and bookkeeping specialists handle everything from \
monthly bookkeeping and payroll processing to corporate tax preparation, IRS audit representation, \
and long-term financial planning.

Small business owners in {city} trust us to keep their books clean, their taxes optimized, and their \
cash flow healthy — so they can focus on running their business instead of drowning in spreadsheets. \
We work with sole proprietors, LLCs, S-corps, and C-corps across every industry, and we're fluent in \
QuickBooks, Xero, Wave, and other popular accounting platforms.

Our approach is proactive, not just reactive. We don't just file your taxes — we look for opportunities \
to minimize your liability, catch errors before they become problems, and give you the financial clarity \
you need to make confident decisions. Schedule a free 30-minute consultation today.""",

    "IT Services": """\
{biz} delivers managed IT support and technology solutions to small and mid-sized businesses \
across {city}, {state}. Our certified technicians provide everything from help desk support and \
network setup to cloud migrations, cybersecurity assessments, and hardware procurement — all under \
one predictable monthly rate.

Downtime is expensive. That's why our managed IT clients get 24/7 monitoring, proactive maintenance, \
and guaranteed response times so issues get resolved before they derail your workday. We protect your \
data with enterprise-grade backup solutions, multi-factor authentication, and regular security audits \
tailored to your industry's compliance requirements.

{city} businesses choose us because we act like an in-house IT department at a fraction of the cost. \
No more chasing down freelancers or waiting days for a fix — our team knows your systems inside out \
and responds fast. Get a free network assessment today and see exactly where your vulnerabilities are.""",

    "Pest Control": """\
{biz} provides fast, thorough pest elimination and prevention services for homes and businesses \
throughout {city}, {state}. Our state-licensed exterminators are trained to handle everything from \
common ant and roach infestations to more serious issues like termite colonies, bed bug outbreaks, \
and rodent invasions.

We use Integrated Pest Management (IPM) techniques — targeted, science-based treatments that eliminate \
pests effectively while minimizing chemical exposure for your family, pets, and the surrounding environment. \
After every treatment, we walk you through what we found, what we applied, and what to expect, so you're \
never left guessing.

Our protection plans offer scheduled quarterly or monthly visits to keep {city} homes pest-free year-round, \
with a re-treatment guarantee if pests return between visits. Whether you need a one-time treatment or \
ongoing coverage, we'll build a plan that fits your situation and budget. Call today for a free inspection.""",

    "Plumbing": """\
{biz} is {city}'s trusted plumbing service for residential and commercial customers across {state}. \
From leaky faucets and clogged drains to full pipe replacements, water heater installations, and \
sewer line repairs, our licensed plumbers handle every job with speed, precision, and fair pricing.

Plumbing problems rarely happen at a convenient time. That's why we offer 24/7 emergency service \
with same-day availability for burst pipes, major leaks, and sewer backups — no after-hours \
surcharges for emergencies. Every technician arrives in a fully stocked service vehicle so most \
repairs are completed on the first visit.

{city} homeowners and property managers rely on us for transparent, upfront pricing (you approve \
the price before we start), honest recommendations, and workmanship backed by a written guarantee. \
Our team is background-checked, licensed in {state}, and fully insured. Call or book online today.""",

    "Landscaping": """\
{biz} transforms outdoor spaces throughout {city}, {state} — from routine lawn maintenance to \
complete landscape redesigns. Our crews handle mowing, edging, fertilization, weed control, \
irrigation installation and repair, seasonal planting, tree and shrub trimming, mulching, \
and full hardscape projects like patios and retaining walls.

We believe curb appeal matters. A well-maintained yard adds real value to your property, improves \
your neighborhood, and gives you an outdoor space you actually want to spend time in. Our landscape \
designers work with your budget and vision to create a plan that's both beautiful and practical — \
low-maintenance where you want it, lush where you need it.

Residential and HOA clients across {city} count on our consistent, reliable service. Every crew is \
trained, uniformed, and background-checked. Seasonal packages are available so you get the right \
services at the right time of year without managing individual appointments. Get a free estimate today.""",

    "Roofing": """\
{biz} is a fully licensed and insured roofing contractor serving homeowners and commercial property \
owners throughout {city}, {state}. Whether you need a minor repair, a full replacement after storm \
damage, or a brand-new installation on a new build, our experienced roofing crews deliver quality \
materials and expert workmanship on every job.

We specialize in asphalt shingles, metal roofing, flat roofing systems, and tile — and we carry \
products from top manufacturers backed by industry-leading manufacturer warranties. Our team also \
handles gutter installation and cleaning, soffit and fascia repair, and attic ventilation upgrades \
that extend the life of your roof and reduce energy costs.

{city} property owners trust us because we show up with a crew that's on time, cleans up thoroughly \
after every job, and backs all work with a written labor warranty on top of the manufacturer coverage. \
Call today for a free roof inspection and no-pressure estimate.""",

    "Electrical": """\
{biz} provides professional electrical services for homes and businesses throughout {city}, {state}. \
Our licensed electricians handle the full spectrum of electrical work — panel upgrades and replacements, \
outlet and switch installation, lighting design and retrofit, whole-home generator hookups, EV charger \
installation, and comprehensive safety inspections.

Electrical work isn't something to DIY or hand to an unlicensed handyman. Every job we complete is \
done to {state} code, pulled with the proper permits, and inspected to protect your family and your \
investment. We carry full liability insurance and workers' compensation on every technician.

{city} residents choose us for our honest assessments, upfront pricing, and the confidence that comes \
from working with a team that does this right. Whether your home needs a 200-amp panel upgrade or you \
just want to add a few outlets to your home office, we'll give you a clear, itemized quote before \
any work begins. Call today.""",

    "Moving": """\
{biz} makes relocation stress-free for families and businesses throughout {city}, {state}. \
Whether you're moving across town or across the country, our trained crews handle every step — \
packing, loading, transport, unloading, and furniture placement — with the care your belongings deserve.

We use professional-grade packing materials and furniture protection on every move, and our GPS-tracked \
fleet means you always know where your possessions are. Specialty items like pianos, artwork, \
and antiques get dedicated wrapping and handling procedures. We also offer short- and long-term \
storage solutions at our climate-controlled facility.

Thousands of {city} families have trusted us with their most important moves. We're fully licensed, \
insured, and registered with the FMCSA. Get a free in-home or virtual estimate today — \
no hidden fees, no surprises on moving day.""",

    "Painting": """\
{biz} delivers flawless interior and exterior painting for homes and commercial spaces throughout \
{city}, {state}. Our licensed painters prep every surface properly, use premium paints and materials, \
and clean up completely — so you get a finish that looks great and lasts for years.

Interior services include walls, ceilings, trim, cabinets, and accent walls. Exterior work covers \
full house painting, wood staining, deck refinishing, and pressure washing as part of the prep process. \
We work with all major paint brands and can help you choose the right sheen, color palette, \
and finish for every room or surface.

{city} homeowners trust us because we protect their furniture and flooring, stick to the agreed timeline, \
and back every job with a satisfaction guarantee. Our crews are background-checked, fully insured, \
and trained in low-VOC and eco-friendly product options. Request your free color consultation today.""",

    "Flooring": """\
{biz} is {city}'s go-to source for beautiful, durable flooring installations across {state}. \
We carry and install hardwood, engineered wood, luxury vinyl plank (LVP), tile, laminate, \
and carpet — with a showroom-quality selection and expert installation for every style and budget.

Our certified installers handle subfloor preparation, moisture testing, and precision fitting so \
your new floors look perfect and last decades. We also refinish and restore existing hardwood floors, \
replacing scratches, dents, and worn finish with a like-new surface — often at a fraction of \
the cost of replacement.

{city} homeowners and commercial clients rely on us for on-time installations, honest pricing, \
and workmanship backed by a written warranty. Free in-home measurements and estimates are always \
available. Browse our portfolio and schedule your consultation today.""",

    "Home Security": """\
{biz} protects homes and businesses throughout {city}, {state} with professional security system \
installation, 24/7 monitoring, and smart-home integration. Our licensed technicians design a customized \
security plan around your property — covering entry points, interior motion, cameras, glass-break \
sensors, and flood or fire detection.

Modern security is about more than alarms. We install and configure smart locks, video doorbells, \
indoor and outdoor cameras, and app-connected control panels so you can monitor your home from \
anywhere in the world. Our 24/7 monitoring center contacts emergency services the moment an event \
is detected — average response in under 45 seconds.

{city} residents choose us for our no-contract monitoring options, local support team, and systems \
that work even when the internet goes down. Get a free security assessment and custom quote today.""",

    "Solar Energy": """\
{biz} helps {city}, {state} homeowners and businesses reduce their energy bills and carbon footprint \
with professionally installed solar panel systems. Our certified solar installers handle everything \
from roof assessment and system design through permitting, installation, grid interconnection, \
and utility incentive filing.

We work with top-tier panel manufacturers — LG, SunPower, Panasonic, and REC — and offer multiple \
battery storage solutions including the Tesla Powerwall and Enphase IQ Battery, so you stay powered \
even during grid outages. Our team identifies every available federal, state, and utility incentive, \
including the 30% federal tax credit, to maximize your savings from day one.

The average {city} homeowner who goes solar saves thousands over the life of their system. \
We back all installations with a 25-year panel warranty and a 10-year workmanship guarantee. \
Get a free solar assessment and savings estimate today — no pressure, no obligation.""",

    "Pool & Spa": """\
{biz} is {city}'s trusted pool and spa service company, handling everything from routine weekly \
maintenance to full pool construction, resurfacing, and equipment replacement. Our certified pool \
technicians keep your water chemistry balanced, equipment running efficiently, and surfaces clean \
all year long.

Weekly service plans include skimming, brushing, vacuuming, chemical balancing, and equipment \
inspection — so you can enjoy your pool without lifting a finger. When repairs are needed, \
our stocked service vehicles carry pumps, filters, heaters, automation controls, and lighting \
components for same-day fixes on most issues.

{city} pool owners rely on us for responsive service, transparent pricing, and the peace of mind \
that comes from working with a fully licensed and insured team. We also offer seasonal opening \
and closing packages, pool remodels, and spa installation. Call today for a free water analysis \
and service quote.""",

    "Auto Repair": """\
{biz} is {city}'s trusted auto repair shop, providing honest, high-quality vehicle service for \
cars, trucks, and SUVs across {state}. Our ASE-certified mechanics diagnose and fix everything \
from routine oil changes and brake jobs to complex engine repairs, transmission rebuilds, \
and electrical system diagnostics.

We believe auto repair shouldn't feel like a gamble. Every service begins with a transparent \
digital inspection — photos included — so you see exactly what needs attention and why, \
with no pressure to approve anything you're not ready for. Most repairs are completed same-day, \
and we stand behind our work with a 12-month/12,000-mile parts-and-labor warranty.

{city} drivers trust us because we're straightforward, fast, and genuinely care about keeping \
your vehicle safe and reliable. We work on all makes and models and accept most extended warranties. \
Book your appointment online or give us a call — free estimates on most repairs.""",

    "Pet Services": """\
{biz} provides compassionate, professional pet care services for dogs, cats, and small animals \
throughout {city}, {state}. Whether your pet needs a full grooming session, boarding while you \
travel, daycare during the workday, or obedience training, our experienced team treats every \
animal like family.

Our grooming services include breed-appropriate cuts, baths, nail trims, ear cleaning, \
and teeth brushing — performed in a calm, stress-free environment. Boarding guests stay in \
spacious, climate-controlled suites with daily exercise, playtime, and individual attention. \
Our certified trainers offer private lessons, group classes, and puppy socialization programs \
backed by positive reinforcement methods.

{city} pet owners love us for our transparent communication — daily updates and photos during \
boarding and daycare — and for the genuine love our staff shows every animal. All facilities \
are clean, safe, and fully insured. Book your pet's first visit today.""",

    "Personal Training": """\
{biz} helps {city}, {state} residents achieve their fitness goals through personalized, \
science-backed training programs. Our certified personal trainers design every workout plan \
around your specific body, goals, and lifestyle — whether you want to lose weight, build muscle, \
improve athletic performance, or simply feel better every day.

We offer one-on-one personal training, small group sessions, and nutrition coaching in private \
studio settings, at your home gym, or outdoors. Every program starts with a comprehensive \
fitness assessment so we understand your current level, history, and any injuries or limitations. \
From there we build a progressive plan and adjust it as you improve.

{city} clients choose us because we get results — and because we hold you accountable with \
the right mix of encouragement and challenge. Our trainers are certified through NASM, ACE, \
or NSCA and carry full liability insurance. Book a free intro session today.""",

    "Tutoring": """\
{biz} connects {city}, {state} students with experienced, caring tutors who make learning click. \
We offer one-on-one and small-group tutoring for K–12 students in all core subjects — \
math, reading, writing, science, history, and foreign languages — as well as SAT/ACT prep \
and specialized support for students with learning differences.

Our tutors are credentialed teachers, college professors, and subject-matter experts who adapt \
their teaching style to each student's learning profile. Sessions are available in-home, \
at our learning center, or online — flexible scheduling that works around school and family life.

{city} families see measurable results: most students improve a full letter grade within 4–6 weeks. \
We track progress transparently and keep parents informed every step of the way. \
Call today for a free academic assessment and to get matched with your perfect tutor.""",

    "Mortgage": """\
{biz} helps {city}, {state} homebuyers and homeowners navigate the mortgage process with \
confidence. Our licensed mortgage advisors shop rates across dozens of lenders to find you \
the best possible rate and terms — whether you're purchasing your first home, moving up, \
refinancing for a lower payment, or tapping home equity.

We work with conventional, FHA, VA, USDA, and jumbo loan programs, and our team is experienced \
with first-time buyer grants and down payment assistance programs available in {state}. \
From pre-approval to closing, we handle the paperwork and keep you informed at every milestone \
so there are no surprises at the settlement table.

{city} clients choose us for our speed — most pre-approvals within 24 hours — \
and for our commitment to finding the right loan, not just closing quickly. \
We're independently licensed, which means our loyalty is to you, not to a single lender. \
Get your free rate quote today.""",

    "Handyman": """\
{biz} is {city}'s reliable handyman service for all the home repairs and maintenance tasks \
that pile up on your to-do list. From hanging doors and fixing drywall to caulking bathrooms, \
patching roofs, installing ceiling fans, and assembling furniture — we handle hundreds of \
repair types that don't require a specialized contractor.

Our handymen arrive on time, in uniform, with a fully stocked truck so most jobs are completed \
in a single visit. We charge transparent hourly and flat rates — no bait-and-switch estimates. \
All work is backed by our satisfaction guarantee, and our team is background-checked, \
licensed where required, and fully insured.

{city} homeowners and landlords rely on us to keep properties in top shape without the hassle \
of finding and coordinating multiple specialists. We also offer home maintenance packages \
for seasonal check-ups and preventive care. Schedule your visit online today — \
same-week availability in most areas.""",
}

# ── Card display data ─────────────────────────────────────────────────────────
CARD_SNIPPETS = {
    "HVAC":             "Expert heating & cooling installation, repairs, and tune-ups for homes and businesses.",
    "Legal":            "Experienced attorneys serving individuals, families, and businesses with personalized care.",
    "Cleaning":         "Professional home and office cleaning with eco-friendly products and a re-clean guarantee.",
    "Contracting":      "Licensed general contractors for remodels, additions, and new construction projects.",
    "Digital Marketing":"Results-driven SEO, paid ads, and social media to grow your online presence and leads.",
    "Accounting":       "CPA-led bookkeeping, tax prep, and financial planning for individuals and small businesses.",
    "IT Services":      "Managed IT support, cybersecurity, and network solutions with 24/7 monitoring.",
    "Pest Control":     "State-licensed exterminators using targeted IPM treatments safe for kids and pets.",
    "Plumbing":         "Licensed plumbers for repairs, installations, and 24/7 emergency service.",
    "Landscaping":      "Full-service lawn care, landscape design, and hardscaping for curb appeal you'll love.",
    "Roofing":          "Expert roof repairs, full replacements, and inspections backed by a written warranty.",
    "Electrical":       "Licensed electricians for panel upgrades, EV chargers, lighting, and safety inspections.",
    "Moving":           "Licensed movers handling packing, loading, transport, and storage with care.",
    "Painting":         "Interior and exterior painting using premium paints — surfaces prepped, clean-up included.",
    "Flooring":         "Hardwood, LVP, tile, and carpet installation plus hardwood refinishing.",
    "Home Security":    "24/7 monitored security systems with cameras, smart locks, and rapid emergency response.",
    "Solar Energy":     "Custom solar panel installations to slash your energy bill — federal tax credit eligible.",
    "Pool & Spa":       "Weekly pool service, repairs, and full pool construction for {city} homeowners.",
    "Auto Repair":      "ASE-certified mechanics for all makes and models with transparent digital inspections.",
    "Pet Services":     "Grooming, boarding, daycare, and training for dogs and cats by certified pet professionals.",
    "Personal Training":"Certified personal trainers delivering customized workout plans and real results.",
    "Tutoring":         "One-on-one K–12 tutoring in all subjects, SAT/ACT prep, and learning support.",
    "Mortgage":         "Licensed mortgage advisors shopping dozens of lenders for your best rate and terms.",
    "Handyman":         "Trusted handyman for repairs, installations, and maintenance — same-week availability.",
    "Local Business":   "Trusted local professionals serving your community with quality and care.",
}

CARD_SERVICES = {
    "HVAC":             ["AC Installation", "Heating Repair", "Maintenance Plans"],
    "Legal":            ["Free Consultation", "Personal Injury", "Family Law"],
    "Cleaning":         ["Deep Cleaning", "Move-In/Out", "Weekly Service"],
    "Contracting":      ["Kitchen Remodels", "Home Additions", "Commercial Build-Out"],
    "Digital Marketing":["SEO & SEM", "Paid Ads", "Social Media"],
    "Accounting":       ["Tax Preparation", "Bookkeeping", "Payroll"],
    "IT Services":      ["Managed IT", "Cybersecurity", "Cloud Migration"],
    "Pest Control":     ["Termite Control", "Rodent Removal", "Quarterly Plans"],
    "Plumbing":         ["Drain Cleaning", "Water Heaters", "Emergency Service"],
    "Landscaping":      ["Lawn Maintenance", "Landscape Design", "Irrigation"],
    "Roofing":          ["Roof Replacement", "Storm Damage", "Gutter Install"],
    "Electrical":       ["Panel Upgrades", "EV Chargers", "Lighting Install"],
    "Moving":           ["Local Moves", "Long Distance", "Packing & Storage"],
    "Painting":         ["Interior Painting", "Exterior Painting", "Cabinet Refinishing"],
    "Flooring":         ["Hardwood Install", "LVP & Laminate", "Tile & Refinishing"],
    "Home Security":    ["24/7 Monitoring", "Camera Systems", "Smart Locks"],
    "Solar Energy":     ["Panel Installation", "Battery Storage", "Tax Credit Help"],
    "Pool & Spa":       ["Weekly Service", "Equipment Repair", "Pool Construction"],
    "Auto Repair":      ["Oil & Brakes", "Engine Diagnostics", "Same-Day Repair"],
    "Pet Services":     ["Dog Grooming", "Boarding & Daycare", "Obedience Training"],
    "Personal Training":["Custom Programs", "Nutrition Coaching", "Group Sessions"],
    "Tutoring":         ["Math & Science", "SAT/ACT Prep", "All Grade Levels"],
    "Mortgage":         ["Purchase Loans", "Refinancing", "Rate Shopping"],
    "Handyman":         ["Repairs & Fixes", "Installations", "Maintenance Plans"],
    "Local Business":   ["Free Estimates", "Local Service", "Top Rated"],
}

CARD_RATINGS = ["4.7", "4.8", "4.9", "4.8", "5.0", "4.6", "4.8", "4.9", "4.7", "4.8"]
CARD_REVIEWS = [23, 47, 31, 62, 18, 54, 39, 28, 71, 45]

# ── FAQ content per category (renders as FAQPage schema + visible accordion) ──
FAQS = {
    "HVAC": [
        ("How much does HVAC repair cost in {city}?",
         "HVAC repair costs in {city} typically range from $150–$500 for minor fixes like a capacitor or refrigerant recharge, up to $1,500+ for compressor or coil replacement. Get 2–3 free estimates from local {city} HVAC companies before committing."),
        ("How often should I service my HVAC system?",
         "Most manufacturers recommend a professional tune-up twice a year — spring for your AC and fall for your heating system. Annual maintenance extends equipment life, improves efficiency, and catches small issues before they become expensive breakdowns."),
        ("What SEER rating should I look for?",
         "SEER (Seasonal Energy Efficiency Ratio) measures cooling efficiency. Modern systems run 14–25 SEER. In warmer climates a 16–18 SEER unit offers the best balance of upfront cost and long-term energy savings."),
        ("How long do HVAC systems last?",
         "Central AC units last 15–20 years and furnaces 20–30 years with proper maintenance. If your system is over 15 years old and needs a major repair, replacement is often more cost-effective. A local {city} HVAC technician can assess your system during a free inspection."),
        ("Do {city} HVAC companies offer emergency same-day service?",
         "Yes — most {city} HVAC companies provide 24/7 emergency service for situations like a broken AC in summer heat or a failed furnace in winter. Many charge no after-hours surcharge for genuine emergencies."),
    ],
    "Legal": [
        ("How do I find a good attorney in {city}?",
         "Start with a free consultation — most {city} law firms offer one. Look for attorneys who specialize in your specific issue (personal injury, family law, criminal defense, etc.), check their bar standing, and ask about fee structures before hiring."),
        ("What is a contingency fee?",
         "A contingency fee means you pay nothing unless your attorney wins your case. The attorney takes a percentage of the settlement or award — typically 25–40%. This arrangement is common in personal injury, workers' comp, and class-action cases."),
        ("How much does a lawyer cost in {city}?",
         "{city} attorney rates vary widely by practice area. Hourly rates typically range from $150–$500/hr for general practice up to $400–$800/hr for complex litigation. Many cases use flat-fee or contingency arrangements instead."),
        ("What should I bring to my first legal consultation?",
         "Bring all relevant documents: contracts, medical records, police reports, correspondence, photos, or anything related to your case. The more information your {city} attorney has upfront, the better they can assess your situation."),
        ("How long do legal cases take in {city}?",
         "Timelines vary significantly. Simple contract disputes may settle in weeks; personal injury cases often take 6–18 months; complex litigation can run 2–3 years. Your attorney can give you a realistic timeline after reviewing your specific situation."),
    ],
    "Cleaning": [
        ("How much does house cleaning cost in {city}?",
         "Professional house cleaning in {city} typically costs $100–$200 for a standard clean of a 1,500 sq ft home. Deep cleans, move-out cleans, and post-construction cleans run higher — usually $200–$400+. Most services offer free instant quotes online."),
        ("How often should I have my home professionally cleaned?",
         "Most homeowners schedule professional cleaning every 2–4 weeks. Weekly service suits busy households or homes with pets and kids; bi-weekly is the most popular frequency; monthly works well for single occupants or low-traffic homes."),
        ("Are cleaning products safe for kids and pets?",
         "Reputable {city} cleaning companies use EPA-approved, non-toxic products that are safe for children and pets. Ask your cleaning service about their product line — many offer fully green cleaning options at no extra charge."),
        ("Do I need to be home during the cleaning?",
         "No — most {city} cleaning clients provide a key or door code and aren't home during service. All professional cleaning staff are background-checked and insured, so you can feel comfortable leaving them access to your home."),
        ("What's included in a deep clean vs a regular clean?",
         "A regular clean covers standard surfaces, floors, bathrooms, and kitchen. A deep clean adds inside appliances, baseboards, window sills, ceiling fans, grout scrubbing, and other detail work. Most {city} cleaning companies recommend starting with a deep clean, then switching to maintenance visits."),
    ],
    "Contracting": [
        ("How do I find a licensed contractor in {city}?",
         "Always verify a contractor's license with {state}'s licensing board before hiring. Ask for proof of insurance, check reviews on Google and Houzz, and get at least three written bids. Licensed contractors in {city} are required to pull permits, protecting you legally."),
        ("How much does a home addition cost in {city}?",
         "Home additions in {city} average $150–$300 per square foot depending on complexity, materials, and finishes. A 400 sq ft addition could run $60,000–$120,000. Always get a detailed written estimate that breaks out labor, materials, and permits."),
        ("What permits are required for remodeling in {city}?",
         "Most structural changes, electrical work, plumbing, HVAC modifications, and additions require permits in {city}. Your licensed contractor should handle all permit applications. Unpermitted work can cause issues when you sell your home."),
        ("How long does a kitchen remodel take?",
         "A mid-sized kitchen remodel typically takes 4–8 weeks for an experienced {city} contractor. Complex projects with custom cabinetry and structural changes can run 10–16 weeks. Ask for a detailed project timeline in your written contract."),
        ("What should a contractor contract include?",
         "A solid contract should include: project scope and specifications, start and completion dates, payment schedule (never pay more than 10% upfront), materials list, change-order process, warranty terms, and proof of insurance. Your {city} contractor should provide all of this in writing."),
    ],
    "Digital Marketing": [
        ("How much does digital marketing cost in {city}?",
         "Digital marketing budgets in {city} vary widely. SEO retainers typically run $750–$3,000/month; PPC management 10–20% of ad spend; social media management $500–$2,500/month. Most agencies offer free audits so you can see the opportunity before committing."),
        ("How long does SEO take to show results?",
         "SEO is a long-term investment — most {city} businesses see meaningful ranking improvements in 3–6 months, with strong results at 9–12 months. Factors like domain age, competition, and content quality all affect the timeline."),
        ("What's better for {city} businesses — SEO or paid ads?",
         "Paid ads deliver immediate traffic but stop when your budget stops. SEO builds lasting organic visibility. Most {city} marketing agencies recommend running both: paid ads for quick wins while SEO compounds in the background."),
        ("How do I know if my digital marketing is working?",
         "Track the metrics that matter: organic traffic growth, keyword rankings, lead volume, cost per acquisition, and return on ad spend (ROAS). A good {city} marketing agency provides monthly reports and is proactive about strategy adjustments."),
        ("Do I need a website before running ads?",
         "Yes — your ads send traffic somewhere, and a slow or poorly designed landing page wastes your budget. Before investing in paid ads, ensure your {city} business website loads in under 3 seconds, works on mobile, and has clear calls to action."),
    ],
    "Accounting": [
        ("How much does a CPA cost in {city}?",
         "CPA rates in {city} range from $150–$400/hr for complex work. Tax return preparation for a small business typically runs $500–$2,500 depending on complexity. Monthly bookkeeping retainers start around $200–$800/month. Most {city} accounting firms offer a free initial consultation."),
        ("When should a small business hire an accountant?",
         "If you're spending more than 5 hours a month on bookkeeping, have employees, are considering business structure changes, or are facing an IRS notice — it's time. A {city} CPA typically saves businesses more than they cost through tax planning alone."),
        ("What's the difference between a CPA and a bookkeeper?",
         "A bookkeeper records daily transactions and reconciles accounts. A CPA (Certified Public Accountant) has advanced credentials, can prepare audited financial statements, represent you before the IRS, and provide strategic financial advice. Many {city} firms offer both services."),
        ("Can an accountant help me save on taxes in {city}?",
         "Absolutely. A proactive {city} CPA identifies legal deductions, advises on business structure (LLC vs S-corp), manages quarterly estimated taxes, and plans for capital events — typically saving small business owners thousands annually."),
        ("What records should I keep for my accountant?",
         "Keep all receipts for business expenses, bank statements, payroll records, mileage logs, invoices issued and received, and prior-year tax returns. Most {city} accountants recommend cloud-based accounting software like QuickBooks or Xero to keep everything organized."),
    ],
    "IT Services": [
        ("How much does managed IT support cost in {city}?",
         "Managed IT services in {city} typically cost $75–$200 per user per month, depending on the level of support and monitoring included. This is usually far less than a full-time IT employee and includes 24/7 monitoring, help desk support, and proactive maintenance."),
        ("What is managed IT and do I need it?",
         "Managed IT means outsourcing your technology management to a local {city} IT firm that monitors your systems around the clock, handles updates and patches, provides help desk support, and responds to issues — often before you even notice them."),
        ("How do I protect my {city} business from cyberattacks?",
         "Start with multi-factor authentication, up-to-date software and patches, employee phishing training, endpoint protection, and regular data backups. A {city} IT security firm can assess your current vulnerabilities and build a layered defense tailored to your business."),
        ("What's the best cloud backup solution for a small business?",
         "Leading options include Microsoft Azure Backup, Backblaze B2, and Veeam. The right choice depends on your data volume, recovery time objectives, and compliance requirements. Your {city} IT provider can recommend and manage the right solution for your size and industry."),
        ("How quickly can an IT company respond to emergencies in {city}?",
         "Reputable managed IT firms in {city} offer guaranteed response times — often 15–60 minutes for critical issues. Many provide 24/7 help desk support. Make sure your contract specifies response time SLAs before signing."),
    ],
    "Pest Control": [
        ("How much does pest control cost in {city}?",
         "A one-time pest treatment in {city} typically costs $150–$300. Ongoing quarterly service plans run $100–$200 per visit. Termite treatments are more involved — $500–$2,500 depending on treatment method and home size. Most companies offer a free inspection before quoting."),
        ("How long does a pest treatment take to work?",
         "Most residual pesticide treatments take 24–72 hours to fully eliminate active insects. For termites, liquid treatments work within days but full colony elimination can take 30–90 days. Your {city} exterminator will tell you what to expect for your specific pest and treatment type."),
        ("Are pest control chemicals safe for my family and pets?",
         "Licensed {city} pest control companies use EPA-registered products that are safe when applied correctly. Technicians will advise you on re-entry times (typically 1–4 hours) and any precautions for children and pets during and after treatment."),
        ("How do I prevent pests from coming back?",
         "Integrated Pest Management (IPM) combines sealing entry points, eliminating moisture and food sources, and scheduled preventive treatments. A quarterly protection plan from a {city} pest control company is the most reliable way to stay pest-free year-round."),
        ("When should I call an exterminator vs handle it myself?",
         "DIY products work for minor ant or roach issues. Call a licensed {city} exterminator for termites, bed bugs, rodents, wasps, or any infestation that's spread or recurring. These require professional-grade treatments and safety protocols."),
    ],
    "Plumbing": [
        ("How much does a plumber cost in {city}?",
         "Plumbers in {city} typically charge $75–$150/hr for standard work, with a $50–$100 service call fee. Common jobs: drain cleaning $100–$250, water heater installation $800–$1,500, pipe repair $200–$500. Emergency calls may carry a higher rate — always ask upfront."),
        ("What plumbing issues require emergency service?",
         "Call a {city} plumber immediately for: burst pipes, sewer backup, gas line issues, water heater failure, no water pressure, or flooding. Most {city} plumbing companies offer 24/7 emergency service with same-day response."),
        ("How do I know if I have a hidden water leak?",
         "Signs include an unexplained spike in your water bill, low water pressure, mold or mildew smell, wet spots on walls or ceilings, and the sound of running water when everything is off. A {city} plumber can perform a leak detection inspection to confirm."),
        ("How long does a water heater last?",
         "Traditional tank water heaters last 8–12 years; tankless units last 15–20 years. If yours is over 10 years old and showing signs of corrosion, rust-colored water, or inconsistent temperatures, consult a {city} plumber about replacement before it fails."),
        ("Should I repair or replace my water heater?",
         "If repairs cost more than 50% of a new unit and the heater is over 8 years old, replacement is usually smarter. A {city} plumber can assess your unit and give you an honest recommendation — a quality plumber won't push replacement if repair is the right call."),
    ],
    "Landscaping": [
        ("How much does lawn care cost in {city}?",
         "Weekly mowing and edging in {city} runs $30–$80 per visit depending on yard size. Monthly lawn care packages average $150–$400. Full landscape design and installation projects are priced per scope — most {city} landscapers offer free estimates."),
        ("How often should my lawn be mowed in {city}?",
         "During peak growing season, most {city} lawns need mowing every 7–10 days. Cool-season grasses may slow in summer heat; warm-season grasses grow fastest in summer. Your landscaper will recommend a frequency that keeps your lawn healthy without over-cutting."),
        ("What's the best time to plant in {city}?",
         "Planting timing depends on your plant type and {state}'s climate zone. Generally, spring (after last frost) and fall (6 weeks before first frost) are ideal for most plants. A {city} landscape designer can recommend plants suited to your specific soil and sun conditions."),
        ("How do I get rid of weeds without hurting my lawn?",
         "Pre-emergent herbicides applied in early spring prevent weed seeds from germinating. Post-emergent products target existing weeds. Thick, healthy turf is your best long-term defense — proper fertilization, watering, and mowing height all help. A {city} lawn care professional can develop a year-round program."),
        ("Do I need an irrigation system in {city}?",
         "Irrigation systems pay for themselves in water savings and plant health, especially during {city}'s dry seasons. A smart drip or sprinkler system installed by a {city} landscaper typically costs $2,500–$6,000 and can reduce outdoor water use by 30–50%."),
    ],
    "Roofing": [
        ("How much does roof replacement cost in {city}?",
         "A full roof replacement in {city} typically costs $8,000–$18,000 for an average-sized home with asphalt shingles, depending on roof size, pitch, and materials. Metal and tile roofs run higher. Get 2–3 free estimates from licensed {city} roofing contractors."),
        ("How long does a roof last?",
         "Asphalt shingles: 20–30 years. Architectural shingles: 25–30 years. Metal roofing: 40–70 years. Tile: 50+ years. Regular inspections by a {city} roofing contractor can catch minor issues and extend your roof's life significantly."),
        ("How do I know if my roof needs replacement vs repair?",
         "Signs you may need replacement: shingles curling, cracking, or missing in large areas; granules in gutters; daylight through attic; roof age over 20 years; repeated leaks after repairs. A licensed {city} roofer can assess during a free inspection."),
        ("Does homeowner's insurance cover roof replacement in {city}?",
         "Most {state} homeowner's policies cover storm-related damage (wind, hail) but not normal wear and tear. After a severe storm, have a licensed {city} roofing contractor document the damage before you file a claim — they can often assist with the insurance process."),
        ("How long does a roof replacement take?",
         "Most residential roof replacements in {city} are completed in 1–2 days by an experienced crew. Larger or more complex roofs may take 2–3 days. Your {city} roofer should give you a clear timeline and communicate any weather-related delays."),
    ],
    "Electrical": [
        ("How much does an electrician cost in {city}?",
         "Electricians in {city} charge $75–$150/hr, with a $50–$100 service call fee. Common jobs: outlet installation $100–$200, panel upgrade $1,500–$3,500, EV charger installation $500–$1,200. Always get a written estimate before work begins."),
        ("When do I need to upgrade my electrical panel?",
         "Panel upgrades are needed when: you're adding major appliances, installing EV charging, adding a home addition, or your panel is under 100 amps (or over 25 years old with fuses). A {city} electrician can assess your panel during a free safety inspection."),
        ("Is it safe to DIY electrical work in {city}?",
         "Minor tasks like replacing a light switch or outlet cover are generally safe for DIYers. But anything involving your panel, new circuits, or structural wiring must be done by a licensed {city} electrician — unpermitted electrical work is dangerous and can void your home insurance."),
        ("How do I know if I have faulty wiring?",
         "Warning signs: flickering lights, tripped breakers, burning smell, discolored outlets, sparks, or a buzzing sound from your panel. If you notice any of these in your {city} home, call a licensed electrician immediately — faulty wiring is a leading cause of house fires."),
        ("Can an electrician install EV charging in {city}?",
         "Yes — most licensed {city} electricians install Level 2 EV chargers (240V). The process involves adding a dedicated circuit, installing the charger unit, and pulling the required permit. Total cost typically runs $500–$1,200 installed, and federal tax credits may apply."),
    ],
    "Moving": [
        ("How much does it cost to hire movers in {city}?",
         "Local moves in {city} (under 50 miles) typically cost $100–$200/hr for a 2-person crew, with most moves totaling $400–$1,500 depending on home size. Long-distance moves are usually quoted by weight and distance. Always get an in-home or virtual estimate."),
        ("How far in advance should I book movers in {city}?",
         "Book at least 4–6 weeks ahead for peak season (May–September) and month-end dates. For off-peak moves, 2 weeks is usually sufficient. The best {city} moving companies fill up fast — don't wait until the week before."),
        ("What's the difference between a binding and non-binding moving estimate?",
         "A binding estimate is a guaranteed price. A non-binding estimate is based on weight and may change. Always request a binding estimate from your {city} mover to avoid surprise charges on moving day. Reputable movers provide these in writing."),
        ("How do I protect my valuables during a move in {city}?",
         "Keep irreplaceable items (jewelry, documents, hard drives) with you personally. Use quality packing materials for fragile items, and photograph valuables before packing. Verify that your {city} moving company carries full-value protection insurance, not just released-liability coverage."),
        ("Are {city} moving companies required to be licensed?",
         "Yes — interstate movers must be registered with the FMCSA and have a USDOT number. Local {city} movers must hold a state license. Always verify before booking, and avoid any mover that refuses to provide written estimates or asks for a large cash deposit upfront."),
    ],
    "Painting": [
        ("How much does interior painting cost in {city}?",
         "Interior painting in {city} typically costs $2–$6 per square foot of wall space, or $1,500–$4,000 for an average 3-bedroom home. Cost depends on ceiling height, number of colors, surface prep needed, and finish quality. Get 2–3 free quotes from licensed {city} painters."),
        ("How long does interior painting take?",
         "A professional {city} painting crew can paint a 3-bedroom home in 2–4 days. Exterior projects depend on home size and prep needs — most run 3–5 days. Proper surface prep (caulking, priming, sanding) is what separates a lasting paint job from one that peels in two years."),
        ("What's the best paint sheen for each room?",
         "Flat/matte: low-traffic areas like bedrooms and ceilings. Eggshell: living rooms and dining rooms. Satin: kitchens, bathrooms, hallways. Semi-gloss: trim, doors, and high-moisture areas. Your {city} painter can help you choose the right sheen and finish for each space."),
        ("How do I prepare my home for interior painting?",
         "Remove fragile items and move furniture to room centers. Your {city} painting crew will cover floors and furniture with drop cloths, tape trim and outlets, and fill holes and cracks before painting. You don't need to do much beyond clearing the space."),
        ("How long does exterior paint last in {city}?",
         "Quality exterior paint in {city}'s climate lasts 5–10 years. Proper surface preparation — pressure washing, sanding, priming, and caulking — is the biggest factor in longevity. A professional paint job from a {city} contractor significantly outlasts DIY work."),
    ],
    "Flooring": [
        ("How much does hardwood floor installation cost in {city}?",
         "Solid hardwood installation in {city} runs $8–$15 per square foot installed. Engineered hardwood is $5–$10/sq ft; luxury vinyl plank $4–$8/sq ft; carpet $3–$7/sq ft. Most {city} flooring companies offer free in-home estimates including subfloor assessment."),
        ("Hardwood vs luxury vinyl plank — which is better?",
         "Hardwood adds more resale value and can be refinished multiple times. LVP is 100% waterproof, more durable against scratches, and easier to install. For kitchens, bathrooms, or homes with pets and kids, LVP is often the smarter choice. Your {city} flooring specialist can walk you through both options."),
        ("How long does floor installation take?",
         "A typical 1,000 sq ft installation takes 1–3 days for an experienced {city} flooring crew. Add time for subfloor prep and acclimation (hardwood needs 3–5 days to acclimate to your home's humidity before installation)."),
        ("Can hardwood floors be refinished instead of replaced?",
         "Yes — solid hardwood can typically be sanded and refinished 3–5 times over its lifetime. Refinishing costs $3–$5 per square foot, a fraction of replacement cost. A {city} flooring company can assess your floor's thickness and condition to see if it's a candidate."),
        ("What subfloor conditions are needed for new flooring?",
         "Your subfloor must be dry, level (within 3/16\" over 10 feet), structurally sound, and free of squeaks. Moisture is the enemy of hardwood and laminate — your {city} flooring installer should conduct a moisture test before installation begins."),
    ],
    "Home Security": [
        ("How much does a home security system cost in {city}?",
         "Professional security systems in {city} typically cost $200–$800 for equipment, plus $20–$60/month for 24/7 monitoring. Smart home integration (cameras, smart locks, video doorbell) adds to equipment cost. Many companies offer $0-down equipment with a monitoring contract."),
        ("Do I need a professional installer or can I DIY?",
         "DIY systems (Ring, SimpliSafe, Wyze) are cheaper and flexible but lack professional installation and often have higher false-alarm rates. Professional {city} security companies handle installation, system programming, and integrate all devices for maximum reliability."),
        ("What deters burglars most effectively?",
         "Studies show visible security cameras, alarm system signage, motion-activated lighting, and reinforced door locks are the most effective deterrents. A {city} security professional can assess your home's vulnerabilities and recommend a layered approach."),
        ("How fast does a monitoring center respond in {city}?",
         "Professional monitoring centers have average response times of 30–45 seconds. When an alarm triggers, they attempt to contact you, then dispatch police, fire, or medical services as needed. Local {city} response times after dispatch depend on your area's emergency services."),
        ("Does a security system lower my homeowner's insurance in {city}?",
         "Yes — most {state} insurance carriers offer 5–20% discounts for professionally monitored security systems. Discounts vary by carrier and system type. Ask your {city} security company to provide documentation for your insurance agent."),
    ],
    "Solar Energy": [
        ("How much do solar panels cost in {city}?",
         "A typical residential solar installation in {city} costs $15,000–$25,000 before incentives. After the 30% federal tax credit (ITC), the net cost drops to $10,500–$17,500. Most {city} homeowners break even in 6–10 years and save $20,000–$40,000 over the system's lifetime."),
        ("What solar incentives are available in {state}?",
         "{state} homeowners can claim the 30% federal Investment Tax Credit (ITC) on the full cost of their solar system. {state} may also offer additional state tax credits, net metering policies, and utility rebates. A {city} solar installer can identify every incentive you qualify for."),
        ("How much can solar reduce my electricity bill in {city}?",
         "Most {city} homeowners eliminate 70–100% of their electricity bill with a properly sized solar system. Your exact savings depend on your current usage, roof size and orientation, and local utility rates. A {city} solar company will model your savings before you sign anything."),
        ("Do solar panels work on cloudy days?",
         "Yes — solar panels generate electricity from daylight, not direct sun. They're less efficient on cloudy days (typically 10–25% of peak output) but still produce meaningful energy. {city} homeowners in cloudier climates still achieve excellent payback through net metering."),
        ("How long do solar panels last?",
         "Quality solar panels carry 25-year performance warranties and often last 30–40 years. System output degrades slowly — about 0.5% per year. Your {city} solar installer will show you a production model projecting output over the full warranty period."),
    ],
    "Pool & Spa": [
        ("How much does pool maintenance cost in {city}?",
         "Weekly pool service in {city} typically costs $100–$200/month for chemical balancing, cleaning, and equipment checks. Equipment repairs are billed separately. Many {city} pool companies offer bundled service plans that include chemical costs and a set number of repairs per year."),
        ("How often should my pool be serviced?",
         "During swim season, weekly service is standard. Off-season, every 2 weeks is often sufficient. Pools left unserviced quickly develop algae, imbalanced chemistry, and equipment wear. A regular {city} pool service plan is the most cost-effective way to protect your investment."),
        ("How do I close my pool for winter in {city}?",
         "Pool winterization in {city} involves balancing chemicals, lowering the water level, blowing out lines, adding antifreeze (in freeze-risk areas), covering the pool, and winterizing the pump and filter. Most {city} pool companies offer seasonal closing packages starting at $150–$300."),
        ("How long does pool construction take in {city}?",
         "A typical in-ground pool build in {city} takes 6–12 weeks from excavation to final inspection, depending on design complexity, material availability, and permit timelines. Your {city} pool builder should provide a detailed timeline with milestones before construction begins."),
        ("What chemicals do I need to maintain my pool?",
         "Core pool chemicals include chlorine (sanitizer), pH increaser/decreaser, alkalinity increaser, calcium hardness increaser, and algaecide. Target ranges: pH 7.2–7.6, chlorine 1–3 ppm, alkalinity 80–120 ppm. A {city} pool service tech will handle all of this on your weekly service visits."),
    ],
    "Auto Repair": [
        ("How do I know if an auto repair shop in {city} is trustworthy?",
         "Look for ASE-certified technicians, verified Google reviews (4.5+ stars with 50+ reviews), written estimates before work begins, and a clear warranty on parts and labor. The best {city} shops are transparent about what they find and never pressure you into repairs."),
        ("How much does an oil change cost in {city}?",
         "Conventional oil changes in {city} run $30–$60; synthetic oil changes $60–$120 depending on vehicle. Dealer service centers charge more; independent {city} shops are typically 20–40% less for the same quality work."),
        ("How often should I get my brakes inspected?",
         "Have brakes inspected every 12,000 miles or annually, whichever comes first. Signs you need brake service: squealing or grinding noise, vibration when braking, a soft pedal, or the brake warning light. Don't delay — brakes are a safety-critical system."),
        ("What is a digital vehicle inspection?",
         "Modern {city} auto shops use tablet-based digital inspections that include photos of your vehicle's actual condition. You see exactly what the technician sees — no more guessing whether a recommended repair is legitimate. Ask any {city} shop if they offer digital inspections."),
        ("What warranty should I expect on auto repairs in {city}?",
         "Reputable {city} auto repair shops offer 12-month/12,000-mile warranties on parts and labor as a minimum standard. Some shops offer 24-month/24,000-mile warranties. Ask about warranty coverage before approving any repair."),
    ],
    "Pet Services": [
        ("How often should my dog be groomed in {city}?",
         "Most dogs benefit from professional grooming every 4–8 weeks. Short-coated breeds can go 8–12 weeks; long-coated or double-coated breeds typically need grooming every 4–6 weeks to prevent matting. Your {city} groomer can recommend the right schedule for your breed."),
        ("What should I look for in a dog boarding facility in {city}?",
         "Visit in person before booking. Look for clean facilities, adequate space, separated areas by dog size, staff-to-dog ratios (ideally 1:10 or better), vaccination requirements for all guests, and 24-hour supervision. Ask to see the sleeping areas and outdoor runs."),
        ("Is doggy daycare worth it for my dog?",
         "Daycare is excellent for high-energy dogs, those prone to separation anxiety, and dogs that thrive on socialization. A well-run {city} daycare provides structured play, rest periods, and monitoring — resulting in a calmer, happier dog at home."),
        ("How do I find a certified dog trainer in {city}?",
         "Look for trainers certified by the CCPDT (Certified Professional Dog Trainer) or IAABC. Positive reinforcement methods are the gold standard — avoid trainers who rely on punishment or dominance-based techniques. Most {city} trainers offer free consultations."),
        ("What vaccinations are required for boarding and daycare in {city}?",
         "Most {city} pet facilities require current rabies, DHPP (distemper combo), and Bordetella (kennel cough) vaccinations. Some also require the canine influenza vaccine. Check your facility's specific requirements when booking and ensure your vet records are up to date."),
    ],
    "Personal Training": [
        ("How much does a personal trainer cost in {city}?",
         "Personal training in {city} typically costs $60–$120 per session for one-on-one training. Package rates lower the per-session cost. Semi-private (2–4 people) training runs $30–$60/session. Online coaching with a {city} trainer runs $100–$300/month."),
        ("How many personal training sessions do I need to see results?",
         "Most clients see noticeable changes in 4–8 weeks of consistent training (3x/week) combined with nutritional improvements. Significant body composition changes typically take 3–6 months. Consistency is far more important than frequency — 2 quality sessions per week beats 5 inconsistent ones."),
        ("Should I get a personal trainer if I'm a beginner?",
         "Absolutely — beginners benefit most from professional guidance. A {city} personal trainer teaches proper form from the start (preventing injuries), sets realistic expectations, and builds habits that last. The investment pays dividends for years."),
        ("What should I look for in a personal trainer's credentials?",
         "Look for certifications from NASM, ACE, NSCA, or ACSM — the four most recognized bodies. Additionally, check for CPR/AED certification, liability insurance, and experience with clients who have similar goals or conditions as yours."),
        ("Can a personal trainer help me lose weight?",
         "Training is one piece of the puzzle. A qualified {city} personal trainer will combine resistance training (which preserves muscle and boosts metabolism) with cardio programming and nutritional guidance. Clients who train consistently and improve their nutrition typically lose 1–2 lbs per week safely."),
    ],
    "Tutoring": [
        ("How much does tutoring cost in {city}?",
         "Private tutoring in {city} runs $40–$100/hr for most subjects; SAT/ACT prep and specialized subjects can run $80–$150/hr. Online tutoring is generally 20–30% less. Many {city} tutoring centers offer package rates and free initial assessments."),
        ("How do I know if my child needs a tutor?",
         "Common signs: dropping grades, avoiding homework, loss of confidence in school, teacher concerns, or struggling with a specific subject. Early intervention is key — the sooner a {city} tutor identifies and addresses gaps, the faster progress happens."),
        ("How often should my child meet with a tutor?",
         "Most students benefit from 1–2 sessions per week. For SAT/ACT prep or urgent grade recovery, 2–3 sessions per week is more effective. Consistency matters more than volume — regular 60–90 minute sessions with homework in between produce the best results."),
        ("What's the difference between a tutoring center and private tutoring?",
         "Tutoring centers offer structured programs, consistent availability, and group sessions — often at lower cost. Private tutors provide completely personalized attention and flexible scheduling. Both are effective; the best fit depends on your child's learning style and your family's schedule."),
        ("How long does SAT/ACT prep take?",
         "Most students see meaningful score improvements (50–150+ points on SAT) with 40–80 hours of focused prep over 3–4 months. Starting prep 4–6 months before your target test date gives enough time for content review, practice tests, and score analysis."),
    ],
    "Mortgage": [
        ("What credit score do I need for a mortgage in {city}?",
         "Conventional loans typically require a 620+ credit score; FHA loans accept scores as low as 580 (with 3.5% down) or 500 (with 10% down); VA loans have no minimum score set by the VA but lenders usually require 580–620. Your {city} mortgage advisor can help you understand your options."),
        ("How much do I need for a down payment in {city}?",
         "Conventional loans start at 3% down; FHA loans require 3.5%; VA and USDA loans are 0% down for qualifying buyers. First-time buyer programs in {state} may offer down payment assistance. Your {city} mortgage advisor can identify every program you qualify for."),
        ("What's the difference between pre-qualification and pre-approval?",
         "Pre-qualification is a quick estimate based on self-reported information. Pre-approval is a verified commitment — lenders check your credit, income, and assets and issue a formal letter. In competitive {city} markets, sellers strongly prefer buyers with pre-approval letters."),
        ("How long does it take to close on a home in {city}?",
         "Most purchase loans close in 30–45 days; refinances typically close in 20–30 days. Your {city} mortgage company will give you a clear timeline at application. Delays usually stem from appraisals, title issues, or missing documentation — your loan officer will keep you informed."),
        ("Is it worth refinancing my mortgage right now?",
         "The classic rule is to refinance if you can drop your rate by 1%+ and recoup closing costs within 2 years. But every situation is different. A {city} mortgage advisor can run a break-even analysis in minutes to show you exactly when refinancing makes sense for your loan."),
    ],
    "Handyman": [
        ("How much does a handyman cost in {city}?",
         "Handyman rates in {city} typically run $60–$120/hr, with most companies having a 2-hour minimum. Flat-rate pricing is common for defined jobs (e.g., TV mounting $100–$150, ceiling fan install $75–$125, drywall patch $100–$250). Always get a written estimate before work starts."),
        ("What jobs does a handyman do vs a licensed contractor?",
         "Handymen handle general repairs, installations, and maintenance that don't require a specialty license — drywall, caulking, door hardware, furniture assembly, minor carpentry. Jobs involving structural changes, electrical panels, plumbing lines, or gas require licensed {city} contractors with permits."),
        ("How do I find a reliable handyman in {city}?",
         "Ask neighbors for referrals, check Google and Nextdoor reviews, verify they're insured (ask for a certificate), and get a written scope and estimate before any work begins. Reliable {city} handymen are booked out 1–2 weeks — if someone is immediately available at a very low price, be cautious."),
        ("Can a handyman do multiple small jobs in one visit?",
         "Yes — this is one of a handyman's biggest advantages over specialty contractors. Most {city} handymen will work through your honey-do list in a single visit, making efficient use of the minimum charge. Group your small jobs together to maximize value."),
        ("Is a handyman insured in {city}?",
         "Always ask for proof of general liability insurance before letting anyone into your home. Professional {city} handyman services carry at least $1M in liability coverage. This protects you if they accidentally damage your property or cause an injury on site."),
    ],
}

# ── Cross-category suggestions (shown on business detail pages) ──────────────
CROSS_CATS = {
    "HVAC":             [("Electrical", "⚡"), ("Plumbing", "🔧"), ("Home Security", "🔒")],
    "Legal":            [("Accounting", "📊"), ("Mortgage", "🏡"), ("IT Services", "💻")],
    "Cleaning":         [("Handyman", "🛠️"), ("Pest Control", "🐛"), ("Flooring", "🪵")],
    "Contracting":      [("Electrical", "⚡"), ("Plumbing", "🔧"), ("Flooring", "🪵")],
    "Digital Marketing":[("IT Services", "💻"), ("Accounting", "📊"), ("Contracting", "🔨")],
    "Accounting":       [("Legal", "⚖️"), ("Digital Marketing", "📈"), ("IT Services", "💻")],
    "IT Services":      [("Digital Marketing", "📈"), ("Home Security", "🔒"), ("Accounting", "📊")],
    "Pest Control":     [("Cleaning", "🧹"), ("Handyman", "🛠️"), ("Landscaping", "🌿")],
    "Plumbing":         [("HVAC", "❄️"), ("Electrical", "⚡"), ("Handyman", "🛠️")],
    "Landscaping":      [("Pest Control", "🐛"), ("Pool & Spa", "🏊"), ("Handyman", "🛠️")],
    "Roofing":          [("Electrical", "⚡"), ("Contracting", "🔨"), ("Painting", "🎨")],
    "Electrical":       [("HVAC", "❄️"), ("Home Security", "🔒"), ("Solar Energy", "☀️")],
    "Moving":           [("Handyman", "🛠️"), ("Cleaning", "🧹"), ("Flooring", "🪵")],
    "Painting":         [("Flooring", "🪵"), ("Contracting", "🔨"), ("Handyman", "🛠️")],
    "Flooring":         [("Painting", "🎨"), ("Contracting", "🔨"), ("Cleaning", "🧹")],
    "Home Security":    [("Electrical", "⚡"), ("IT Services", "💻"), ("Handyman", "🛠️")],
    "Solar Energy":     [("Electrical", "⚡"), ("Roofing", "🏠"), ("Home Security", "🔒")],
    "Pool & Spa":       [("Landscaping", "🌿"), ("Electrical", "⚡"), ("Plumbing", "🔧")],
    "Auto Repair":      [("Electrical", "⚡"), ("Handyman", "🛠️"), ("IT Services", "💻")],
    "Pet Services":     [("Cleaning", "🧹"), ("Landscaping", "🌿"), ("Handyman", "🛠️")],
    "Personal Training":[("Tutoring", "📚"), ("Accounting", "📊"), ("IT Services", "💻")],
    "Tutoring":         [("Personal Training", "💪"), ("IT Services", "💻"), ("Legal", "⚖️")],
    "Mortgage":         [("Legal", "⚖️"), ("Accounting", "📊"), ("Contracting", "🔨")],
    "Handyman":         [("Plumbing", "🔧"), ("Electrical", "⚡"), ("Painting", "🎨")],
}

# ── Target listings per city ──────────────────────────────────────────────────
TARGET_PER_CITY = 200
# Spread target evenly across 12 categories — 17 per category = 204 min baseline
LISTINGS_PER_CAT = 41


# ── Helpers ───────────────────────────────────────────────────────────────────
def detect_category(filename):
    fn = os.path.splitext(os.path.basename(filename))[0].lower()
    segments = set(re.split(r'[_\-\s]+', fn))
    for key, meta in CATEGORY_MAP.items():
        for kw in meta["keywords"]:
            kw_segs = set(kw.split('_'))
            if kw_segs.issubset(segments):
                return meta["label"], meta["emoji"], meta["css"]
    return "Local Business", "🏢", ""

def generate_biz_name(filename, city_name):
    fn = os.path.splitext(os.path.basename(filename))[0].lower()
    segments = set(re.split(r'[_\-\s]+', fn))
    num_match = re.search(r'_(\d+)$', fn)
    file_num = int(num_match.group(1)) - 1 if num_match else 0
    for cat_key in sorted(CITY_BIZ_NAMES.keys(), key=len, reverse=True):
        kw_segs = set(cat_key.split('_'))
        if kw_segs.issubset(segments):
            templates = CITY_BIZ_NAMES[cat_key]
            idx = (len(city_name) + file_num) % len(templates)
            return templates[idx].replace("{city}", city_name)
    return city_name + " Professionals"

def extract_business_name(filename, city_name):
    try:
        with open(filename) as f:
            content = f.read()
        m = re.search(r'<h1[^>]*>([^<]+)</h1>', content, re.IGNORECASE)
        if m:
            raw = m.group(1).strip()
            raw = re.sub(r'^[^-]+-\s*', '', raw).strip()
            if re.search(r'_(hvac|legal|cleaning|contracting|marketing|accounting|it|pest|plumbing|landscaping|roofing|electrical)', raw, re.I):
                return generate_biz_name(filename, city_name)
            if raw.endswith('Professionals'):
                return generate_biz_name(filename, city_name)
            if raw and '_' not in raw and len(raw) > 3:
                return raw
    except Exception:
        pass
    return generate_biz_name(filename, city_name)

def jsonld_local_business(biz_name, cat_label, city_name, state, page_url):
    return f"""  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "LocalBusiness",
    "name": "{biz_name}",
    "description": "Professional {cat_label.lower()} services in {city_name}, {state}.",
    "address": {{
      "@type": "PostalAddress",
      "addressLocality": "{city_name}",
      "addressRegion": "{state}",
      "addressCountry": "US"
    }},
    "url": "{page_url}",
    "aggregateRating": {{
      "@type": "AggregateRating",
      "ratingValue": "4.8",
      "reviewCount": "47"
    }}
  }}
  </script>"""

def jsonld_breadcrumb(crumbs):
    items = []
    for i, (name, url) in enumerate(crumbs):
        items.append(f'{{"@type":"ListItem","position":{i+1},"name":"{name}","item":"{url}"}}')
    return f"""  <script type="application/ld+json">
  {{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{",".join(items)}]}}
  </script>"""


# ── City index page ───────────────────────────────────────────────────────────
def city_index_html(city_slug, city_name, state, emoji, listings, state_cities=None):
    cards = ""
    for i, (biz_name, cat_label, cat_emoji, fname) in enumerate(listings):
        snippet = CARD_SNIPPETS.get(cat_label, CARD_SNIPPETS["Local Business"])
        services = CARD_SERVICES.get(cat_label, CARD_SERVICES["Local Business"])
        rating = CARD_RATINGS[i % len(CARD_RATINGS)]
        review_count = CARD_REVIEWS[i % len(CARD_REVIEWS)]
        service_pills = "".join(f'<span class="svc-pill">{s}</span>' for s in services)
        stars = "★" * int(float(rating)) + ("" if float(rating) == int(float(rating)) else "½")
        cards += f"""
    <a href="/{city_slug}/{fname}" class="listing-card">
      <div class="listing-card-header">
        <div class="listing-avatar">{cat_emoji}</div>
        <div>
          <div class="name">{biz_name}</div>
          <div class="category-tag">{cat_label}</div>
        </div>
      </div>
      <div class="listing-card-body">
        <div class="card-rating"><span class="stars">{stars}</span> <strong>{rating}</strong> <span class="review-ct">({review_count} reviews)</span></div>
        <div class="card-snippet">{snippet}</div>
        <div class="card-services">{service_pills}</div>
        <div class="listing-detail"><span class="di">📍</span> {city_name}, {state}</div>
      </div>
      <div class="listing-card-actions">
        <div class="btn-primary">View Details →</div>
      </div>
    </a>"""

    count = len(listings)
    page_url = f"{DOMAIN}/{city_slug}/"
    breadcrumb_ld = jsonld_breadcrumb([("Home", DOMAIN), (city_name, page_url)])

    # State cities internal linking section
    if state_cities:
        sc_links = " &nbsp;·&nbsp; ".join(
            f'<a href="/{slug}/" style="color:var(--blue);text-decoration:none;">{name}</a>'
            for slug, name in state_cities[:20] if slug != city_slug
        )
        state_cities_section = f"""<div class="section" style="padding-top:0">
  <h2 class="section-title" style="font-size:1rem;">More Cities in {state}</h2>
  <p style="font-size:0.85rem;color:var(--gray-600);line-height:1.9;">{sc_links}</p>
</div>"""
    else:
        state_cities_section = ""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name='impact-site-verification' value='6b714473-0498-4933-83ec-09fb32acd5fa'>
  <title>{city_name} Local Professionals — AllCityPros</title>
  <meta name="description" content="Find top-rated {city_name} professionals: HVAC, legal, cleaning, contracting, digital marketing, accounting, IT and more. {count} local businesses listed.">
  <link rel="canonical" href="{page_url}">
  <meta property="og:title" content="{city_name} Local Professionals — AllCityPros">
  <meta property="og:description" content="Discover {count} top-rated professionals in {city_name}, {state}. Compare services and get free quotes.">
  <meta property="og:type" content="website">
{breadcrumb_ld}
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/styles.css">
</head>
<body>

<header class="site-header">
  <a href="/" class="logo">AllCity<span>Pros</span></a>
  <button class="nav-toggle" aria-label="Toggle navigation" onclick="this.nextElementSibling.classList.toggle('open')">
    <span></span><span></span><span></span>
  </button>
  <nav class="header-nav">
    <a href="/">Cities</a>
    <a href="#">Categories</a>
    <a href="#">List Your Business</a>
  </nav>
</header>

<nav class="breadcrumb">
  <a href="/">Home</a>
  <span class="sep">›</span>
  <span>{city_name}</span>
</nav>

<section class="page-hero">
  <h1>{emoji} {city_name}, {state}</h1>
  <p>Top-rated local professionals serving {city_name} and surrounding areas</p>
</section>

<div class="category-strip">
  <div class="cat-pill active"><span class="icon">🏙️</span> All</div>
  <div class="cat-pill"><span class="icon">❄️</span> HVAC</div>
  <div class="cat-pill"><span class="icon">⚖️</span> Legal</div>
  <div class="cat-pill"><span class="icon">🧹</span> Cleaning</div>
  <div class="cat-pill"><span class="icon">🔨</span> Contracting</div>
  <div class="cat-pill"><span class="icon">📈</span> Digital Marketing</div>
  <div class="cat-pill"><span class="icon">📊</span> Accounting</div>
  <div class="cat-pill"><span class="icon">💻</span> IT Services</div>
  <div class="cat-pill"><span class="icon">🐛</span> Pest Control</div>
  <div class="cat-pill"><span class="icon">🔧</span> Plumbing</div>
  <div class="cat-pill"><span class="icon">🌿</span> Landscaping</div>
  <div class="cat-pill"><span class="icon">🏠</span> Roofing</div>
  <div class="cat-pill"><span class="icon">⚡</span> Electrical</div>
  <div class="cat-pill"><span class="icon">🚛</span> Moving</div>
  <div class="cat-pill"><span class="icon">🎨</span> Painting</div>
  <div class="cat-pill"><span class="icon">🪵</span> Flooring</div>
  <div class="cat-pill"><span class="icon">🔒</span> Home Security</div>
  <div class="cat-pill"><span class="icon">☀️</span> Solar Energy</div>
  <div class="cat-pill"><span class="icon">🏊</span> Pool &amp; Spa</div>
  <div class="cat-pill"><span class="icon">🚗</span> Auto Repair</div>
  <div class="cat-pill"><span class="icon">🐾</span> Pet Services</div>
  <div class="cat-pill"><span class="icon">💪</span> Personal Training</div>
  <div class="cat-pill"><span class="icon">📚</span> Tutoring</div>
  <div class="cat-pill"><span class="icon">🏡</span> Mortgage</div>
  <div class="cat-pill"><span class="icon">🛠️</span> Handyman</div>
</div>

<div class="section">
  <h2 class="section-title">{city_name} Professionals</h2>
  <p class="section-sub">{count} businesses listed in {city_name}</p>
  <div class="listing-grid">
{cards}
  </div>
</div>

<div class="section" style="padding-top:0">
  <div class="claim-banner">
    <div class="claim-text">
      <strong>Own a business in {city_name}?</strong>
      <span>Claim or add your listing — it's free to get started.</span>
    </div>
    <button type="button" class="claim-btn" style="cursor:pointer;border:none;"
      onclick="this.style.display='none';document.getElementById('city-claim-form').style.display='block';">
      List My Business →
    </button>
    <form id="city-claim-form" action="https://formspree.io/f/allcitypros-claim" method="POST"
      style="display:none;margin-top:14px;width:100%;">
      <input type="hidden" name="city" value="{city_name}, {state}">
      <input type="hidden" name="type" value="New Listing Request">
      <div style="display:flex;flex-wrap:wrap;gap:8px;">
        <input type="text" name="business_name" placeholder="Business name" required
          style="flex:1;min-width:160px;padding:9px 11px;border:1px solid var(--gray-200);border-radius:7px;font-size:0.85rem;font-family:inherit;">
        <input type="text" name="owner_name" placeholder="Your name" required
          style="flex:1;min-width:160px;padding:9px 11px;border:1px solid var(--gray-200);border-radius:7px;font-size:0.85rem;font-family:inherit;">
        <input type="email" name="email" placeholder="Email address" required
          style="flex:1;min-width:160px;padding:9px 11px;border:1px solid var(--gray-200);border-radius:7px;font-size:0.85rem;font-family:inherit;">
        <input type="tel" name="phone" placeholder="Phone number"
          style="flex:1;min-width:160px;padding:9px 11px;border:1px solid var(--gray-200);border-radius:7px;font-size:0.85rem;font-family:inherit;">
        <input type="text" name="category" placeholder="Business category (e.g. HVAC)"
          style="flex:1;min-width:160px;padding:9px 11px;border:1px solid var(--gray-200);border-radius:7px;font-size:0.85rem;font-family:inherit;">
        <input type="url" name="website" placeholder="Website (optional)"
          style="flex:1;min-width:160px;padding:9px 11px;border:1px solid var(--gray-200);border-radius:7px;font-size:0.85rem;font-family:inherit;">
        <button type="submit" class="btn-primary"
          style="border:none;cursor:pointer;padding:10px 20px;font-size:0.85rem;border-radius:7px;font-weight:700;white-space:nowrap;">
          Submit for Review →
        </button>
      </div>
    </form>
  </div>
</div>

{state_cities_section}

<footer class="site-footer">
  <div class="footer-logo">AllCity<span>Pros</span></div>
  <p>Connecting people with trusted local professionals across America.</p>
  <p class="mt-4"><a href="#">Privacy Policy</a> &nbsp;·&nbsp; <a href="#">Terms of Service</a> &nbsp;·&nbsp; <a href="mailto:hello@allcitypros.com?subject=List My Business">List Your Business</a></p>
</footer>

</body>
</html>
"""


# ── Business detail page ──────────────────────────────────────────────────────
def business_page_html(city_slug, city_name, state, biz_name, cat_label, cat_emoji, cat_css, filename,
                       related_listings=None, state_cities=None):
    services_map = {
        "HVAC":             ["AC Installation & Replacement", "AC Repair & Emergency Service", "Heating System Service", "Preventive Maintenance Plans", "Indoor Air Quality Solutions", "Duct Cleaning & Sealing"],
        "Legal":            ["Free Initial Consultation", "Civil Litigation", "Family Law", "Criminal Defense", "Personal Injury", "Business Law"],
        "Cleaning":         ["Residential Deep Cleaning", "Regular Maintenance Cleaning", "Move-In / Move-Out Cleaning", "Post-Construction Cleanup", "Office & Commercial Cleaning", "Eco-Friendly Products Available"],
        "Contracting":      ["New Construction", "Home Renovations & Remodels", "Kitchen & Bathroom Upgrades", "Roofing & Siding", "Decks & Outdoor Structures", "Licensed, Bonded & Insured"],
        "Digital Marketing":["Search Engine Optimization (SEO)", "Pay-Per-Click Advertising", "Social Media Management", "Website Design & Development", "Email Marketing Campaigns", "Analytics & Reporting"],
        "Accounting":       ["Bookkeeping & Payroll", "Tax Preparation & Planning", "Business Financial Statements", "QuickBooks Setup & Support", "Audit & Compliance", "CFO Advisory Services"],
        "IT Services":      ["Managed IT Support", "Network Setup & Security", "Cloud Migration", "Help Desk & Remote Support", "Cybersecurity Assessments", "Hardware & Software Procurement"],
        "Pest Control":     ["Residential Pest Inspection", "Commercial Pest Management", "Termite Treatment & Prevention", "Rodent Exclusion", "Bed Bug Treatment", "Ongoing Protection Plans"],
        "Plumbing":         ["Leak Detection & Repair", "Drain Cleaning", "Water Heater Installation", "Pipe Replacement", "Bathroom & Kitchen Plumbing", "Emergency 24/7 Service"],
        "Landscaping":      ["Lawn Mowing & Edging", "Landscape Design", "Tree & Shrub Trimming", "Irrigation System Install", "Seasonal Cleanup", "Mulching & Sodding"],
        "Roofing":          ["Roof Inspection & Repair", "Full Roof Replacement", "Gutter Installation & Cleaning", "Storm Damage Restoration", "Flat & Metal Roofing", "Free Estimates"],
        "Electrical":       ["Panel Upgrades & Repairs", "Outlet & Switch Installation", "Lighting Design", "EV Charger Installation", "Generator Hookup", "Safety Inspections"],
        "Moving":           ["Local & Long-Distance Moves", "Packing & Unpacking", "Furniture Disassembly/Assembly", "Specialty Item Handling", "Short & Long-Term Storage", "Free In-Home Estimates"],
        "Painting":         ["Interior Painting", "Exterior Painting", "Cabinet Painting & Refinishing", "Deck & Fence Staining", "Pressure Washing & Prep", "Color Consultation Included"],
        "Flooring":         ["Hardwood Installation & Refinishing", "Luxury Vinyl Plank (LVP)", "Tile & Stone", "Carpet Installation", "Laminate Flooring", "Subfloor Repair & Prep"],
        "Home Security":    ["Security System Design & Install", "24/7 Professional Monitoring", "Indoor & Outdoor Cameras", "Smart Lock Installation", "Video Doorbell Setup", "Fire & Flood Sensors"],
        "Solar Energy":     ["Residential Solar Panel Install", "Battery Storage Systems", "Federal & State Incentive Filing", "Roof Assessment & Permitting", "Grid Tie-In & Interconnection", "Annual System Monitoring"],
        "Pool & Spa":       ["Weekly Pool Maintenance", "Chemical Balancing", "Equipment Repair & Replacement", "Pool Resurfacing", "Leak Detection", "Seasonal Opening & Closing"],
        "Auto Repair":      ["Oil Change & Fluid Services", "Brake Repair & Replacement", "Engine Diagnostics", "Transmission Service", "AC & Heat Repair", "Tire Rotation & Alignment"],
        "Pet Services":     ["Dog & Cat Grooming", "Overnight Boarding", "Doggy Daycare", "Puppy & Adult Training", "Nail Trims & Ear Cleaning", "Pick-Up & Drop-Off Available"],
        "Personal Training":["Personalized Workout Programs", "Nutrition & Meal Planning", "One-on-One Sessions", "Small Group Training", "Online Coaching", "Fitness Assessments"],
        "Tutoring":         ["Math (K–12 & SAT)", "Reading & Writing", "Science & STEM", "SAT/ACT Test Prep", "Learning Disability Support", "In-Home, Center, or Online"],
        "Mortgage":         ["Home Purchase Loans", "Refinancing", "FHA, VA & USDA Loans", "Jumbo Loans", "Down Payment Assistance", "Pre-Approval in 24 Hours"],
        "Handyman":         ["Drywall Repair & Patching", "Door & Window Installation", "Furniture Assembly", "Caulking & Weatherstripping", "Light Fixture Replacement", "General Home Maintenance"],
    }
    service_items = "\n".join(
        f'        <div class="listing-detail"><span class="di">✅</span> {s}</div>'
        for s in services_map.get(cat_label, ["Professional Services", "Free Estimates", "Licensed & Insured"])
    )

    raw_desc = LONG_DESCS.get(cat_label, f"{biz_name} is a trusted local business serving {city_name}, {state} and surrounding communities.")
    desc_html = raw_desc.replace("{biz}", biz_name).replace("{city}", city_name).replace("{state}", state)
    desc_paragraphs = "\n".join(f"        <p>{p.strip()}</p>" for p in desc_html.split("\n\n") if p.strip())

    # Impact affiliate link — primary CTA on every listing page
    aff_url = IMPACT_AFFILIATES.get(cat_label, IMPACT_FALLBACK)
    page_url = f"{DOMAIN}/{city_slug}/{os.path.splitext(filename)[0]}"
    biz_slug = os.path.splitext(filename)[0]

    # ── FAQ schema + HTML ──────────────────────────────────────────────────
    raw_faqs = FAQS.get(cat_label, [])
    faq_items_ld = []
    faq_html_items = []
    for q_tmpl, a_tmpl in raw_faqs:
        q = q_tmpl.replace("{city}", city_name).replace("{state}", state)
        a = a_tmpl.replace("{city}", city_name).replace("{state}", state)
        faq_items_ld.append(
            f'{{"@type":"Question","name":"{q}","acceptedAnswer":{{"@type":"Answer","text":"{a}"}}}}'
        )
        faq_html_items.append(f"""      <details class="faq-item">
        <summary class="faq-q">{q}</summary>
        <div class="faq-a">{a}</div>
      </details>""")
    faq_schema = ""
    faq_section = ""
    if faq_items_ld:
        faq_schema = f"""  <script type="application/ld+json">
  {{"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{",".join(faq_items_ld)}]}}
  </script>"""
        faq_section = f"""        <br>
        <h2>Frequently Asked Questions</h2>
        <div class="faq-list">
{"".join(faq_html_items)}
        </div>"""

    # ── Related listings (same category, same city) ────────────────────────
    related_html = ""
    if related_listings:
        rel_links = "".join(
            f'<a href="/{city_slug}/{rfname}" class="rel-link">'
            f'<span class="rel-emoji">{cat_emoji}</span> {rbiz}</a>'
            for rbiz, rfname in related_listings[:6]
        )
        related_html = f"""        <br>
        <h2>Other {cat_label} Pros in {city_name}</h2>
        <div class="rel-grid">{rel_links}</div>"""

    # ── Cross-category suggestions ─────────────────────────────────────────
    cross = CROSS_CATS.get(cat_label, [])
    cross_html = ""
    if cross:
        cross_links = "".join(
            f'<a href="/{city_slug}/" class="cross-link">'
            f'<span>{emoji}</span> {label} in {city_name}</a>'
            for label, emoji in cross
        )
        cross_html = f"""        <br>
        <h2>You Might Also Need</h2>
        <div class="rel-grid">{cross_links}</div>"""

    # ── Nearby cities (same state) ─────────────────────────────────────────
    nearby_html = ""
    if state_cities:
        city_links = "".join(
            f'<a href="/{slug}/" class="rel-link">'
            f'<span class="rel-emoji">📍</span> {cat_label} in {name}</a>'
            for slug, name in state_cities[:8] if slug != city_slug
        )
        nearby_html = f"""        <br>
        <h2>{cat_label} Pros in Other {state} Cities</h2>
        <div class="rel-grid">{city_links}</div>"""

    local_biz_ld = jsonld_local_business(biz_name, cat_label, city_name, state, page_url)
    breadcrumb_ld = jsonld_breadcrumb([
        ("Home", DOMAIN),
        (city_name, f"{DOMAIN}/{city_slug}/"),
        (biz_name, page_url),
    ])

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name='impact-site-verification' value='6b714473-0498-4933-83ec-09fb32acd5fa'>
  <title>{biz_name} — {cat_label} in {city_name}, {state} | AllCityPros</title>
  <meta name="description" content="{biz_name} provides professional {cat_label.lower()} services in {city_name}, {state}. Rated 4.8★ by local customers. Get a free quote today.">
  <link rel="canonical" href="{page_url}">
  <meta property="og:title" content="{biz_name} — {cat_label} in {city_name}, {state}">
  <meta property="og:description" content="Professional {cat_label.lower()} services in {city_name}. Rated 4.8★. Free quotes available.">
  <meta property="og:type" content="website">
{local_biz_ld}
{breadcrumb_ld}
{faq_schema}
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/styles.css">
</head>
<body>

<header class="site-header">
  <a href="/" class="logo">AllCity<span>Pros</span></a>
  <button class="nav-toggle" aria-label="Toggle navigation" onclick="this.nextElementSibling.classList.toggle('open')">
    <span></span><span></span><span></span>
  </button>
  <nav class="header-nav">
    <a href="/">Cities</a>
    <a href="#">Categories</a>
    <a href="#">List Your Business</a>
  </nav>
</header>

<nav class="breadcrumb">
  <a href="/">Home</a>
  <span class="sep">›</span>
  <a href="/{city_slug}/">{city_name}</a>
  <span class="sep">›</span>
  <span>{biz_name}</span>
</nav>

<section class="biz-hero {cat_css}">
  <div class="biz-hero-inner">
    <div class="biz-logo">{cat_emoji}</div>
    <div class="biz-meta">
      <div class="biz-tag">{cat_label}</div>
      <h1>{biz_name}</h1>
      <div class="biz-city">📍 {city_name}, {state} — Serving the Greater {city_name} Area</div>
      <div class="rating-badge">⭐ 4.8 / 5 &nbsp;·&nbsp; 47 reviews</div>
    </div>
  </div>
</section>

<!-- Impact affiliate banner -->
<div style="background:linear-gradient(90deg,#1d4ed8,#2563eb);color:#fff;text-align:center;padding:14px 20px;font-size:0.9rem;font-weight:600;">
  🔗 Looking for the best {cat_label} pros in {city_name}?
  <a href="{aff_url}" target="_blank" rel="noopener sponsored"
     style="color:#fde68a;margin-left:10px;text-decoration:underline;font-weight:700;">
    Compare Top-Rated Pros Now →
  </a>
</div>

<div class="biz-content">
  <div class="biz-card">
    <div class="biz-card-grid">
      <div class="biz-info">
        <h2>About {biz_name}</h2>
{desc_paragraphs}

        <br>
        <h2>Services Offered</h2>
        <br>
{service_items}

        <br><br>
        <h2>Get a Free Quote</h2>
        <div class="quote-form">
          <h3>Tell us about your project</h3>
          <form action="https://formspree.io/f/allcitypros" method="POST">
            <input type="hidden" name="business" value="{biz_name}">
            <input type="hidden" name="city" value="{city_name}, {state}">
            <div class="form-row">
              <input type="text" name="name" placeholder="Your name" required>
              <input type="email" name="email" placeholder="Email address" required>
            </div>
            <div class="form-row">
              <input type="tel" name="phone" placeholder="Phone number">
              <select name="service">
                <option value="">Select a service...</option>
                {"".join(f'<option>{s}</option>' for s in services_map.get(cat_label, ["General Service"]))}
              </select>
            </div>
            <div class="form-row full">
              <textarea name="message" placeholder="Describe your project or question..." rows="3"></textarea>
            </div>
            <button type="submit" class="btn-primary" style="border:none;cursor:pointer;padding:12px 24px;font-size:0.9rem;border-radius:8px;">Send Request →</button>
          </form>
        </div>

        <br>
        <h2>Customer Reviews</h2>
        <p style="color:var(--gray-600);font-size:0.9rem;margin-bottom:16px;">⭐ <strong>4.8 / 5</strong> based on 47 local reviews</p>
        <textarea id="review-{biz_slug}" placeholder="Share your experience with {biz_name}..." rows="3" style="width:100%;padding:10px;border:1px solid var(--gray-200);border-radius:8px;font-family:inherit;font-size:0.9rem;resize:vertical;margin-bottom:10px;"></textarea>
        <button type="button" onclick="document.getElementById('review-{biz_slug}').value='';alert('Thank you for your review!')" class="btn-primary" style="display:inline-block;padding:10px 20px;border:none;cursor:pointer;border-radius:8px;">Submit Review</button>

{faq_section}
{related_html}
{cross_html}
{nearby_html}
      </div>

      <div class="biz-sidebar">
        <h2 style="font-size:1rem;font-weight:700;margin-bottom:16px;">Contact &amp; Info</h2>

        <div class="contact-item">
          <span class="ci">📍</span>
          <div>
            <div class="cl">Location</div>
            <div class="cv">{city_name}, {state}</div>
          </div>
        </div>

        <div class="contact-item">
          <span class="ci">🕐</span>
          <div>
            <div class="cl">Hours</div>
            <div class="cv">Mon–Fri: 8am–6pm<br>Sat: 9am–4pm</div>
          </div>
        </div>

        <div class="contact-item">
          <span class="ci">🪪</span>
          <div>
            <div class="cl">Credentials</div>
            <div class="cv">Licensed &amp; Insured<br>Serving {city_name}, {state}</div>
          </div>
        </div>

        <div class="contact-item">
          <span class="ci">⭐</span>
          <div>
            <div class="cl">Rating</div>
            <div class="cv">4.8 / 5 &nbsp;(47 reviews)</div>
          </div>
        </div>

        <br>
        <!-- Impact affiliate CTA buttons -->
        <a href="{aff_url}" target="_blank" rel="noopener sponsored" class="btn-primary"
           style="display:block;text-align:center;padding:13px;border-radius:8px;font-size:0.9rem;font-weight:700;margin-bottom:10px;">
          📋 Request a Free Quote
        </a>
        <a href="{aff_url}" target="_blank" rel="noopener sponsored" class="btn-outline"
           style="display:block;text-align:center;padding:10px;border-radius:8px;font-size:0.85rem;">
          View More {cat_label} Pros →
        </a>

        <div class="claim-banner" style="margin-top:24px;padding:16px;">
          <div class="claim-text">
            <strong>Is this your business?</strong>
            <span>Submit your info and we'll verify and update this listing.</span>
          </div>
          <button type="button" class="claim-btn"
            style="margin-top:12px;cursor:pointer;border:none;width:100%;"
            onclick="this.style.display='none';document.getElementById('claim-form-{biz_slug}').style.display='block';">
            Claim This Listing →
          </button>
          <form id="claim-form-{biz_slug}"
            action="https://formspree.io/f/allcitypros-claim"
            method="POST"
            style="display:none;margin-top:14px;">
            <input type="hidden" name="listing" value="{biz_name}">
            <input type="hidden" name="city" value="{city_name}, {state}">
            <input type="hidden" name="listing_url" value="{page_url}">
            <div style="display:flex;flex-direction:column;gap:8px;">
              <input type="text" name="owner_name" placeholder="Your full name" required
                style="padding:9px 11px;border:1px solid var(--gray-200);border-radius:7px;font-size:0.85rem;font-family:inherit;">
              <input type="email" name="email" placeholder="Business email" required
                style="padding:9px 11px;border:1px solid var(--gray-200);border-radius:7px;font-size:0.85rem;font-family:inherit;">
              <input type="tel" name="phone" placeholder="Business phone"
                style="padding:9px 11px;border:1px solid var(--gray-200);border-radius:7px;font-size:0.85rem;font-family:inherit;">
              <input type="url" name="website" placeholder="Website URL (optional)"
                style="padding:9px 11px;border:1px solid var(--gray-200);border-radius:7px;font-size:0.85rem;font-family:inherit;">
              <input type="text" name="address" placeholder="Business street address"
                style="padding:9px 11px;border:1px solid var(--gray-200);border-radius:7px;font-size:0.85rem;font-family:inherit;">
              <textarea name="notes" placeholder="Anything else we should know?" rows="2"
                style="padding:9px 11px;border:1px solid var(--gray-200);border-radius:7px;font-size:0.85rem;font-family:inherit;resize:vertical;"></textarea>
              <button type="submit" class="btn-primary"
                style="border:none;cursor:pointer;padding:10px;font-size:0.85rem;border-radius:7px;font-weight:700;">
                Submit for Review →
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</div>

<footer class="site-footer">
  <div class="footer-logo">AllCity<span>Pros</span></div>
  <p>Connecting people with trusted local professionals across America.</p>
  <p class="mt-4"><a href="#">Privacy Policy</a> &nbsp;·&nbsp; <a href="#">Terms of Service</a> &nbsp;·&nbsp; <a href="mailto:hello@allcitypros.com?subject=List My Business">List Your Business</a></p>
</footer>

</body>
</html>
"""


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    all_urls = [DOMAIN + "/"]
    total_cities = 0
    total_businesses = 0

    # Pre-build state → [(slug, city_name)] map for internal linking
    state_city_map = {}
    for slug, (name, st, _) in CITY_META.items():
        state_city_map.setdefault(st, []).append((slug, name))

    for city_slug, (city_name, state, emoji) in CITY_META.items():
        city_dir = os.path.join(root, city_slug)
        os.makedirs(city_dir, exist_ok=True)

        # ── Step 1: discover real named files (not index.html, not numbered slugs) ──
        existing = sorted([
            f for f in os.listdir(city_dir)
            if f.endswith('.html') and f != 'index.html'
        ])
        # Identify numbered generic files (e.g. tampa_hvac_3.html)
        numbered_pattern = re.compile(rf'^{re.escape(city_slug)}_[a-z_]+_\d+\.html$')
        named_files = [f for f in existing if not numbered_pattern.match(f)]

        # ── Step 2: count how many named files exist per category ──
        named_per_cat = {slug: 0 for slug in CATEGORY_SLUGS}
        for f in named_files:
            cat_label, _, _ = detect_category(f)
            for slug, meta in CATEGORY_MAP.items():
                if meta["label"] == cat_label:
                    named_per_cat[slug] += 1
                    break

        # ── Step 3: ensure LISTINGS_PER_CAT numbered files per category ──
        for cat_slug in CATEGORY_SLUGS:
            cat_meta = CATEGORY_MAP[cat_slug]
            named_count = named_per_cat[cat_slug]
            needed = max(0, LISTINGS_PER_CAT - named_count)
            for n in range(1, needed + 1):
                fname = f"{city_slug}_{cat_slug}_{n}.html"
                fpath = os.path.join(city_dir, fname)
                if not os.path.exists(fpath):
                    # Create a stub so extract_business_name works on first pass
                    with open(fpath, 'w') as fp:
                        fp.write("")

        # ── Step 4: collect all files and regenerate ──
        all_files = sorted([
            f for f in os.listdir(city_dir)
            if f.endswith('.html') and f != 'index.html'
        ])

        # Collect full listing metadata (including cat_css)
        full_listings = []  # (biz_name, cat_label, cat_emoji, cat_css, fname)
        for fname in all_files:
            fpath = os.path.join(city_dir, fname)
            biz_name = generate_biz_name(fpath, city_name) if not os.path.getsize(fpath) else extract_business_name(fpath, city_name)
            cat_label, cat_emoji, cat_css = detect_category(fname)
            full_listings.append((biz_name, cat_label, cat_emoji, cat_css, fname))

        # listings for city index (without cat_css)
        listings = [(b, c, e, f) for b, c, e, cs, f in full_listings]

        # Category bucket for related-listing internal links
        cat_bucket = {}
        for biz_name, cat_label, cat_emoji, cat_css, fname in full_listings:
            cat_bucket.setdefault(cat_label, []).append((biz_name, fname))

        nearby_cities = state_city_map.get(state, [])

        for biz_name, cat_label, cat_emoji, cat_css, fname in full_listings:
            fpath = os.path.join(city_dir, fname)
            related = [(b, f) for b, f in cat_bucket.get(cat_label, []) if f != fname][:6]

            page_html = business_page_html(
                city_slug, city_name, state, biz_name, cat_label, cat_emoji, cat_css, fname,
                related_listings=related,
                state_cities=nearby_cities,
            )
            with open(fpath, 'w') as fp:
                fp.write(page_html)
            all_urls.append(f"{DOMAIN}/{city_slug}/{os.path.splitext(fname)[0]}")
            total_businesses += 1

        # ── Step 5: write city index ──
        idx_path = os.path.join(city_dir, 'index.html')
        with open(idx_path, 'w') as fp:
            fp.write(city_index_html(city_slug, city_name, state, emoji, listings,
                                     state_cities=nearby_cities))
        all_urls.append(f"{DOMAIN}/{city_slug}/")
        total_cities += 1
        print(f"  ✓ {city_name} — {len(listings)} listings")

    # ── Sitemap ──
    sitemap_path = os.path.join(root, 'sitemap.xml')
    with open(sitemap_path, 'w') as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
        for url in all_urls:
            f.write(f'  <url><loc>{url}</loc><changefreq>monthly</changefreq><priority>0.8</priority></url>\n')
        f.write('</urlset>\n')
    print(f"\nSitemap: {len(all_urls)} URLs → sitemap.xml")

    # ── robots.txt ──
    robots_path = os.path.join(root, 'robots.txt')
    with open(robots_path, 'w') as f:
        f.write("User-agent: *\nAllow: /\nSitemap: https://allcitypros.com/sitemap.xml\n")
    print("robots.txt written")

    print(f"Done: {total_cities} city pages, {total_businesses} business pages")

if __name__ == '__main__':
    main()
