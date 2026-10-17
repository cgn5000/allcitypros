# AllCityPros

Independent city x service guides (24 services, 155 cities). Static HTML on Vercel; pushing to `main` auto-deploys (~8 min).

## Regenerate
```
python3 scripts/generate_guides.py      # guides, hubs, homepage, sitemap (wave 1 = WAVE1_N cities)
python3 scripts/noindex_listings.py     # one-off cleanup of the old template listings (idempotent)
```
- Content lives in `scripts/guide_data.py` (national cost ranges only; no ratings, no business names).
- Grow the sitemap by raising `WAVE1_N` (env var) once earlier waves are indexed.
- Monetization: fill `scripts/monetization.json` (affiliate `cta` per category). Nothing renders until set.
- The old listings (`<city>/*_*.html`, `<city>/listings.html`) are template-generated samples: noindexed and labeled.
