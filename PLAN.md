# When To Book — Plan

Current roadmap. Scribe keeps this updated. Orchestrator reads this at the start of every session.

Last updated: 2026-05-04

See `IMPROVEMENT_PLAN.md` for the full strategic context behind these items.

---

## Active / Up Next

- [ ] **Activate GitHub Pages** — go to `https://github.com/215781/booking-window/settings/pages`, set Source: "Deploy from a branch" → `main` → `/ (root)`. CNAME already committed. **User action required.**
- [ ] **Configure DNS at Squarespace** — Squarespace > Domains > `whentobook.co.uk` > DNS Settings. Add 4 A records (`@` → `185.199.108.153 / .109 / .110 / .111`) + CNAME (`www` → `215781.github.io`). After propagation: confirm custom domain in Pages Settings + Enforce HTTPS. **User action required.**
- [ ] **Decommission Vercel** (once Pages DNS is live) — remove Vercel project. `vercel.json` can stay in repo as the Vercel block for `/_data/` is a safety net.
- [ ] **Confirm `VMOC_WINTER` code** — a space was noted (`VMO C_WINTER`) in one session note. Verify the actual code in `clubmed_checker.py` against the API.
- [ ] **Grand Massif + Serre-Chevalier departure day** — both show Sat+Sun prices. Needs data accumulation to confirm correct departure day, then lock it in the checker.
- [ ] **🔴 URGENT: Eurostar Snow ticket alert page** — tickets go on sale **9 July 2026 at ~8am**. Build a page to capture emails + send an alert. Deadline in 36 days from 2026-05-04. (See IMPROVEMENT_PLAN.md QW-3)
- [ ] **Fix deep-link Club Med CTAs** — "Book on Club Med" buttons link to homepage; update `bookingUrl` in RESORT_DATA to link directly to each resort's booking page (`clubmed.co.uk/r/[slug]/y`). Pre-work for affiliate programme. (QW-1)
- [ ] **Add analytics** — install Plausible Analytics (recommended) or GA4. Currently flying blind with no visitor data. (QW-4)
- [ ] **URL architecture restructure — move Club Med site to `/clubmed` path** — the site currently serves at root `/`. Restructure so `whentobook.co.uk/clubmed` hosts the Club Med tracker and the root becomes a brand landing page (listing all operators). This sets up URL architecture for future expansions (`/markwarner`, `/sandals` etc.). Steps: (1) create `clubmed/` subfolder, move `WhentoBook.html` → `clubmed/index.html`; (2) update `clubmed_checker.py` to write to `clubmed/index.html`; (3) update `vercel.json` routing; (4) add 301 redirect from old root URLs; (5) build minimal root `index.html` brand landing page; (6) update canonical URLs and sitemap. Do this **before** significant SEO traction to avoid breaking established URLs. (Architecture)

---

## Backlog (future work, not yet prioritised)

### Quick wins (high value, low effort)
- [ ] **Real resort photography** — card image areas are currently gradient placeholders. Source from Club Med press kit or Unsplash. (QW-5)
- [ ] **Improve OG image** — current `og-image.svg` may not render in all social preview contexts. Create a 1200×630 PNG. (QW-6)

### Medium term
- [ ] **Affiliate programme — apply to Awin** — apply once ~100 click-throughs are happening. 45-day cookie (UK), ~3% commission, ~£150 per £5,000 booking. Position as Club Med specialist content site. (MT-1)
- [ ] **3-adult party size** — add 3-adult option to search form and RESORT_DATA. Also verify 6-night checker queries are working. (MT-2)
- [ ] **Mobile responsiveness** — layout uses CSS Grid with fixed column counts; needs thorough mobile testing and media query fixes. (existing)
- [ ] **SEO foundations — schema markup** — add JSON-LD schema (`WebSite`, `TravelAgency`, resort entities). Do after URL restructure so canonical URLs are correct. (MT-3)
- [ ] **Blog / content section** — build `whentobook.co.uk/blog` using Jekyll's `_posts/` folder (GitHub Pages supports natively). Create `_layouts/post.html` matching site design, `blog/index.html` listing page. First 5 target articles listed in IMPROVEMENT_PLAN.md. (MT-3b)
- [ ] **Content Writer agent (CONTENT_WRITER.md)** — write a dedicated agent file for researching and publishing SEO blog posts to `_posts/`. Target 2 articles per month once blog is set up. (MT-3c)
- [ ] **Email sequence expansion** — extend Kit welcome sequence from 1 email to 4–6 emails over 2–3 weeks (how Club Med pricing works, resort comparison, what to watch). (MT-4)
- [ ] **Price alert trigger — flash sale notification** — alert subscribers when the annual Club Med early booking flash sale opens (ski ~Feb, summer ~Oct). (MT-5)
- [ ] **Booking-window analysis script** — target Oct 2026 when price_history.csv has 6+ months of data. Group by resort + departure date, plot price vs days_before_departure, find inflection points at 180d, 90d, 60d, 30d, 14d, 7d. (MT-6)

