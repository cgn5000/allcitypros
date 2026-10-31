"""Generate city x service guide pages, category hubs, city hubs and the sitemap.

Run from the repo root:  python3 scripts/generate_guides.py

Outputs
  guides/<city>-<service>.html   (155 cities x 24 services)
  guides/<service>.html          (24 category hubs, one per service)
  guides/index.html              (all guides)
  <city>/index.html              (city hub; the old listings page is kept as <city>/listings.html, noindex)
  sitemap.xml                    (sitemap index; child files written by scripts/build_sitemap.py)

Monetization hooks are config-driven and render nothing until configured:
  scripts/monetization.json -> {"cta": {"hvac": {"url": "...", "label": "...", "partner": "..."}}, "formspree_id": "xxxx"}
"""
import ast, datetime, html, json, os, re, sys

sys.path.insert(0, os.path.dirname(__file__))
from guide_data import CATS, CLIMATE, REGION, REGION_LABEL, STATE_NAMES, local_note  # noqa: E402
from ga4 import GA4_SNIPPET  # noqa: E402
from build_sitemap import build as build_sitemap  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOMAIN = "https://allcitypros.com"
TODAY = os.environ.get("GUIDE_DATE", "2026-10-17")
MONTH_YEAR = datetime.date.fromisoformat(TODAY).strftime("%B %Y")

# Largest metros first; their guides go in the first sitemap wave (grow the wave as pages get indexed).
WAVE1 = ("newyork losangeles chicago houston phoenix philadelphia sanantonio sandiego dallas sanjose austin jacksonville "
         "fortworth columbus charlotte sanfrancisco indianapolis seattle denver washington boston elpaso nashville detroit "
         "oklahomacity portland lasvegas louisville baltimore milwaukee albuquerque tucson fresno sacramento atlanta "
         "kansascity miami raleigh omaha minneapolis tampa orlando").split()
# Used for the "popular cities" link lists only. The sitemap no longer has waves: the service
# hubs are the indexable set, so there is nothing left to ration.
WAVE1_N = int(os.environ.get("WAVE1_N", "25"))

CAT_EMOJI = {"hvac":"❄️","plumbing":"🔧","electrical":"⚡","roofing":"🏠","general_contracting":"🔨","landscaping":"🌿","painting":"🎨",
 "flooring":"🪵","pool_spa":"🏊","pest_control":"🐛","residential_cleaning":"🧹","handyman":"🛠️","moving":"🚛","home_security":"🔒",
 "solar_energy":"☀️","auto_repair":"🚗","pet_services":"🐾","personal_training":"💪","tutoring":"📚","accounting":"📊","legal":"⚖️",
 "mortgage":"🏡","digital_marketing":"📈","it_services":"💻"}

EMOJI = {}

def load_cities():
    tree = ast.parse(open(os.path.join(ROOT, "scripts/generate_all.py")).read())
    for n in tree.body:
        if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", "") == "CITY_META":
            meta = ast.literal_eval(n.value)
            EMOJI.update({k: v[2] for k, v in meta.items()})
            return {k: (v[0], v[1]) for k, v in meta.items()}
    raise SystemExit("CITY_META not found")

CITIES = load_cities()
CFG = {}
cfg_path = os.path.join(ROOT, "scripts/monetization.json")
if os.path.exists(cfg_path):
    CFG = json.load(open(cfg_path))

def lc(label):
    return label if label.isupper() or label.split()[0].isupper() else label.lower()

def esc(s): return html.escape(s, quote=True)
def slug(cat): return cat.replace("_", "-")
def gpath(city, cat): return f"/guides/{city}-{slug(cat)}"

# GA4_SNIPPET is concatenated with braces doubled so HEAD.format() leaves the
# inline script intact (the script itself contains `{` / `}`).
HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
""" + GA4_SNIPPET.replace("{", "{{").replace("}", "}}") + """  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name='impact-site-verification' value='6b714473-0498-4933-83ec-09fb32acd5fa'>
  <title>{title}</title>
  <meta name="description" content="{desc}">
  <link rel="canonical" href="{canon}">
{robots}  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{desc}">
  <meta property="og:type" content="article">
{ld}
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/styles.css">
  <link rel="stylesheet" href="/guides.css">
