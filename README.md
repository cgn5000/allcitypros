# AllCityPros

Independent city x service guides (24 services, 155 cities). Static HTML on Vercel; pushing to `main` auto-deploys (~8 min).

## Regenerate
```
python3 scripts/generate_guides.py      # guides, city hubs, homepage, sitemap
python3 scripts/noindex_listings.py     # keep template listings noindexed and unlinked
```
- Content lives in `scripts/guide_data.py` (national cost ranges only; no ratings, no business names).
- `WAVE1_N` (default 25, overridable with the `WAVE1_N` env var) only shortens the "popular cities" link list on the service hubs. It does not decide which URLs are indexed or listed in the sitemap.
- Local data (added 2026-11-15) lives in `scripts/local_data/` and is rendered by `scripts/local_render.py`: state licensing bodies, rules and official lookups for HVAC, plumbing, electrical, roofing, general contracting and attorneys (42 jurisdictions, hand-researched from official sites); official building-permit pages per city; Census County Business Patterns 2023 firm counts by county; BLS OEWS May 2025 metro median wages; NOAA 1991-2020 climate normals. Every figure on a page names its source and the date checked. `scripts/build_local_data.py RAW_DIR` rebuilds `cbp.json`, `oews.json`, `climate.json` from the raw federal downloads (URLs in its docstring).
- City x service pages for those six trades are indexable when the state licensing entry and Census data exist, except where several cities share one county (same Census, wage and climate figures): only the largest city in that county is indexable (`COUNTY_PRINCIPAL` in `local_render.py`). That is 756 pages.
- All other city x service pages (`guides/<city>-<service>.html`) stay noindex. They repeat the service hub with the city name swapped in, which is what made Google choose a different canonical. The files stay on the site; they are not in the sitemap.
- Template listings (`<city>/<city>_*.html` and `<city>/listings.html`) stay noindex. Indexable pages do not link to them, and `scripts/build_sitemap.py` leaves them out even if the robots tag is missing.
- Canonicals and internal links use the URL Vercel serves with HTTP 200: `https://allcitypros.com` plus the path, no `www`, no `.html`, and no trailing slash. The homepage keeps `https://allcitypros.com/`. `vercel.json` sets `cleanUrls` and `trailingSlash: false`, and permanently redirects `www.allcitypros.com` to the apex host.
- Monetization: fill `scripts/monetization.json` (affiliate `cta` per category). Nothing renders until set.
