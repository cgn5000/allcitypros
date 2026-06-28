"""
Generate styled index pages for every city and styled detail pages for every business.
Run from the repo root: python3 scripts/generate_all.py
"""

import os
import re

DOMAIN = "https://allcitypros.com"

CATEGORY_MAP = {
    # Order matters: more specific keywords checked before short/ambiguous ones
    "it_services":  {"label": "IT Services",       "emoji": "💻",  "css": "cat-it",          "keywords": ["it_services", "it_support", "managed_it", "computer", "network", "tech_support"]},
    "pest_control": {"label": "Pest Control",      "emoji": "🐛",  "css": "cat-pest",        "keywords": ["pest_control", "pest", "exterminator", "termite", "rodent"]},
    "general_contracting": {"label": "Contracting","emoji": "🔨",  "css": "cat-contracting", "keywords": ["general_contracting", "contracting", "builders", "construction", "build"]},
    "digital_marketing":   {"label": "Digital Marketing","emoji": "📈","css": "cat-marketing","keywords": ["digital_marketing", "digital", "marketing", "growth", "agency", "seo"]},
    "residential_cleaning":{"label": "Cleaning",   "emoji": "🧹",  "css": "cat-cleaning",    "keywords": ["residential_cleaning", "elite_clean", "sparkle", "cleaning"]},
    "hvac":         {"label": "HVAC",             "emoji": "❄️",  "css": "cat-hvac",        "keywords": ["hvac", "cooling", "heating", "climate", "comfort_systems"]},
    "legal":        {"label": "Legal",             "emoji": "⚖️",  "css": "cat-legal",       "keywords": ["legal", "law", "justice", "attorney"]},
    "accounting":   {"label": "Accounting",        "emoji": "📊",  "css": "cat-accounting",  "keywords": ["accounting", "bookkeeping", "cpa", "tax", "finance"]},
    "plumbing":     {"label": "Plumbing",          "emoji": "🔧",  "css": "cat-plumbing",    "keywords": ["plumbing", "plumber", "drain", "pipe"]},
    "landscaping":  {"label": "Landscaping",       "emoji": "🌿",  "css": "cat-landscaping", "keywords": ["landscaping", "lawn", "garden", "yard"]},
    "roofing":      {"label": "Roofing",           "emoji": "🏠",  "css": "cat-roofing",     "keywords": ["roofing", "roof", "gutter", "shingle"]},
    "electrical":   {"label": "Electrical",        "emoji": "⚡",  "css": "cat-electrical",  "keywords": ["electrical", "electrician", "wiring"]},
}

# Affiliate base URLs by category — swap these for real program links
AFFILIATE_BASES = {
    "HVAC":             "https://www.homeadvisor.com/c.HVAC.html?ref=allcitypros",
    "Legal":            "https://www.avvo.com/?ref=allcitypros",
    "Cleaning":         "https://www.homeadvisor.com/c.House-Cleaning.html?ref=allcitypros",
    "Contracting":      "https://www.homeadvisor.com/c.General-Contractors.html?ref=allcitypros",
    "Digital Marketing":"https://www.clutch.co/agencies/digital-marketing?ref=allcitypros",
    "Accounting":       "https://www.thumbtack.com/k/accountant/near-me/?ref=allcitypros",
    "IT Services":      "https://www.clutch.co/it-services?ref=allcitypros",
    "Pest Control":     "https://www.homeadvisor.com/c.Pest-Control.html?ref=allcitypros",
    "Plumbing":         "https://www.homeadvisor.com/c.Plumbing.html?ref=allcitypros",
    "Landscaping":      "https://www.homeadvisor.com/c.Lawn-Care.html?ref=allcitypros",
    "Roofing":          "https://www.homeadvisor.com/c.Roofing.html?ref=allcitypros",
    "Electrical":       "https://www.homeadvisor.com/c.Electricians.html?ref=allcitypros",
}