</head>
<body>
<header class="site-header">
  <a href="/" class="logo">AllCity<span>Pros</span></a>
  <button class="nav-toggle" aria-label="Toggle navigation" onclick="this.nextElementSibling.classList.toggle('open')"><span></span><span></span><span></span></button>
  <nav class="header-nav">
    <a href="/">Cities</a>
    <a href="/guides">Guides</a>
    <a href="/#list-business">List Your Business</a>
  </nav>
</header>
"""
FOOT = """
<footer class="site-footer">
  <div class="footer-logo">AllCity<span>Pros</span></div>
  <p>Independent local service guides for homeowners and small businesses.</p>
  <p class="mt-4"><a href="/guides">All guides</a> &nbsp;·&nbsp; <a href="/privacy-policy">Privacy Policy</a> &nbsp;·&nbsp; <a href="/terms-of-service">Terms of Service</a> &nbsp;·&nbsp; <a href="mailto:hello@allcitypros.com?subject=Guide%20feedback">Send feedback</a></p>
</footer>
</body>
</html>
"""

def crumbs_ld(items):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": DOMAIN + u} for i, (n, u) in enumerate(items)]}

def ld_block(*objs):
    return "\n".join('  <script type="application/ld+json">' + json.dumps(o, ensure_ascii=False) + "</script>" for o in objs)

def breadcrumb_html(items):
    out = []
    for i, (n, u) in enumerate(items):
        out.append(f'<a href="{u}">{esc(n)}</a>' if i < len(items) - 1 else f"<span>{esc(n)}</span>")
    return '<nav class="breadcrumb">' + '<span class="sep">›</span>'.join(out) + "</nav>"

def cta_html(cat, city_name):
    c = CFG.get("cta", {}).get(cat)
    if not c or not c.get("url"):
        return ""
    return (f'<div class="g-cta"><strong>{esc(c.get("headline", "Compare quotes from vetted local pros"))}</strong>'
            f'<p>{esc(c.get("blurb", f"Request free estimates for {city_name}."))}</p>'
            f'<a class="btn-primary" href="{esc(c["url"])}" target="_blank" rel="noopener sponsored">{esc(c.get("label", "Get free quotes"))} →</a>'
            f'<small>Sponsored link{": " + esc(c["partner"]) if c.get("partner") else ""}. We may earn a commission at no cost to you.</small></div>')

def guide_page(city, cat):
    name, st = CITIES[city]
    d = CATS[cat]
    state = STATE_NAMES[st]
    region = REGION.get(st, "mixed")
    label = d["label"]
    fmt = dict(city=name, state=state, st=st)
    title = f"{label} in {name}, {st}: Costs, How to Hire & Questions to Ask"
    desc = (f"Plain-English {lc(label)} guide for {name}, {state}: typical costs, how to compare {d['noun']}s, "
            f"license checks, red flags and FAQs. Updated {MONTH_YEAR}.")
    url = f"{DOMAIN}{gpath(city, cat)}"
    note = CLIMATE.get(cat, {}).get(region) or ""
    note = note.format(**fmt) if note else local_note(cat, name, st)
    snap = (f"{name} is in {state}, which generally has {REGION_LABEL[region]}. "
            f"That shapes what {lc(label)} work looks like locally and when it is best to schedule it.")
    faq = [(q.format(**fmt), a.format(**fmt)) for q, a in d["faq"]]
    ld = ld_block(
        {"@context": "https://schema.org", "@type": "Article", "headline": title, "description": desc, "dateModified": TODAY,
         "datePublished": TODAY, "mainEntityOfPage": url, "author": {"@type": "Organization", "name": "AllCityPros"},
         "publisher": {"@type": "Organization", "name": "AllCityPros", "url": DOMAIN}},
        crumbs_ld([("Home", "/"), ("Guides", "/guides"), (label, f"/guides/{slug(cat)}"), (f"{name}, {st}", gpath(city, cat))]))
    rows = "".join(f"<tr><td>{esc(a)}</td><td>{esc(b)}</td></tr>" for a, b in d["cost"])
    steps = "".join(f"<li>{esc(s.format(**fmt))}</li>" for s in d["steps"])
    qs = "".join(f"<li>{esc(s.format(**fmt))}</li>" for s in d["questions"])
    red = "".join(f"<li>{esc(s.format(**fmt))}</li>" for s in d["red"])
    faqh = "".join(f'<details class="faq-item"><summary class="faq-q">{esc(q)}</summary><div class="faq-a">{esc(a)}</div></details>' for q, a in faq)
    others = [c for c in CATS if c != cat]
    more = "".join(f'<a class="rel-link" href="{gpath(city, c)}"><span class="rel-emoji">{CAT_EMOJI[c]}</span> {esc(CATS[c]["label"])} in {esc(name)}</a>' for c in others)
    same_state = [c for c, (n, s) in CITIES.items() if s == st and c != city][:8]
    if len(same_state) < 6:
        same_state += [c for c in WAVE1 if c in CITIES and c != city and c not in same_state][: 8 - len(same_state)]
    nearby = "".join(f'<a class="rel-link" href="{gpath(c, cat)}">{esc(label)} in {esc(CITIES[c][0])}, {CITIES[c][1]}</a>' for c in same_state)
    crumbs = [("Home", "/"), ("Guides", "/guides"), (label, f"/guides/{slug(cat)}"), (f"{name}, {st}", gpath(city, cat))]
    body = f"""{breadcrumb_html(crumbs)}
