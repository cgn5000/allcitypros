"""One-off cleanup of the original template-generated directory pages.

Those pages describe businesses that are not verified (names come from templates in generate_all.py) and carried
invented ratings/review counts, so this script:
  - adds <meta name="robots" content="noindex, follow">
  - removes the fake rating/review markup (JSON-LD aggregateRating, badges, sidebar rating, card ratings, review form)
  - removes dead Formspree forms and the placeholder Impact links (YOUR_IMPACT_ID)
  - adds a visible 'sample entry' notice pointing to the real guide
Idempotent. Run from the repo root AFTER scripts/generate_guides.py:  python3 scripts/noindex_listings.py
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

def process(args):
    city, fname = args
    p = os.path.join(ROOT, city, fname)
    s = open(p, encoding="utf-8").read()
    if MARK in s:
        return 0
    for rx, rep in R:
        s = rx.sub(rep, s)
    s = s.replace('<meta name="viewport" content="width=device-width, initial-scale=1.0">',
                  '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n  ' + MARK, 1)
    if MARK not in s:  # unexpected head layout
        s = s.replace("<head>", "<head>\n  " + MARK, 1)
    cat = None if fname == "listings.html" else parse(city, fname)
    s = s.replace("</header>", "</header>\n" + banner(city, cat), 1)
    open(p, "w", encoding="utf-8").write(s)
    return 1

def main():
    jobs = []
    for city in CITIES:
        d = os.path.join(ROOT, city)
        if not os.path.isdir(d):
            continue
        for f in os.listdir(d):
            if f.endswith(".html") and f != "index.html":
                jobs.append((city, f))
    with Pool() as pool:
        done = sum(pool.imap_unordered(process, jobs, chunksize=200))
    print(f"processed {done} of {len(jobs)} pages")
    info = build_sitemap(ROOT)
    print(f"sitemap urls: {info['url_count']}")

if __name__ == "__main__":
    main()
