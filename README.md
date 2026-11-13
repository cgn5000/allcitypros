# AllCityPros

Independent city x service guides (24 services, 155 cities). Static HTML on Vercel; pushing to `main` auto-deploys (~8 min).

## Regenerate
```
python3 scripts/generate_guides.py      # guides, city hubs, homepage, sitemap
python3 scripts/noindex_listings.py     # keep template listings noindexed and unlinked
```
- Content lives in `scripts/guide_data.py` (national cost ranges only; no ratings, no business names).
- `WAVE1_N` (default 25, overridable with the `WAVE1_N` env var) only shortens the "popular cities" link list on the service hubs. It does not decide which URLs are indexed or listed in the sitemap.
- City x service pages (`guides/<city>-<service>.html`) stay noindex. They repeat the service hub with the city name swapped in, which is what made Google choose a different canonical. The files stay on the site; they are not in the sitemap.
- Template listings (`<city>/<city>_*.html` and `<city>/listings.html`) stay noindex. Indexable pages do not link to them, and `scripts/build_sitemap.py` leaves them out even if the robots tag is missing.
- Canonicals and internal links use the URL Vercel serves with HTTP 200: `https://allcitypros.com` plus the path, no `www`, no `.html`, and no trailing slash. The homepage keeps `https://allcitypros.com/`. `vercel.json` sets `cleanUrls` and `trailingSlash: false`, and permanently redirects `www.allcitypros.com` to the apex host.
- Monetization: fill `scripts/monetization.json` (affiliate `cta` per category). Nothing renders until set.