<section class="page-hero"><h1>{CAT_EMOJI[cat]} {esc(label)} in {esc(name)}, {st}</h1><p>Costs, how to hire and what to ask &middot; Updated {MONTH_YEAR}</p></section>
<main class="g-wrap">
<article class="g-article">
<p class="g-lead">{esc(d['intro'].format(**fmt))}</p>
<p>{esc(snap)}</p>
<p class="g-small">For the full {esc(lc(label))} guide &mdash; cost drivers, how prices vary by region, licensing and the complete FAQ &mdash; see <a href="/guides/{slug(cat)}">our {esc(lc(label))} guide</a>.</p>
{f'<h2>What to know in {esc(name)}</h2><p>{esc(note)}</p>' if note else ''}
<h2>Typical {esc(lc(label))} costs</h2>
<p class="g-small">National ballpark ranges for planning only. Actual prices in {esc(name)} depend on the scope of work, materials and the provider &mdash; always compare written quotes.</p>
<table class="g-table"><thead><tr><th>Service</th><th>Typical range</th></tr></thead><tbody>{rows}</tbody></table>
{cta_html(cat, name)}
<h2>How to hire the right {esc(d['noun'])} in {esc(name)}</h2><ol>{steps}</ol>
<h2>Questions to ask before you hire</h2><ul>{qs}</ul>
<h2>Red flags to watch for</h2><ul>{red}</ul>
<h2>Licensing and verification in {esc(state)}</h2><p>{esc(d['lic'].format(**fmt))}</p>
<h2>When to schedule</h2><p>{esc(d['timing'])}</p>
<h2>Frequently asked questions</h2><div class="faq-list">{faqh}</div>
<h2>More {esc(name)} guides</h2><div class="rel-grid">{more}</div>
<h2>{esc(label)} guides for other cities</h2><div class="rel-grid">{nearby}</div>
<p class="g-disclaimer">AllCityPros is an independent information resource. We do not endorse, rate or vouch for any specific business, and nothing here is professional advice. Cost ranges are national ballparks and are not quotes. Always verify licenses, insurance and references yourself.</p>
</article>
</main>"""
    # noindex: these 3,745 pages are ~96% identical city-to-city (only the city name and a
    # state-level climate note change), which is what produced thousands of "Google chose a
    # different canonical" in Search Console. The service hub at /guides/<service> is the
    # indexable page; these stay live and crawlable ("follow") for readers and internal links.
    robots = '  <meta name="robots" content="noindex, follow">\n'
    return HEAD.format(title=esc(title), desc=esc(desc), canon=url, ld=ld, robots=robots) + body + FOOT

REGION_ORDER = ["hot_humid", "hot_dry", "mixed", "cold", "mild"]
REGION_NAME = {
    "hot_humid": "Hot &amp; humid South",
    "hot_dry": "Hot &amp; dry Southwest",
    "mixed": "Mixed / four-season",
    "cold": "Cold North &amp; Mountain",
    "mild": "Mild West Coast",
}
REGION_STATES = {r: sorted(st for st, rr in REGION.items() if rr == r) for r in REGION_ORDER}


# The service copy was written to be stamped into a city page, so it is phrased for a specific
# place: "the {state} licensing authority", "{state} homes need...". Substituting a generic
# phrase leaves "the your state licensing authority" and "your state homes need". These two
# helpers reshape the sentence instead of just swapping the token.
def _tidy(out, *words):
    out = re.sub(r"\bthe (your (?:state|city|area)|this region)\b",
                 lambda m: m.group(1) + ("'s" if m.group(1).startswith("your") else "'s"), out)
    out = re.sub(r"\s{2,}", " ", out).strip()
    # Reshaping "{state} homes need" into "homes in this region need" leaves a lower-case opener.
    return out[:1].upper() + out[1:] if out else out


def generic(text):
    """Render city-page service copy at national level."""
    t = text
    for a, b in (("the {city} building department", "your local building department"),
                 ("{city} building department", "your local building department"),
                 ("{city} homeowners", "homeowners"),
                 ("{city} residents", "residents"),
                 ("{state} homeowners", "homeowners"),
                 ("{city} homes", "homes in your area"),
                 ("{state} homes", "homes in your state")):
        t = t.replace(a, b)
    return _tidy(t.format(city="your area", state="your state", st=""))


def region_text(text):
    """Render a per-region climate note where the region, not a state, is the subject."""
    t = text
    for noun in ("homes", "roofs", "lawns", "homeowners", "residents", "yards", "drivers"):
        t = t.replace(f"{{state}} {noun}", f"{noun} in {{state}}")
        t = t.replace(f"{{city}} {noun}", f"{noun} in {{city}}")
    return _tidy(t.format(city="your city", state="this region", st=""))


def category_hub(cat):
    """The one indexable page per service.

    This carries the full guide. The 155 city variants are noindexed because they were
    ~96% identical to each other, so all the ranking signal belongs here.
    """
    d = CATS[cat]
    label = d["label"]
    url = f"{DOMAIN}/guides/{slug(cat)}"
    title = f"{label} Costs & How to Hire: 2026 Guide | AllCityPros"
    # Only promise the regional section on the services that actually have one.
    region_bit = "how needs vary by region, " if cat in CLIMATE else ""
    desc = (f"What {lc(label)} work actually costs, {region_bit}how to compare "
            f"{d['noun']}s, licence checks, red flags and FAQs. Updated {MONTH_YEAR}.")
    faq = [(generic(q), generic(a)) for q, a in d["faq"]]
    ld = ld_block(
        {"@context": "https://schema.org", "@type": "Article", "headline": title, "description": desc,
         "dateModified": TODAY, "datePublished": TODAY, "mainEntityOfPage": url,
         "author": {"@type": "Organization", "name": "AllCityPros"},
         "publisher": {"@type": "Organization", "name": "AllCityPros", "url": DOMAIN}},
        crumbs_ld([("Home", "/"), ("Guides", "/guides"), (label, f"/guides/{slug(cat)}")]),
        {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]})

    rows = "".join(f"<tr><td>{esc(a)}</td><td>{esc(b)}</td></tr>" for a, b in d["cost"])
    steps = "".join(f"<li>{esc(generic(x))}</li>" for x in d["steps"])
    qs = "".join(f"<li>{esc(generic(x))}</li>" for x in d["questions"])
    red = "".join(f"<li>{esc(generic(x))}</li>" for x in d["red"])
    faqh = "".join(f'<details class="faq-item"><summary class="faq-q">{esc(q)}</summary>'
                   f'<div class="faq-a">{esc(a)}</div></details>' for q, a in faq)

    # Regional variation is the one place local detail is real rather than a find-and-replace:
    # these notes are written per service per climate region. Services whose cost drivers are
    # not weather-driven (accounting, legal, tutoring...) have no such data, so they get no table.
    region_block = ""
    if cat in CLIMATE:
        rr = "".join(
            f"<tr><td><strong>{REGION_NAME[r]}</strong><br><span class=\"g-small\">"
            f"{esc(', '.join(REGION_STATES[r]))}</span></td>"
            f"<td>{esc(region_text(CLIMATE[cat][r]))}</td></tr>"
            for r in REGION_ORDER if r in CLIMATE[cat])
        region_block = (f"<h2>How {esc(lc(label))} needs vary by region</h2>"
                        f"<p>Climate changes what matters most, what fails first and when to book. "
                        f"Find your region below.</p>"
                        f'<table class="g-table"><thead><tr><th>Region</th><th>What changes</th></tr></thead>'
                        f"<tbody>{rr}</tbody></table>")

    # Link a readable set of metros, not all 155. Every city hub is in the sitemap already, so
    # the long list bought no discovery -- it just added ~560 words of near-identical link text
    # to all 24 hubs, diluting the editorial content and making the hubs resemble each other.
    top = [c for c in WAVE1 if c in CITIES][:WAVE1_N]
    blocks = ('<div class="rel-grid">'
              + "".join(f'<a class="rel-link" href="{gpath(c, cat)}">{esc(label)} in {esc(CITIES[c][0])}, '
                        f'{CITIES[c][1]}</a>' for c in top)
              + "</div>"
              + f'<p class="g-small"><a href="/">Browse all {len(CITIES)} cities &rarr;</a></p>')

    others = [c for c in CATS if c != cat]
    more = "".join(f'<a class="rel-link" href="/guides/{slug(c)}"><span class="rel-emoji">{CAT_EMOJI[c]}</span> '
                   f'{esc(CATS[c]["label"])}</a>' for c in others)

    crumbs = [("Home", "/"), ("Guides", "/guides"), (label, "")]
    return HEAD.format(title=esc(title), desc=esc(desc), canon=url, ld=ld, robots="") + f"""{breadcrumb_html(crumbs)}
