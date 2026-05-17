# When To Book — Plan

Current roadmap. Scribe keeps this updated. Orchestrator reads this at the start of every session.

Last updated: 2026-05-17 (go-live; signal-first cards; articles 3–7; summer tracker consolidated into /clubmed with Ski/Summer toggle)

See `IMPROVEMENT_PLAN.md` for the full strategic context behind these items.

---

## ✅ SITE STATUS — LIVE

`whentobook.co.uk` and `whentobook.co.uk/clubmed` are live as of 2026-05-17.

- [x] **Under construction page created** — `under-construction.html`: on-brand dark teal, "We're sharpening our data. Back soon.", Kit email signup form. (commit 2575e57) — 2026-05-06
- [x] **Entry-point redirects added** — `index.html` and `clubmed/index.html` both redirect to `/under-construction.html` via meta-refresh. (commit 720f853) — 2026-05-06
- [x] **Go live — meta-refresh redirects removed** — Both entry points restored to live content. (commit 859fe56) — 2026-05-17

---

## 🚨 CRITICAL — Fix immediately

- [x] **Fix resort card click bug** — root cause: buildModalChart used hardcoded indices [0,6,13] assuming 14+ history points; pts[13] undefined with ~9 actual points; fixed with dynamic midIdx/lastIdx (commit 877c0dd). Language violations + diagnostic console.log cleaned up (commit d4c59c6). Tester PASS. — 2026-05-06

---

## Active / Up Next

- [x] **CSV architecture overhaul — separate files per operator** — `_data/price_history.csv` renamed to `_data/prices_clubmed.csv`; placeholder `_data/prices_markwarner.csv` and `_data/prices_sandals.csv` created (headers only); `clubmed_checker.py` updated to write to new path (commit 8236d90) — 2026-05-06
- [x] **`build_site.yml` workflow created** — Dedicated HTML build workflow triggered by changes to any `_data/prices_*.csv` file; runs `--inject-only` to regenerate `clubmed/index.html`; concurrency-queued to prevent overlapping runs (commit 4718bc5) — 2026-05-06
- [x] **HTML generation decoupled from price checker** — Removed HTML commit step from `price_checker.yml` and `clubmed_checker.py`; price checker now touches CSV only; HTML rebuild is fully delegated to `build_site.yml` (commit 711f8c7) — 2026-05-06

- [x] **Data gap backfill** — `backfill_prices.py` built and run: 3,717 rows added for 2026-04-27 to 2026-05-03; backfilled rows marked with `T00:00:00Z` timestamp (vs live data at real UTC times). Run after any future multi-day gap: `python backfill_prices.py && python clubmed_checker.py --inject-only` — 2026-05-04
- [x] **Configure DNS at Squarespace** — 4 × A records + CNAME confirmed configured. DNS resolving to GitHub Pages IPs (185.199.108–111.153). — 2026-05-04
- [x] **GitHub Pages active** — HTTP 200 confirmed from GitHub.com server. Root serves brand landing page; `/clubmed/` serves tracker (373KB). HTTPS cert auto-provisioning (may take a few hours). Once HTTPS is live, go to Settings → Pages → Enforce HTTPS. — 2026-05-04
- [x] **Enforce HTTPS on GitHub Pages** — Once cert is provisioned: go to `https://github.com/215781/booking-window/settings/pages`, tick "Enforce HTTPS". **User action — check in a few hours.** — 2026-05-05
- [x] **Decommission Vercel** — DNS no longer routes to Vercel (points to GitHub Pages). Safe to remove Vercel project. `vercel.json` stays in repo for reference. **User action.** — 2026-05-05
- [x] **Wire up GA4 measurement ID** — `G-G2RES5DX0K` live in both HTML files. CSP updated. — 2026-05-04
- [x] **Confirm `VMOC_WINTER` code** — verified correct in `clubmed_checker.py` and CSV. No space. The session note was erroneous. — 2026-05-04
- [x] **Quality check gate** — `continue-on-error: true` added to quality check step in `price_checker.yml`; check always logs but never blocks data collection (commit d549110). — 2026-05-06
- [x] **Fix remaining Saturday references in `clubmed/index.html`** — All 5 remaining "Saturday" departure references updated to "Sunday": alert form note, How It Works body, modal subtitle, search modal rows label, JS comment (commit 4701ea0) — 2026-05-07
- [x] **Grand Massif + Serre-Chevalier departure_day** — departure_day fixed to Sunday (6) in async rewrite (commit 927784b). — 2026-05-06
- [x] **Resort cards lead with price movement signal** — movementHTML now appears above card-price; format includes % change (e.g. ↓ £438 (−9%) in 14 days). Signal-first layout consistent with booking-intelligence positioning. (commit 34a74c0) — 2026-05-17

