"""Cleanup of the original template-generated directory pages.

Those pages describe businesses that are not verified (names come from templates
in generate_all.py). This script:
  - keeps <meta name="robots" content="noindex, follow">
  - removes fake rating/review markup, dead Formspree forms, and placeholder Impact links
  - adds a visible sample-entry notice pointing at the real guide
  - makes canonicals self-reference the final URL (apex, no .html, no trailing slash)
  - drops links to other sample listings, including /<city>/<file>.html links that
    308 under cleanUrls, and points remaining city links at /<city>
  - removes the city-hub link to /<city>/listings

Idempotent. Run from the repo root after scripts/generate_guides.py:
    python3 scripts/noindex_listings.py
"""
import os, re, sys
from multiprocessing import Pool

sys.path.insert(0, os.path.dirname(__file__))
from guide_data import CATS  # noqa: E402
from generate_guides import CITIES, gpath, slug  # noqa: E402
from build_sitemap import build as build_sitemap  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MARK = '<meta name="robots" content="noindex, follow">'
MAILTO = '<p><a href="mailto:hello@allcitypros.com?subject=List%20My%20Business">Email us to claim, correct or remove this entry</a></p>'

R = [
    (re.compile(r',\s*"aggregateRating":\s*\{[^}]*\}'), ""),
    (re.compile(r'<div class="rating-badge">.*?</div>', re.S), ""),
    (re.compile(r'<div class="contact-item">\s*<span class="ci">⭐</span>.*?</div>\s*</div>\s*</div>', re.S), ""),
    (re.compile(r'<div class="contact-item">\s*<span class="ci">🪪</span>.*?</div>\s*</div>\s*</div>', re.S), ""),
    (re.compile(r'<div class="contact-item">\s*<span class="ci">🕐</span>.*?</div>\s*</div>\s*</div>', re.S), ""),
    (re.compile(r'<p[^>]*>⭐ <strong>[\d.]+ / 5</strong> based on \d+ local reviews</p>'), ""),
    (re.compile(r'<div class="card-rating">.*?</div>'), ""),
    (re.compile(r'<!-- Impact affiliate banner -->\s*<div[^>]*>.*?</div>', re.S), ""),
    (re.compile(r'<a href="https://[a-z]+\.sjv\.io/c/YOUR_IMPACT_ID[^"]*"[^>]*>.*?</a>', re.S), ""),
    (re.compile(r'<h2>Get a Free Quote</h2>\s*<div class="quote-form">.*?</form>\s*</div>', re.S), ""),
    (re.compile(r'<h2>Customer Reviews</h2>.*?Thank you for your review!</div>', re.S), ""),
    (re.compile(r' ?Rated [\d.]+★ by local customers\.'), ""),
    (re.compile(r' ?Rated [\d.]+★\.'), ""),
    (re.compile(r'<form[^>]*formspree\.io.*?</form>', re.S), MAILTO),
]

def banner(city, cat):
    name, st = CITIES[city]
    if cat:
        link = f'<a href="{gpath(city, cat)}">our {CATS[cat]["label"]} guide for {name}, {st}</a>'
    else:
        link = f'<a href="/{city}">our {name} guides</a>'
    return ('<div style="background:#fef3c7;border-bottom:1px solid #fde68a;color:#78350f;padding:12px 20px;text-align:center;font-size:0.9rem;">'
            'Sample entry from an early version of this site. The details on this page are illustrative and not verified. '
            f'For real hiring help, see {link}.</div>')

def parse(city, fname):
    base = fname[:-5]
    m = re.match(rf"^{re.escape(city)}_(.+?)(?:_\d+)?$", base, re.I)
    key = m.group(1).lower() if m else base.lower()
    return key if key in CATS else None

