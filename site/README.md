# whentobook.co.uk - new site (Astro)

Not live yet. The live site is still served from `main` by GitHub Pages; this lives on the `rebuild` branch.

```
cd site
npm ci
npm run build   # builds src/data/summary.json from ../_data/prices_clubmed.csv, then the static site into dist/
npm test        # link check, banned words, no "Ltd", no secrets, 11 resort pages with prices, JSON-LD valid, data fresh, GA only after consent
npx astro preview
```

- `scripts/build_summary.py` - one pass over the price CSV; only real collected prices; flags stale data.
- `scripts/prepare_images.py` - resizes ../images into public/images.
- Pages: home, /club-med/ hub, /club-med/<resort>/ (11), /school-holidays/, /blog/ (existing posts, same URLs), about, privacy, terms, affiliate disclosure, llms.txt, sitemap.
- Signup posts to Kit form 7f784a323c (public endpoint, no API key). Google Analytics loads only after cookie consent.