### 🔴 HIGH PRIORITY — Agent coordination

- [x] **Write tighter agent git rules** — Added `⚠️ GIT RULES — NON-NEGOTIABLE` section to both BUILDER.md and ORCHESTRATOR.md: check `git branch` before every commit, confirm on `main`, no simultaneous Builder sessions, commit per-task not at session end (commit bc975d1). — 2026-05-06
- [x] **Merge/cherry-pick `claude/nifty-shannon-d10066` to main** — content already on main (commit bb8587b); branch can be deleted. — 2026-05-06

### 🔴 HIGH PRIORITY — Start data collection now (before sites are built)

- [x] **Build Mark Warner price checker** — `markwarner_checker.py` built and verified 2026-05-04. API: POST `/resort/getresortsearchcriteria` with `{resortId: 957, adults, children, childAges, airport: "LGW", duration: 7, checkIn: today}`. Returns `validDates[]` with `pr` (promo total), `prpp` (promo pp), `wp` (was-total), `wppp` (was-pp), room type. 18 departure dates per party size, 3 party sizes = 54 rows/run. Seeded with 54 rows. GitHub Actions at 07:00 UTC daily. Note: `resortId` (957) is embedded in page HTML — update if they redesign. One resort only (Tignes); PLAN.md will note when a MW Tignes tracker page is worth building. — 2026-05-04
- [x] **Mark Warner workflow fix — git pull --rebase** — Added `git pull --rebase` to `markwarner_checker.yml` to prevent push failures on diverged branches (commit a746a74) — 2026-05-06
- [x] **Mark Warner async rewrite** — Full async rewrite using aiohttp + asyncio, Semaphore(8) concurrency, per-resort git commits, 7 rotating User-Agent strings, 429 backoff, push retry with 3-attempt exponential backoff (2s/4s/8s). `fetch_price_async()` replaces synchronous version. `--verify` confirmed £1,658 for 2026-12-06. (commit eaccfd2) — 2026-05-07
- [x] **`markwarner_checker.yml` fix — timeout, aiohttp, CSV path** — timeout 180→60 min, `aiohttp` added to pip install, safety-net commit updated to `_data/prices_markwarner.csv`, HTML commit step removed. (commit 3f10acf) — 2026-05-07
- [ ] **Build Sandals price checker** — GitHub references confirm an "official Sandals booking API" exists but it's not publicly documented — may require a partner relationship. Try reverse-engineering `sandals.co.uk` via DevTools first. Also check for a `/developers` or `/partner` portal. Build `sandals_checker.py` + `_data/sandals_prices.csv`. Add to Actions.
- [ ] **Add both new checkers to GitHub Actions** — Create `.github/workflows/markwarner_checker.yml` and `.github/workflows/sandals_checker.yml` (or extend `price_checker.yml`). Daily at offset times (e.g. 07:00 and 08:00 UTC) to avoid concurrent runs. Commit updated CSVs.

### 🔴 HIGH PRIORITY — Blog / editorial content