# "Other {category} Pros" is the block that linked sample listings as .html URLs.
OTHER_PROS = re.compile(
    r"\s*<br>\s*<h2>Other [^<]*</h2>\s*<div class=\"rel-grid\">.*?</div>",
    re.S,
)
# /{city}/ 308s to /{city} because trailingSlash is false. The homepage stays "/".
TRAILING_HREF = re.compile(r'href="/([A-Za-z0-9]+)/"')
TRAILING_ABS = re.compile(r'https://allcitypros.com/([A-Za-z0-9]+)/"')
HOME_ITEM = '"item":"https://allcitypros.com"'
HOME_FIXED = '"item":"https://allcitypros.com/"'
CARD_OPEN = re.compile(r'<a href="/[^"]+\.html" (class="listing-card" data-cat="[^"]*")>')
CARD_CLOSE = '<div class="btn-primary">View Details →</div>\n      </div>\n    </a>'
CARD_CLOSE_NEW = '<div class="btn-primary">View Details →</div>\n      </div>\n    </div>'
LISTINGS_LINK = re.compile(
    r" Sample directory entries from an earlier version of this site are kept for reference"
    r' at <a href="/[A-Za-z0-9]+/listings">/[A-Za-z0-9]+/listings</a> and are not verified\.'
)
LISTINGS_LINK_NEW = (
    " Sample directory entries from an earlier version of this site are kept for reference"
    " and are not verified."
)
VIEWPORT = '<meta name="viewport" content="width=device-width, initial-scale=1.0">'


def _still_dirty(text):
    return (
        MARK not in text
        or "aggregateRating" in text
        or "formspree.io" in text
        or "YOUR_IMPACT_ID" in text
        or "card-rating" in text
    )


def fix_signals(city, fname, text):
    """Point this page at final URLs and stop linking sample listings."""
    if fname == "index.html":
        return LISTINGS_LINK.sub(LISTINGS_LINK_NEW, text)
    if fname == "listings.html":
        # The old canonical was the city hub with a trailing slash, which 308s,
        # so Google could not treat it as this page's own URL.
        text = text.replace(
            f'https://allcitypros.com/{city}/"',
            f'https://allcitypros.com/{city}/listings"',
        )
        text = CARD_OPEN.sub(r"<div \1>", text)
        text = text.replace(CARD_CLOSE, CARD_CLOSE_NEW)
        text = TRAILING_HREF.sub(r'href="/\1"', text)
        return text.replace(HOME_ITEM, HOME_FIXED)
    # Numbered files (yonkers_tutoring_37.html) and older named files
    # (Kansas_City_legal.html) are the same sample-listing template.
    if fname.endswith(".html"):
        text = OTHER_PROS.sub("", text, count=1)
        text = TRAILING_HREF.sub(r'href="/\1"', text)
        text = TRAILING_ABS.sub(r'https://allcitypros.com/\1"', text)
        return text.replace(HOME_ITEM, HOME_FIXED)
    return text


def process(args):
    city, fname = args
    path = os.path.join(ROOT, city, fname)
    with open(path, encoding="utf-8") as handle:
        text = handle.read()
    original = text
    if fname != "index.html" and _still_dirty(text):
        for rx, rep in R:
            text = rx.sub(rep, text)
        if MARK not in text:
            text = text.replace(VIEWPORT, VIEWPORT + "\n  " + MARK, 1)
            if MARK not in text:
                text = text.replace("<head>", "<head>\n  " + MARK, 1)
        if "Sample entry from an early version" not in text:
            cat = None if fname == "listings.html" else parse(city, fname)
            text = text.replace("</header>", "</header>\n" + banner(city, cat), 1)
    text = fix_signals(city, fname, text)
    if text == original:
        return 0
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)
    return 1


def main():
    jobs = []
    for city in CITIES:
        directory = os.path.join(ROOT, city)
        if not os.path.isdir(directory):
            continue
        for fname in os.listdir(directory):
            if fname.endswith(".html"):
                jobs.append((city, fname))
    with Pool() as pool:
        done = sum(pool.imap_unordered(process, jobs, chunksize=200))
    print(f"updated {done} of {len(jobs)} pages")
    info = build_sitemap(ROOT)
    print(f"sitemap urls: {info['url_count']}")
    for name, count in info["files"]:
        print(f"  {name}: {count}")

if __name__ == "__main__":
    main()