<section class="page-hero"><h1>{CAT_EMOJI[cat]} {esc(label)}: Costs &amp; How to Hire</h1><p>What the work costs, how to compare quotes and what to ask &middot; Updated {MONTH_YEAR}</p></section>
<main class="g-wrap">
<article class="g-article">
<p class="g-lead">{esc(generic(d['intro']))}</p>
<h2>Typical {esc(lc(label))} costs</h2>
<p class="g-small">National ballpark ranges for planning only &mdash; not quotes. What you pay depends on scope, materials, access and your local market, so always compare written estimates.</p>
<table class="g-table"><thead><tr><th>Service</th><th>Typical range</th></tr></thead><tbody>{rows}</tbody></table>
{cta_html(cat, "your area")}
{region_block}
<h2>How to hire the right {esc(d['noun'])}</h2><ol>{steps}</ol>
<h2>Questions to ask before you hire</h2><ul>{qs}</ul>
<h2>Red flags to watch for</h2><ul>{red}</ul>
<h2>Licensing and verification</h2><p>{esc(generic(d['lic']))}</p>
<h2>When to schedule</h2><p>{esc(generic(d['timing']))}</p>
<h2>Frequently asked questions</h2><div class="faq-list">{faqh}</div>
<h2>{esc(label)} by city</h2>
<p class="g-small">Local notes for {len(CITIES)} cities &mdash; licensing bodies, climate and seasonal timing.</p>
{blocks}
<h2>Other guides</h2><div class="rel-grid">{more}</div>
<p class="g-disclaimer">AllCityPros is an independent information resource. We do not endorse, rate or vouch for any specific business, and nothing here is professional advice. Cost ranges are national ballparks and are not quotes. Always verify licences, insurance and references yourself.</p>
</article>
</main>""" + FOOT


def guides_index():
    url = f"{DOMAIN}/guides"
    title = "Local Service Guides: Costs, Hiring Tips & Red Flags | AllCityPros"
    desc = "Independent guides to hiring home-service and professional providers in 150+ U.S. cities: typical costs, questions to ask, licensing checks and red flags."
    ld = ld_block(crumbs_ld([("Home", "/"), ("Guides", "/guides")]))
    cards = "".join(f'<a class="rel-link" href="/guides/{slug(c)}"><span class="rel-emoji">{CAT_EMOJI[c]}</span> {esc(d["label"])} guides</a>' for c, d in CATS.items())
    top = [c for c in WAVE1 if c in CITIES][:WAVE1_N]
    city_cards = "".join(f'<a class="rel-link" href="/{c}">{esc(CITIES[c][0])}, {CITIES[c][1]}</a>' for c in top)
    return HEAD.format(title=esc(title), desc=esc(desc), canon=url, ld=ld, robots="") + f"""{breadcrumb_html([("Home", "/"), ("Guides", "")])}
