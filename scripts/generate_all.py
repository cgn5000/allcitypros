"""
Generate styled index pages for every city and styled detail pages for every business.
Run from the repo root: python3 scripts/generate_all.py
"""

import os
import re

CATEGORY_MAP = {
    "hvac":         {"label": "HVAC",             "emoji": "❄️", "keywords": ["hvac", "cooling", "heating", "climate", "comfort", "air"]},
    "legal":        {"label": "Legal",             "emoji": "⚖️", "keywords": ["legal", "law", "justice", "attorney"]},
    "cleaning":     {"label": "Cleaning",          "emoji": "🧹", "keywords": ["clean", "sparkle", "elite_clean", "shine", "maid", "residential_cleaning"]},
    "contracting":  {"label": "Contracting",       "emoji": "🔨", "keywords": ["contracting", "builders", "construction", "build", "general_contracting"]},
    "marketing":    {"label": "Digital Marketing", "emoji": "📈", "keywords": ["digital", "marketing", "growth", "agency", "seo"]},
    "accounting":   {"label": "Accounting",        "emoji": "📊", "keywords": ["accounting", "bookkeeping", "cpa", "tax", "finance"]},
    "it_services":  {"label": "IT Services",       "emoji": "💻", "keywords": ["it_services", "it_support", "tech", "computer", "network", "managed_it"]},
    "pest_control": {"label": "Pest Control",      "emoji": "🐛", "keywords": ["pest", "exterminator", "termite", "bug", "rodent"]},
    "plumbing":     {"label": "Plumbing",          "emoji": "🔧", "keywords": ["plumbing", "plumber", "drain", "pipe"]},
    "landscaping":  {"label": "Landscaping",       "emoji": "🌿", "keywords": ["landscaping", "lawn", "garden", "yard", "landscape"]},
    "roofing":      {"label": "Roofing",           "emoji": "🏠", "keywords": ["roofing", "roof", "gutter", "shingle"]},
    "electrical":   {"label": "Electrical",        "emoji": "⚡", "keywords": ["electrical", "electrician", "wiring", "electric"]},
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

def detect_category(filename):
    fn = filename.lower()
    for key, meta in CATEGORY_MAP.items():
        for kw in meta["keywords"]:
            if kw in fn:
                return meta["label"], meta["emoji"]
    return "Local Business", "🏢"

def generate_biz_name(filename, city_name):
    fn = os.path.splitext(os.path.basename(filename))[0].lower()
    # match longest key first to avoid "it" matching "digital"
    for cat_key in sorted(CITY_BIZ_NAMES.keys(), key=len, reverse=True):
        if cat_key in fn:
            templates = CITY_BIZ_NAMES[cat_key]
            idx = len(city_name) % len(templates)
            return templates[idx].replace("{city}", city_name)
    return city_name + " Professionals"

def extract_business_name(filename, city_name):
    try:
        with open(filename) as f:
            content = f.read()
        m = re.search(r'<h1[^>]*>([^<]+)</h1>', content, re.IGNORECASE)
        if m:
            raw = m.group(1).strip()
            # strip leading "CityName - "
            raw = re.sub(r'^[^-]+-\s*', '', raw).strip()
            # reject slugs and generic fallbacks
            if re.search(r'_(hvac|legal|cleaning|contracting|marketing|accounting|it|pest|plumbing|landscaping|roofing|electrical)', raw, re.I):
                return generate_biz_name(filename, city_name)
            if raw.endswith('Professionals'):
                return generate_biz_name(filename, city_name)
            if raw and '_' not in raw and len(raw) > 3:
                return raw
    except Exception:
        pass
    return generate_biz_name(filename, city_name)

def affiliate_slug(filename):
    return os.path.splitext(os.path.basename(filename))[0]

def city_index_html(city_slug, city_name, state, emoji, listings):
    cards = ""
    for biz_name, cat_label, cat_emoji, fname in listings:
        cards += f"""
    <a href="/{city_slug}/{fname}" class="listing-card">
      <div class="listing-card-header">
        <div class="listing-avatar">{cat_emoji}</div>
        <div><div class="name">{biz_name}</div><div class="category-tag">{cat_label}</div></div>
      </div>
      <div class="listing-card-body">
        <div class="listing-detail"><span class="di">📍</span> {city_name}, {state}</div>
      </div>
      <div class="listing-card-actions">
        <div class="btn-primary">View Details</div>
      </div>
    </a>"""

    count = len(listings)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name='impact-site-verification' value='6b714473-0498-4933-83ec-09fb32acd5fa'>
  <title>{city_name} Local Professionals — AllCityPros</title>
  <meta name="description" content="Find top-rated local professionals in {city_name}, {state}. HVAC, legal services, cleaning, contracting, and digital marketing.">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/styles.css">
</head>
<body>

<header class="site-header">
  <a href="/" class="logo">AllCity<span>Pros</span></a>
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
</div>

<div class="section">
  <h2 class="section-title">{city_name} Professionals</h2>
  <p class="section-sub">{count} businesses listed in {city_name}</p>
  <div class="listing-grid">
{cards}
  </div>
</div>

<footer class="site-footer">
  <div class="footer-logo">AllCity<span>Pros</span></div>
  <p>Connecting people with trusted local professionals across America.</p>
  <p class="mt-4"><a href="#">Privacy Policy</a> &nbsp;·&nbsp; <a href="#">Terms of Service</a> &nbsp;·&nbsp; <a href="#">List Your Business</a></p>
</footer>

</body>
</html>
"""

def business_page_html(city_slug, city_name, state, biz_name, cat_label, cat_emoji, aff_slug):
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
    desc_map = {
        "HVAC":             f"{biz_name} provides expert heating, cooling, and air quality services throughout {city_name}. Our certified technicians deliver reliable, same-day service you can count on year-round. We service all major brands and specialize in efficient, lasting solutions for homes and businesses.",
        "Legal":            f"{biz_name} is a trusted law firm serving clients throughout {city_name} and {state}. Our experienced attorneys provide strategic, client-centered representation across a wide range of practice areas. We offer free consultations and work on contingency for eligible cases.",
        "Cleaning":         f"{biz_name} delivers professional residential and commercial cleaning services throughout {city_name}. Our background-checked, insured cleaning teams use proven methods and eco-friendly products to leave every space spotless. Flexible scheduling — book online in minutes.",
        "Contracting":      f"{biz_name} is {city_name}'s trusted general contractor for new builds, renovations, and specialty projects. Our licensed team delivers quality craftsmanship on time and on budget. From small remodels to full construction, we handle it all.",
        "Digital Marketing":f"{biz_name} helps {city_name} businesses grow online through data-driven digital marketing strategies. Our team specializes in SEO, paid advertising, and social media — delivering measurable results that turn clicks into customers.",
        "Accounting":       f"{biz_name} provides reliable accounting and bookkeeping services for individuals and businesses throughout {city_name}. From tax preparation to financial planning, our licensed CPAs help you stay organized, compliant, and profitable.",
        "IT Services":      f"{biz_name} delivers managed IT support and technology solutions to businesses in {city_name}. From network security to cloud migrations, our certified technicians keep your systems running smoothly so you can focus on growing.",
        "Pest Control":     f"{biz_name} provides fast, effective pest elimination for homes and businesses throughout {city_name}. Our licensed exterminators use safe, targeted treatments to remove pests and keep them out for good.",
        "Plumbing":         f"{biz_name} is {city_name}'s trusted plumbing service for repairs, installations, and emergencies. Our licensed plumbers are available around the clock, delivering fast, lasting fixes at fair prices.",
        "Landscaping":      f"{biz_name} transforms yards and commercial properties throughout {city_name} with professional lawn care, landscape design, and seasonal maintenance. Let us handle the outdoors so you don't have to.",
        "Roofing":          f"{biz_name} provides expert roofing installation, repair, and inspection services throughout {city_name}. Our licensed roofing contractors use quality materials and back all work with a satisfaction guarantee.",
        "Electrical":       f"{biz_name} is {city_name}'s trusted electrical contractor for residential and commercial projects. Our licensed electricians handle everything from panel upgrades to EV charger installation — safely and up to code.",
    }
    services = services_map.get(cat_label, ["Professional Services", "Free Estimates", "Licensed & Insured"])
    desc = desc_map.get(cat_label, f"{biz_name} is a trusted local business serving {city_name}, {state} and surrounding communities.")
    service_items = "\n".join(f'        <div class="listing-detail"><span class="di">✅</span> {s}</div>' for s in services)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name='impact-site-verification' value='6b714473-0498-4933-83ec-09fb32acd5fa'>
  <title>{biz_name} — {city_name}, {state} | AllCityPros</title>
  <meta name="description" content="{biz_name} provides professional {cat_label.lower()} services in {city_name}, {state}. Contact us today for a free estimate.">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/styles.css">
</head>
<body>

<header class="site-header">
  <a href="/" class="logo">AllCity<span>Pros</span></a>
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

<section class="biz-hero">
  <div class="biz-hero-inner">
    <div class="biz-logo">{cat_emoji}</div>
    <div class="biz-meta">
      <div class="biz-tag">{cat_label}</div>
      <h1>{biz_name}</h1>
      <div class="biz-city">📍 {city_name}, {state} — Serving the Greater {city_name} Area</div>
    </div>
  </div>
</section>

<div class="biz-content">
  <div class="biz-card">
    <div class="biz-card-grid">
      <div class="biz-info">
        <h2>About This Business</h2>
        <p>{desc}</p>
        <br>
        <h2>Services Offered</h2>
        <br>
{service_items}

        <br><br>
        <h2>Customer Reviews</h2>
        <p style="color:var(--gray-600);font-size:0.9rem;margin-bottom:16px;">⭐ <strong>4.8/5</strong> based on local sentiment</p>
        <textarea id="review" placeholder="Write a review for {biz_name}..." rows="3" style="width:100%;padding:10px;border:1px solid var(--gray-200);border-radius:8px;font-family:inherit;font-size:0.9rem;resize:vertical;margin-bottom:10px;"></textarea>
        <button type="button" onclick="alert('Thank you for your review!')" class="btn-primary" style="display:inline-block;padding:10px 20px;border:none;cursor:pointer;">Submit Review</button>
      </div>

      <div class="biz-sidebar">
        <h2 style="font-size:1rem;font-weight:700;margin-bottom:16px;">Contact Information</h2>

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
            <div class="cv">Licensed &amp; Insured<br>Serving {city_name}</div>
          </div>
        </div>

        <br>
        <a href="http://affiliate.link/{aff_slug}" class="btn-primary" style="display:block;text-align:center;padding:12px;border-radius:8px;font-size:0.9rem;font-weight:700;margin-bottom:10px;">
          📞 Request a Quote
        </a>
        <a href="http://affiliate.link/{aff_slug}" class="btn-outline" style="display:block;text-align:center;padding:10px;border-radius:8px;font-size:0.85rem;">
          Learn More
        </a>
      </div>
    </div>
  </div>
</div>

<footer class="site-footer">
  <div class="footer-logo">AllCity<span>Pros</span></div>
  <p>Connecting people with trusted local professionals across America.</p>
  <p class="mt-4"><a href="#">Privacy Policy</a> &nbsp;·&nbsp; <a href="#">Terms of Service</a> &nbsp;·&nbsp; <a href="#">List Your Business</a></p>
</footer>

</body>
</html>
"""

def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    total_cities = 0
    total_businesses = 0

    for city_slug, (city_name, state, emoji) in CITY_META.items():
        city_dir = os.path.join(root, city_slug)
        if not os.path.isdir(city_dir):
            print(f"  SKIP {city_slug} (no dir)")
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
            cat_label, cat_emoji = detect_category(fname)
            listings.append((biz_name, cat_label, cat_emoji, fname))

            page_html = business_page_html(city_slug, city_name, state, biz_name, cat_label, cat_emoji, affiliate_slug(fname))
            with open(fpath, 'w') as f:
                f.write(page_html)
            total_businesses += 1

        idx_path = os.path.join(city_dir, 'index.html')
        with open(idx_path, 'w') as f:
            f.write(city_index_html(city_slug, city_name, state, emoji, listings))
        total_cities += 1
        print(f"  ✓ {city_name} — {len(listings)} listings")

    print(f"\nDone: {total_cities} city pages, {total_businesses} business pages")

if __name__ == '__main__':
    main()