- [x] **Set up Jekyll blog infrastructure** — `_posts/` directory created; blog nav link + footer link added to `index.html`. GitHub Pages serves Jekyll natively. (commits ba1a6a0 + e6e1125) — 2026-05-06
- [x] **Blog link added to Club Med page nav and footer** — Blog navigation and footer links added to `clubmed/index.html` (commit 4263be0) — 2026-05-06
- [x] **Departure day copy corrected** — "Saturday" → "Sunday" across `clubmed/index.html` (commit e87cbb2) — 2026-05-06. Note: 3 instances remain — see pending item above.
- [x] **Twitter card meta tags added** — Open Graph / Twitter card `<meta>` tags added to root `index.html`, blog index, and `_layouts/post.html` (commit 2342a16) — 2026-05-06
- [x] **Blog URLs added to sitemap.xml** — Blog index and post URLs added to `sitemap.xml` (commit 7905b02) — 2026-05-06
- [x] **Logo href and JSON-LD WebSite URL corrected** — Logo link href and JSON-LD `WebSite` url property corrected across root and blog pages (commit 6888363) — 2026-05-06
- [x] **Publish first article** — "When to Book a Club Med Ski Holiday: The Price Window Explained" live at `/blog/2026/05/06/when-to-book-club-med-ski-holiday/`. 1,405 words, UK English, JSON-LD schema, links to /clubmed, no banned words. Unapproved draft (`why-timing-matters-when-booking-club-med`) removed (efaedce). (commit 894ee8b) — 2026-05-06
- [x] **Publish article 2** — "Club Med Tignes vs Les Arcs: Which Resort is Worth the Price?" live at `_posts/2026-05-06-club-med-tignes-vs-les-arcs.md`. 1,412 words, UK English, comparison table, JSON-LD schema, links to /clubmed, no banned words. (commit bcde757) — 2026-05-06
- [x] **Publish article 3** — "Is Club Med Ski Worth the Money? An Honest Assessment". Target term: `is Club Med ski worth it`. 1,100 words. Package breakdown vs DIY, timing angle (Jan/March more favourable), CTA to tracker. Internal links to articles 1 and 2. Sitemap updated. (commit 0cf9154) — 2026-05-17
- [ ] **Create CONTENT_WRITER.md agent file** — Write a dedicated agent file for researching and publishing SEO blog posts to `_posts/`. Template: research a keyword → draft → optimise → publish. Target 2 articles per month once blog is set up.

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
- [ ] **Post-launch: schedule Content Writer — 2 blog posts/week via scheduled task** — Once site is live (approx end of May 2026), set up a recurring scheduled agent (via `anthropic-skills:schedule`) to run the Content Writer agent and publish 2 blog posts per week automatically. User decision: 2026-05-06.
- [ ] **Email sequence expansion** — extend Kit welcome sequence from 1 email to 4–6 emails over 2–3 weeks (how Club Med pricing works, resort comparison, what to watch). (MT-4)
- [ ] **Price alert trigger — flash sale notification** — alert subscribers when the annual Club Med early booking flash sale opens (ski ~Feb, summer ~Oct). (MT-5)
- [ ] **Booking-window analysis script** — target Oct 2026 when price_history.csv has 6+ months of data. Group by resort + departure date, plot price vs days_before_departure, find inflection points at 180d, 90d, 60d, 30d, 14d, 7d. (MT-6)

### Future design constraints

- [ ] **Flexible duration support (7 / 10 / 14 nights)** — DESIGN CONSTRAINT for summer resorts and multi-operator expansion. When adding summer Club Med resorts or new operators (Mark Warner, Sandals), the checker must query all relevant durations. The homepage display stays 7-night for comparability, but the raw CSV should capture all durations. Checker config per resort must use a `durations` parameter array (e.g. `durations: [7]` today, `durations: [7, 10, 14]` for summer operators) rather than hardcoding 7. Do not add this to existing winter Club Med checker without user instruction. Noted 2026-05-06.