<section class="page-hero"><h1>Local Service Guides</h1><p>What it costs, how to hire well and what to watch out for &mdash; in {len(CITIES)} U.S. cities.</p></section>
<main class="g-wrap"><article class="g-article"><h2>Browse by service</h2><div class="rel-grid">{cards}</div>
<h2>Popular cities</h2><div class="rel-grid">{city_cards}</div>
<p class="g-disclaimer">AllCityPros is an independent information resource and does not endorse or rate specific businesses.</p></article></main>""" + FOOT

def city_hub(city):
    name, st = CITIES[city]
    url = f"{DOMAIN}/{city}"
    title = f"{name}, {st} Local Service Guides: Costs & Hiring Tips | AllCityPros"
    desc = f"Hiring help in {name}, {st}: cost guides, questions to ask and red flags for HVAC, plumbing, roofing, legal, accounting and 18 more services."
    ld = ld_block(crumbs_ld([("Home", "/"), (f"{name}, {st}", f"/{city}")]))
    # Point the city hub at the indexable service guides. It used to link only the city x service
    # leaves, which are now noindexed -- that left every city hub a dead end passing no signal to
    # the pages meant to rank. The local page is still offered, as a secondary "local notes" link.
    cards = "".join(f'<a class="rel-link" href="/guides/{slug(c)}"><span class="rel-emoji">{CAT_EMOJI[c]}</span> '
                    f'{esc(d["label"])}</a>' for c, d in CATS.items())
    local = "".join(f'<a class="rel-link" href="{gpath(city, c)}">{esc(CATS[c]["label"])} in {esc(name)}</a>'
                    for c in CATS)
    return HEAD.format(title=esc(title), desc=esc(desc), canon=url, ld=ld, robots="") + f"""{breadcrumb_html([("Home", "/"), ("Guides", "/guides"), (f"{name}, {st}", "")])}