CITY_BIZ_NAMES = {
    "hvac":                 ["{city} Climate Control", "{city} Air Experts", "{city} Comfort Systems", "Premier HVAC {city}", "{city} Heating & Cooling"],
    "legal":                ["{city} Law Group", "{city} Legal Partners", "The {city} Attorneys", "{city} Justice Law", "Premier Legal {city}"],
    "residential_cleaning": ["Sparkle {city} Cleaning", "{city} Elite Clean", "Fresh Start {city}", "{city} Shine Services", "Pro Clean {city}"],
    "cleaning":             ["Sparkle {city} Cleaning", "{city} Elite Clean", "Fresh Start {city}", "{city} Shine Services", "Pro Clean {city}"],
    "general_contracting":  ["{city} Prime Contracting", "{city} Builders", "Metro Contractors {city}", "{city} Construction Group", "Premier Build {city}"],
    "contracting":          ["{city} Prime Contracting", "{city} Builders", "Metro Contractors {city}", "{city} Construction Group", "Premier Build {city}"],
    "digital_marketing":    ["{city} Growth Agency", "{city} Digital Co.", "Metro Marketing {city}", "{city} SEO Pros", "Elevate Digital {city}"],
    "marketing":            ["{city} Growth Agency", "{city} Digital Co.", "Metro Marketing {city}", "{city} SEO Pros", "Elevate Digital {city}"],
    "accounting":           ["{city} Accounting Group", "{city} CPA Partners", "Premier Books {city}", "{city} Tax Pros", "Clarity Accounting {city}"],
    "it_services":          ["{city} Tech Solutions", "{city} IT Pros", "Premier IT {city}", "{city} Managed Tech", "NetSure {city}"],
    "it":                   ["{city} Tech Solutions", "{city} IT Pros", "Premier IT {city}", "{city} Managed Tech", "NetSure {city}"],
    "pest":                 ["Shield Pest {city}", "{city} Pest Pros", "Premier Pest {city}", "Bug Guard {city}", "{city} Exterminators"],
    "pest_control":         ["Shield Pest {city}", "{city} Pest Pros", "Premier Pest {city}", "Bug Guard {city}", "{city} Exterminators"],
    "plumbing":             ["{city} Plumbing Pros", "Premier Plumbers {city}", "FlowFix {city}", "{city} Drain Masters", "Quick Plumb {city}"],
    "landscaping":          ["{city} Lawn & Land", "Green Thumb {city}", "Premier Landscapes {city}", "{city} Yard Pros", "Bloom {city}"],
    "roofing":              ["{city} Roofing Pros", "Peak Roofing {city}", "Premier Roof {city}", "SkyShield {city}", "{city} Roof Masters"],
    "electrical":           ["{city} Electric Co.", "Premier Electric {city}", "Volt Pros {city}", "{city} Electricians", "PowerUp {city}"],
}

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
}

# Rich descriptions by category — ~200 words each, unique per city via template
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
}

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
    "Local Business":   ["Free Estimates", "Local Service", "Top Rated"],
}

# Rating variety so cards don't all show identical scores
CARD_RATINGS = ["4.7", "4.8", "4.9", "4.8", "5.0", "4.6", "4.8", "4.9", "4.7", "4.8"]
CARD_REVIEWS = [23, 47, 31, 62, 18, 54, 39, 28, 71, 45]

def detect_category(filename):
    fn = os.path.splitext(os.path.basename(filename))[0].lower()
    # Split into segments so "digital" doesn't match inside "residential"
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

def city_index_html(city_slug, city_name, state, emoji, listings):
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
    <a href="mailto:hello@allcitypros.com?subject=List My Business — {city_name}" class="claim-btn">Claim Your Listing →</a>
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