### Summer resort expansion
- [x] **Phase 1a: Summer data collection infrastructure** — `clubmed_summer_checker.py` built, 9 resort codes confirmed via GraphQL productId probe (May 2026): `GREC` Gregolimano, `MMAC` Magna Marbella, `DBAC` Da Balaia, `CARC` La Caravelle (Corsica), `LAPC` La Palmyre Atlantique, `LPAC` La Palmyre, `PALC` La Palmeraie (Marrakech), `TURC` Palmiye (Turkey), `AGAC` Agadir. GitHub Actions workflow at 07:30 UTC daily. `_data/prices_clubmed_summer.csv` initialised. `--verify` confirmed MMAC £3,918. Note: Cefalù (Sicily) codes not found — all variants returned ARPC_WINTER placeholder. (commits 346d391, effbf4e, 808724b) — 2026-05-12
- [x] **Summer checker: Kani Maldives added + combos crash bug fixed** — `KANC` (Kani, Maldives) confirmed valid via GraphQL productId probe 2026-05-17 and added to RESORTS dict (10 total). Fixed `resort["combos"]` KeyError bug — `_COMBOS` global was never assigned to resort dict; replaced all references in `process_resort` with `_COMBOS` direct (would have crashed on first run). (commit 7fc1677) — 2026-05-17
- [x] **Phase 1b: Summer tracker UI** — Originally launched as `summer/index.html`; consolidated into `/clubmed` with Ski/Summer toggle (see entry below). `--inject-only` added to `clubmed_summer_checker.py`. Root `index.html` and winter nav updated. (commits 1d784e3, d59b799) — 2026-05-17
- [x] **Summer tracker consolidated into /clubmed** — Ski/Summer toggle added to `/clubmed`. `RESORT_DATA_SUMMER` injectable block added. `RESORT_GRADIENTS_SUMMER` dict added. Summer checker now targets `clubmed/index.html` (injects `RESORT_DATA_SUMMER`). `summer/index.html` is now a redirect to `/clubmed`. Root landing page consolidated to a single Club Med card. `sitemap.xml` `/summer/` entry removed. (commit d59b799) — 2026-05-17
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
- [x] TESTER.md QA agent created (commit d651c28) — 2026-05-05
- [x] JS crash fix: guard against resorts with empty departures in `openModal` (commit 668f35c) — 2026-05-05
- [x] Date display fix: dates now "6–13 Dec 2026" format (departure + 7 nights, cross-month handled). Removed stale `w/c` strip from calendar `shortDate`. Commit 7093c2e — 2026-05-05
- [x] LP2C placeholder purge: 328 rows with £3,322 price removed from `price_history.csv`; RESORT_DATA regenerated via `--inject-only` (commit c8df916) — 2026-05-05
- [x] Reverted `clubmed/index.html` to d651c28 after c500fb8 introduced touchstart/touchend regression (broke card clicks, party size tabs, Show Optimal Dates on desktop and mobile) — 2026-05-05
- [x] Blog link added to Club Med page nav and footer (`clubmed/index.html`) — commit 4263be0 — 2026-05-06
- [x] Departure day copy corrected: "Saturday" → "Sunday" in `clubmed/index.html` (partial — 3 instances remain) — commit e87cbb2 — 2026-05-06
- [x] Twitter card meta tags added to root `index.html`, blog index, and `_layouts/post.html` — commit 2342a16 — 2026-05-06
- [x] Blog URLs added to `sitemap.xml` — commit 7905b02 — 2026-05-06
- [x] Logo href and JSON-LD `WebSite` url corrected — commit 6888363 — 2026-05-06
- [x] Mark Warner workflow: `git pull --rebase` added to `markwarner_checker.yml` to prevent diverged-branch push failures — commit a746a74 — 2026-05-06
- [x] Article 2 published: "Club Med Tignes vs Les Arcs: Which Resort is Worth the Price?" — commit bcde757 — 2026-05-06
- [x] Under construction page created: `under-construction.html` — on-brand dark teal, "We're sharpening our data. Back soon.", Kit email signup form — commit 2575e57 — 2026-05-06
- [x] Entry-point redirects added: `index.html` and `clubmed/index.html` meta-refresh to `/under-construction.html`; source files untouched, revert is one line per file — commit 720f853 — 2026-05-06
- [x] **Async rewrite of `clubmed_checker.py`** — aiohttp + asyncio, Semaphore(8) concurrency, per-resort CSV commits, 429 backoff, push retry logic, 7 User-Agent strings. Grand Massif + Serre-Chevalier departure_day fixed to Sunday (6). Estimated runtime: 15–20 min (was 160+). Dry-run confirmed: Tignes £3,648 (commits 927784b + 9c41d58) — 2026-05-06
- [x] **`price_checker.yml` timeout reduced to 60 min** — aiohttp added to pip install step (commit 9c41d58) — 2026-05-06
- [x] **CSV architecture: `price_history.csv` → `prices_clubmed.csv`** — renamed with operator-specific naming convention; placeholder CSVs for Mark Warner and Sandals created (headers only); `clubmed_checker.py` updated (commit 8236d90) — 2026-05-06
- [x] **`build_site.yml` created** — dedicated HTML regeneration workflow triggered by `_data/prices_*.csv` changes; runs `--inject-only`; concurrency-queued (commit 4718bc5) — 2026-05-06
- [x] **HTML generation decoupled from price checker** — price checker writes CSV only; `build_site.yml` owns HTML rebuild; removed HTML commit step from `price_checker.yml` and checker (commit 711f8c7) — 2026-05-06
- [x] **Jekyll Pages build failure fixed** — Root cause: `csv.DictWriter` default `lineterminator='\r\n'` was writing Windows-style CRLF to all `_data/` CSV files; Jekyll's Ruby CSV parser rejects CRLF in unquoted fields. Fix: stripped CRLF from all three `_data/prices_*.csv` files (commit 2558ac4), added `lineterminator='\n'` to `csv.DictWriter` in both `clubmed_checker.py` and `markwarner_checker.py` (commit c2f6020). Pages build confirmed passing. — 2026-05-08
- [x] **Price checker safety net made explicit** — `price_checker.yml` safety net step changed from bare `git pull --rebase` / `git push` to `git pull --rebase origin main` / `git push origin main` to prevent ambiguous-ref failures (commit c2f6020) — 2026-05-08
- [x] **Club Med summer price checker built** — `clubmed_summer_checker.py` (aiohttp/asyncio, Semaphore(8), same architecture as winter checker), `.github/workflows/clubmed_summer_checker.yml` (07:30 UTC daily, 60-min timeout), `_data/prices_clubmed_summer.csv` (header-only placeholder). 9 resort codes confirmed via GraphQL productId probe. `--verify` confirmed £3,918 for MMAC. Cefalù not found — all CEFC/CEFX/etc codes return ARPC_WINTER placeholder. (commits 346d391, effbf4e, 808724b) — 2026-05-12
- [x] **Go live** — Meta-refresh redirects removed from `index.html` and `clubmed/index.html`. Site live at whentobook.co.uk. (commit 859fe56) — 2026-05-17
- [x] **Resort cards lead with price movement signal** — movementHTML moved above card-price; % change added (e.g. ↓ £438 (−9%) in 14 days). Signal-first layout. (commit 34a74c0) — 2026-05-17
- [x] **Article 3 published** — "Is Club Med Ski Worth the Money? An Honest Assessment" at `_posts/2026-05-17-is-club-med-ski-worth-it.md`. ~1,100 words, target `is Club Med ski worth it`, UK English, CTA to /clubmed, internal links to articles 1+2, sitemap updated. (commit 0cf9154) — 2026-05-17
- [x] **Summer checker: Kani (KANC) added + combos crash bug fixed** — KANC confirmed via GraphQL productId probe; added to RESORTS (10 total). Fixed `resort["combos"]` KeyError in `process_resort`. (commit 7fc1677) — 2026-05-17
- [x] **Articles 4–7 published** — Per-resort guides using live price data: Val d'Isère (commit 809f0bf), Tignes + Les Arcs (commit 3a6a5b4), Alpe d'Huez (commit 3f07025). Each ~900–1,100 words, live price tables, seasonal value windows, sitemap updated. Blog now has 7 articles total. — 2026-05-17
- [x] **Summer tracker launched then consolidated** — Initially launched as `summer/index.html` (commit 1d784e3), then consolidated into `/clubmed` with a Ski/Summer toggle (commit d59b799). `RESORT_DATA_SUMMER` injectable block and `RESORT_GRADIENTS_SUMMER` added to `clubmed/index.html`. Summer checker injects into `clubmed/index.html` targeting `RESORT_DATA_SUMMER`. `summer/index.html` now redirects to `/clubmed`. Root landing page consolidated to single Club Med card. `sitemap.xml` `/summer/` entry removed. — 2026-05-17
</content>
</invoke>