<section class="page-hero"><h1>{esc(name)}, {st} Local Service Guides</h1><p>Costs, hiring checklists and red flags for {len(CATS)} services &middot; Updated {MONTH_YEAR}</p></section>
<main class="g-wrap"><article class="g-article"><h2>Choose a service</h2><div class="rel-grid">{cards}</div>
<p>These guides explain what typical projects cost, how to compare providers and how to check licensing in {esc(STATE_NAMES[st])}.</p>
<h2>Local notes for {esc(name)}</h2>
<p class="g-small">Short {esc(name)}-specific notes on climate, seasonal timing and {esc(STATE_NAMES[st])} licensing. The full guidance is in the service guides above.</p>
<div class="rel-grid">{local}</div>
<p class="g-disclaimer">AllCityPros is an independent information resource and does not endorse or rate specific businesses. Sample directory entries from an earlier version of this site are kept for reference at <a href="/{city}/listings">/{city}/listings</a> and are not verified.</p></article></main>""" + FOOT

def homepage():
    url = DOMAIN + "/"
    title = "AllCityPros: Local Service Guides for Homeowners & Small Businesses"
    desc = f"Costs, hiring checklists and red flags for 24 home and professional services in {len(CITIES)} U.S. cities. Independent, plain-English guides."
    ld = ld_block({"@context": "https://schema.org", "@type": "WebSite", "name": "AllCityPros", "url": DOMAIN})
    top = [c for c in WAVE1 if c in CITIES][:12]
    cats = "".join(f'<a class="rel-link" href="/guides/{slug(c)}"><span class="rel-emoji">{CAT_EMOJI[c]}</span> {esc(d["label"])}</a>' for c, d in CATS.items())
    pop = "".join(f'<a class="rel-link" href="{gpath(c, k)}">{CAT_EMOJI[k]} {esc(CATS[k]["label"])} in {esc(CITIES[c][0])}</a>'
                  for c in top[:4] for k in ("hvac", "plumbing", "roofing")[:3])
    cards = "".join(f'<a href="/{c}" class="city-card"><div class="city-icon">{EMOJI.get(c, "📍")}</div><div class="city-info"><div class="city-name">{esc(n)}</div><div class="city-count">{s}</div></div></a>'
                    for c, (n, s) in sorted(CITIES.items(), key=lambda x: (x[1][0], x[1][1])))
    return (HEAD.format(title=esc(title), desc=esc(desc), canon=url, ld=ld, robots="").replace('og:type" content="article"', 'og:type" content="website"') + f"""
