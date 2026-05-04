# When To Book — Plan

Current roadmap. Scribe keeps this updated. Orchestrator reads this at the start of every session.

Last updated: 2026-05-04 (session end)

See `IMPROVEMENT_PLAN.md` for the full strategic context behind these items.

---

## Active / Up Next

- [x] **Data gap backfill** — `backfill_prices.py` built and run: 3,717 rows added for 2026-04-27 to 2026-05-03; backfilled rows marked with `T00:00:00Z` timestamp (vs live data at real UTC times). Run after any future multi-day gap: `python backfill_prices.py && python clubmed_checker.py --inject-only` — 2026-05-04
- [x] **Configure DNS at Squarespace** — 4 × A records + CNAME confirmed configured. DNS resolving to GitHub Pages IPs (185.199.108–111.153). — 2026-05-04
- [x] **GitHub Pages active** — HTTP 200 confirmed from GitHub.com server. Root serves brand landing page; `/clubmed/` serves tracker (373KB). HTTPS cert auto-provisioning (may take a few hours). Once HTTPS is live, go to Settings → Pages → Enforce HTTPS. — 2026-05-04
- [ ] **Enforce HTTPS on GitHub Pages** — Once cert is provisioned: go to `https://github.com/215781/booking-window/settings/pages`, tick "Enforce HTTPS". **User action — check in a few hours.**
- [ ] **Decommission Vercel** — DNS no longer routes to Vercel (points to GitHub Pages). Safe to remove Vercel project. `vercel.json` stays in repo for reference. **User action.**
- [ ] **Wire up GA4 measurement ID** — GA4 script added to `clubmed/index.html` with placeholder `G-XXXXXXXXXX`. Create a GA4 property at analytics.google.com, get the Measurement ID, and replace the placeholder. Then commit. **User action required to create property.**
- [x] **Confirm `VMOC_WINTER` code** — verified correct in `clubmed_checker.py` and CSV. No space. The session note was erroneous. — 2026-05-04
- [ ] **Grand Massif + Serre-Chevalier departure day** — both show Sat+Sun prices. Needs data accumulation to confirm correct departure day, then lock it in the checker.

### 🔴 HIGH PRIORITY — Start data collection now (before sites are built)

- [ ] **Build Mark Warner price checker** — **Research done 2026-05-04:** Mark Warner has only ONE ski property (Chalet Hotel L'Écrin, Tignes; product ID `SKI-24314`). Site is ASP.NET Core with Vue.js frontend. Found API endpoint `/resort/getresortsearchcriteria/` but exact request payload requires DevTools capture. **User action needed:** open `markwarner.co.uk/ski-holidays/france/chalet-hotel-lecrin/accommodation` in Chrome DevTools (Network tab, filter XHR), click search/availability, copy the full request URL + payload + response. Alternative: accommodation page shows seasonal prices as server-rendered HTML (Christmas/Jan/Feb/Easter) — could scrape this instead. Note: only 1 resort limits value vs Club Med's 11.
- [ ] **Build Sandals price checker** — GitHub references confirm an "official Sandals booking API" exists but it's not publicly documented — may require a partner relationship. Try reverse-engineering `sandals.co.uk` via DevTools first. Also check for a `/developers` or `/partner` portal. Build `sandals_checker.py` + `_data/sandals_prices.csv`. Add to Actions.
- [ ] **Add both new checkers to GitHub Actions** — Create `.github/workflows/markwarner_checker.yml` and `.github/workflows/sandals_checker.yml` (or extend `price_checker.yml`). Daily at offset times (e.g. 07:00 and 08:00 UTC) to avoid concurrent runs. Commit updated CSVs.

---

## Backlog (future work, not yet prioritised)

### Quick wins (high value, low effort)
- [ ] **Real resort photography** — card image areas are currently gradient placeholders. Source from Club Med press kit or Unsplash. (QW-5)
- [x] **Improve OG image** — `og-image.png` created (1200×630 PNG from SVG via qlmanage+sips). Both `clubmed/index.html` and `index.html` updated to reference PNG with explicit width/height meta tags. — 2026-05-04

### Medium term
- [x] **Cybersecurity review** — completed 2026-05-04. Findings: no hardcoded secrets; GitHub Actions permissions minimal; XSS self-injection risk in `noMsg` (fixed with `escapeHtml()`); `BookingWindow_v1_2.html` removed from root; security headers added to `vercel.json` (X-Frame-Options, X-Content-Type-Options, Referrer-Policy, Permissions-Policy, CSP). Remaining gap: inline scripts mean CSP uses `unsafe-inline` — acceptable for this stack.
- [x] **Data backup** — weekly GitHub Releases backup added (`.github/workflows/backup.yml`). Runs every Sunday at 02:00 UTC, creates a tagged pre-release with `price_history.csv` as a downloadable artifact. Manual trigger also available. — 2026-05-04
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
- [ ] **Mark Warner / Sandals tracker** — Mark Warner (ski) and Sandals (Caribbean all-inclusive) are the next two operators in the portfolio. (LT-3)
- [ ] **Annual Club Med price report** — email broadcast each September/October with price movement data. High shareability. (LT-5)
- [ ] **Drop Media Ltd — Companies House registration** — register before significant revenue. £12, 15 mins. Enables cross-portfolio email marketing. (LT-6)
- [ ] **DATA_SUFFICIENT = true** — change flag in `clubmed/index.html` to enable live signals. Do not change until autumn 2026. (existing invariant)
- [ ] **Eurostar Snow alert page** — build a page to capture emails and send an alert when Eurostar Snow tickets go on sale. Kit infrastructure already in place — needs a new form + page. (QW-3, lowest priority)
- [ ] **Eurostar Snow seasonal service** — beyond the one-time alert, build a full Eurostar Snow price tracker for ski train routes. (LT-4, lowest priority)

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
- [x] Agent .md files mirrored to vault at `When To Book/Agents/` — 2026-05-04
- [x] URL restructure: `clubmed/index.html` created, root `index.html` brand landing page built, checker + workflow + vercel.json updated, sitemap updated, `WhentoBook.html` converted to redirect — 2026-05-04
- [x] Deep-link Club Med CTAs verified — all `bookingUrl` values already point to resort-specific booking pages — 2026-05-04
- [x] GA4 analytics script added to `clubmed/index.html` with placeholder `G-XXXXXXXXXX` — user must create GA4 property and swap in Measurement ID — 2026-05-04
- [x] Data purge: 612 suspect LP2C_WINTER + VDIC_WINTER rows (Apr 23–25, unverified codes) removed from `price_history.csv`; RESORT_DATA regenerated via `--inject-only` — 2026-05-04
- [x] `VMOC_WINTER` code verified correct; `--inject-only` flag added to `clubmed_checker.py` — 2026-05-04
</content>
</invoke>