def business_page_html(city_slug, city_name, state, biz_name, cat_label, cat_emoji, cat_css, filename):
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
    }
    service_items = "\n".join(
        f'        <div class="listing-detail"><span class="di">✅</span> {s}</div>'
        for s in services_map.get(cat_label, ["Professional Services", "Free Estimates", "Licensed & Insured"])
    )

    raw_desc = LONG_DESCS.get(cat_label, f"{biz_name} is a trusted local business serving {city_name}, {state} and surrounding communities.")
    desc_html = raw_desc.replace("{biz}", biz_name).replace("{city}", city_name).replace("{state}", state)
    desc_paragraphs = "\n".join(f"        <p>{p.strip()}</p>" for p in desc_html.split("\n\n") if p.strip())

    aff_url = AFFILIATE_BASES.get(cat_label, "https://www.homeadvisor.com/?ref=allcitypros")
    page_url = f"{DOMAIN}/{city_slug}/{os.path.splitext(filename)[0]}"
    biz_slug = os.path.splitext(filename)[0]

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
        <a href="{aff_url}" target="_blank" rel="noopener sponsored" class="btn-primary" style="display:block;text-align:center;padding:13px;border-radius:8px;font-size:0.9rem;font-weight:700;margin-bottom:10px;">
          📋 Request a Free Quote
        </a>
        <a href="{aff_url}" target="_blank" rel="noopener sponsored" class="btn-outline" style="display:block;text-align:center;padding:10px;border-radius:8px;font-size:0.85rem;">
          View More {cat_label} Pros →
        </a>

        <div class="claim-banner" style="margin-top:24px;padding:16px;">
          <div class="claim-text">
            <strong>Is this your business?</strong>
            <span>Claim this listing to update info and respond to reviews.</span>
          </div>
          <a href="mailto:hello@allcitypros.com?subject=Claim Listing — {biz_name}" class="claim-btn" style="margin-top:12px;">Claim Listing</a>
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

def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    all_urls = [DOMAIN + "/"]
    total_cities = 0
    total_businesses = 0

    for city_slug, (city_name, state, emoji) in CITY_META.items():
        city_dir = os.path.join(root, city_slug)
        if not os.path.isdir(city_dir):
            continue

        html_files = sorted([
            f for f in os.listdir(city_dir)
            if f.endswith('.html') and f != 'index.html'
        ])
        if not html_files:
            continue

        listings = []
        for fname in html_files:
            fpath = os.path.join(city_dir, fname)
            biz_name = extract_business_name(fpath, city_name)
            cat_label, cat_emoji, cat_css = detect_category(fname)
            listings.append((biz_name, cat_label, cat_emoji, fname))

            page_html = business_page_html(city_slug, city_name, state, biz_name, cat_label, cat_emoji, cat_css, fname)
            with open(fpath, 'w') as f:
                f.write(page_html)
            all_urls.append(f"{DOMAIN}/{city_slug}/{os.path.splitext(fname)[0]}")
            total_businesses += 1

        idx_path = os.path.join(city_dir, 'index.html')
        with open(idx_path, 'w') as f:
            f.write(city_index_html(city_slug, city_name, state, emoji, listings))
        all_urls.append(f"{DOMAIN}/{city_slug}/")
        total_cities += 1
        print(f"  ✓ {city_name} — {len(listings)} listings")

    # Write sitemap.xml
    sitemap_path = os.path.join(root, 'sitemap.xml')
    with open(sitemap_path, 'w') as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
        for url in all_urls:
            f.write(f'  <url><loc>{url}</loc><changefreq>monthly</changefreq><priority>0.8</priority></url>\n')
        f.write('</urlset>\n')
    print(f"\nSitemap: {len(all_urls)} URLs → sitemap.xml")

    # Write robots.txt
    robots_path = os.path.join(root, 'robots.txt')
    with open(robots_path, 'w') as f:
        f.write("User-agent: *\nAllow: /\nSitemap: https://allcitypros.com/sitemap.xml\n")
    print("robots.txt written")

    print(f"Done: {total_cities} city pages, {total_businesses} business pages")

if __name__ == '__main__':
    main()