<section class="hero"><div class="hero-content">
  <div class="hero-badge">Independent local service guides</div>
  <h1>Hire Local Pros <em>With Confidence</em></h1>
  <p>Typical costs, questions to ask and red flags to watch for &mdash; for 24 services in {len(CITIES)} U.S. cities.</p>
  <div class="hero-search"><input type="text" id="city-search" placeholder="Search your city…" oninput="filterCities(this.value)" autocomplete="off"><button type="button" onclick="filterCities(document.getElementById('city-search').value)">Search</button></div>
</div></section>
<main>
<div class="section"><h2 class="section-title">Browse guides by service</h2><p class="section-sub">Pick a service to see guides for every city we cover</p><div class="g-article"><div class="rel-grid">{cats}</div></div></div>
<div class="section"><h2 class="section-title">Popular guides</h2><div class="g-article"><div class="rel-grid">{pop}</div></div></div>
<div class="section" id="cities"><h2 class="section-title">Browse by city</h2><p class="section-sub">Select your city to see every guide for it</p>
  <div class="city-grid" id="city-grid">{cards}</div>
  <p id="no-results" style="display:none;text-align:center;color:var(--gray-400);margin-top:20px;">No matching city. Try another name.</p>
</div>
<div class="section" id="list-business"><h2 class="section-title">About AllCityPros</h2><p style="color:var(--gray-600);line-height:1.7;">AllCityPros publishes independent guides to help you compare providers. We do not endorse or rate specific businesses. Questions or corrections? <a href="mailto:hello@allcitypros.com?subject=Guide%20feedback">Email us</a>.</p></div>
</main>
<script>
function filterCities(q) {{
  q = q.toLowerCase().trim();
  var cards = document.querySelectorAll('#city-grid .city-card'), visible = 0;
  cards.forEach(function(c) {{
    var show = !q || c.querySelector('.city-name').textContent.toLowerCase().includes(q);
    c.style.display = show ? '' : 'none'; if (show) visible++;
  }});
  document.getElementById('no-results').style.display = visible === 0 ? 'block' : 'none';
}}
</script>""" + FOOT)

def write(path, content):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    open(full, "w").write(content)

def main():
    n = 0
    for city in CITIES:
        for cat in CATS:
            write(f"guides/{city}-{slug(cat)}.html", guide_page(city, cat)); n += 1
    for cat in CATS:
        write(f"guides/{slug(cat)}.html", category_hub(cat))
    write("guides/index.html", guides_index())
    write("index.html", homepage())
    for city in CITIES:
        idx = os.path.join(ROOT, city, "index.html"); lst = os.path.join(ROOT, city, "listings.html")
        if os.path.exists(idx) and not os.path.exists(lst):
            os.rename(idx, lst)  # keep the old listings page (noindexed by scripts/noindex_listings.py)
        write(f"{city}/index.html", city_hub(city))
    # City x service guides are noindex (see guide_page). build_sitemap scans the tree and
    # lists only indexable URLs, split under the 50,000-URL / 50 MB sitemap limits.
    info = build_sitemap(ROOT)
    print(
        f"guides: {n} (noindex), service hubs: {len(CATS)}, city hubs: {len(CITIES)}, "
        f"sitemap urls: {info['url_count']}"
    )

if __name__ == "__main__":
    main()