### Summer resort expansion
- [ ] **Phase 1: European summer resorts** — add 5–7 resorts: Magna Marbella (code `MMAC` — already verified), Cefalù, Gregolimano, Palmiye, Marrakech La Palmeraie, Da Balaia, La Palmyre. Requires: resort code discovery via DevTools, checker update, UI ski/beach toggle, date range update. Target: before Oct 2026 summer booking window. (See IMPROVEMENT_PLAN.md)
- [ ] **Phase 2: Caribbean resorts** — Cancún, Punta Cana, Les Boucaniers. (after Phase 1 stable)
- [ ] **Phase 3: Indian Ocean + Asia** — Maldives, Mauritius, Phuket, Bali. (after Phase 2 stable)
- [ ] **Phase 4: Remaining ski resorts** — Pragelato Sestriere (Italy), Saint-Moritz Roi Soleil (Switzerland). (low priority — small incremental value over existing 11)

### Long term / growth
- [ ] **SEO content at scale** — 20–40 articles targeting booking intent keywords ("best time to book Club Med [resort]", "Club Med price history", "when does Club Med release ski prices"). (LT-1)
- [ ] **Mark Warner / Neilson tracker** — same ski audience, natural second site in the portfolio. (LT-3)
- [ ] **Eurostar Snow seasonal service** — beyond the one-time alert, build a full Eurostar Snow price tracker for ski train routes. (LT-4)
- [ ] **Annual Club Med price report** — email broadcast each September/October with price movement data. High shareability. (LT-5)
- [ ] **Drop Media Ltd — Companies House registration** — register before significant revenue. £12, 15 mins. Enables cross-portfolio email marketing. (LT-6)
- [ ] **DATA_SUFFICIENT = true** — change flag in WhentoBook.html to enable live signals. Do not change until autumn 2026. (existing invariant)

---

## Completed

- [x] Built single-file HTML/CSS/JS site (`WhentoBook.html`) — 2026-04-21
- [x] Python price checker (`clubmed_checker.py`) built and verified — 2026-04-21
- [x] GitHub Actions workflow set up (`.github/workflows/price_checker.yml`) — 2026-04-21
- [x] All 6 original resort codes verified via GraphQL API — 2026-04-21
- [x] Expanded to 11 resorts; all codes verified — 2026-04-26 to 2026-04-27
- [x] Scheduled checker live — daily at 06:00 UTC — 2026-04-28
- [x] `price_history.csv` has ~5,862 rows; 2,205 junk rows purged — 2026-04-28
- [x] Signal system: Favourable / Watch / Hold — 2026-04-26
- [x] Three-mode date search, modal search results, mobile layout, alpine card gradients, child age input — 2026-04-26
- [x] CNAME committed (`whentobook.co.uk`) — 2026-04-22
- [x] Cookie notice and `privacy.html` live — 2026-04-26
- [x] Vercel deployment fixed — `vercel.json` committed, rewrite `/` → `/WhentoBook.html` — 2026-04-28
- [x] Kit Cowork session: both forms configured, custom field, tags, welcome sequence live — 2026-04-28
- [x] Search popup wired to correct Kit form (`f197f8f414`) — 2026-04-28
- [x] Season price calendar view added to resort modal — 2026-04-26
- [x] Multi-agent workflow set up: CLAUDE.md, ORCHESTRATOR.md, BUILDER.md, SCRIBE.md — 2026-05-04
- [x] price_history.csv moved to `_data/price_history.csv` (hidden from GitHub Pages/Vercel) — 2026-05-04
