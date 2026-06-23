# Next Session Prompt — When To Book

**Read this file first at the start of every session, before doing anything else.**
Then read `PLAN.md` for the full task list.

---

## ⚠️ START-OF-SESSION VERIFICATION — DO THIS BEFORE ANYTHING ELSE

Run:
```bash
git merge-base --is-ancestor 577bcf9 HEAD && echo "OK — HEAD is ahead of last recorded state" || echo "MISMATCH — investigate before starting work"
```

Last recorded push: **`577bcf9`** (Auto-merge claude/inspiring-borg-f6fda0 to main — stub price fix)

If the check prints MISMATCH: stop, do not begin work, diagnose what diverged and why.

Note: the verification uses ancestry (`--is-ancestor`) rather than exact match because the Scribe's own documentation commits always advance HEAD past the recorded hash. What matters is that `577bcf9` is in the ancestry — meaning all prior work was safely pushed.

---

## Last session (2026-06-23)

**HEAD: 577bcf9** — Auto-merge claude/inspiring-borg-f6fda0 to main (stub price fix)

### Commits made this session (newest first):
```
577bcf9  Auto-merge claude/inspiring-borg-f6fda0 to main [skip ci]
ee1ea4e  fix: replace stub prices with real API data in articles
```

### What was done this session (2026-06-23):

**Critical data accuracy fix — stub prices replaced in 4 articles:**

Root cause: LP2C_WINTER was the wrong resort code for La Plagne 2100. All prices under that code were test stubs (£2,874 for 2A, £3,322 for other party sizes) showing identical values across every departure date — no seasonal variation. Real resort code is PLAC, tracking since 1 June 2026.

Real PLAC prices (2A, 7-night, as of 22 June 2026):
- Range: £3,054 (Apr 11, late season) to £5,466 (Dec 27, New Year)
- Christmas Dec 20: £4,620 — genuine seasonal premium
- Feb half-term: £4,930–£4,976
- New Year Dec 27: £5,466 — season peak

Articles fixed (commit ee1ea4e):
1. `_posts/2026-06-22-club-med-val-disere-vs-la-plagne.md` — complete rewrite of La Plagne sections; removed false "no Christmas spikes / flat pricing" claims; added accurate price comparison table; updated VDIC New Year week price (£13,608→£8,816 following recent market movement); included correct PLAC price range.
2. `_posts/2026-05-23-best-time-to-book-club-med-la-plagne.md` — replaced all LP2C stub prices with real PLAC data; corrected resort code LP2C_WINTER→PLAC; corrected duration 6-night→7-night; added full season price table with 18 departure dates; added update notice.
3. `_posts/2026-03-11-best-time-to-book-club-med-les-arcs.md` — updated stale Dec 27 New Year price (£7,304→£6,642, price moved Jun 8); updated VDIC comparison price (£13,608→£8,816).
4. `_posts/2026-05-19-club-med-ski-holiday-2027-prices.md` — noted VDIC New Year price movement since publication (£13,608→£8,816); corrected Les Arcs Apr 18 price at time of writing (£3,322→£2,874).

**Data verification findings:**
- LP2C had 1,563 rows in CSV, 280 with actual prices (all stubs). These rows remain in CSV (append-only) but are filtered from analysis by `resort_code` filter.
- PLAC has 3,696 rows, all with real prices showing seasonal variation. Data collection confirmed since Jun 1.
- Les Arcs £2,874 (Apr 18 departure) IS real ARPC data — price was £2,874 May 7–Jun 7, then moved to £3,322 by Jun 22. Not a stub.
- VDIC Dec 27 (New Year): moved from £13,608 to £8,816 between Jun 19 and Jun 22 — large downward correction captured.

**Previous session (2026-06-22):**
Mark Warner summer beach checker launched (see commit history).

### What exists on main now (verified):
- `clubmed/index.html` — invariants confirmed: `RESORT_IMAGES` ×2, `renderHeroBestCard` ×4
- `markwarner_summer_checker.py` — live, seeded, running daily at 06:30 UTC
- `_data/prices_markwarner_summer.csv` — growing daily (seeded 1,198 rows 2026-06-22)
- `_data/prices_markwarner.csv` — ski data, checker dormant until Aug/Sep
- Blog: 13+ articles live (including corrected La Plagne and comparison articles)
- `_data/prices_clubmed.csv` — ~120,000+ rows (119K+ as of Jun 23), automated daily collection ongoing
- `_data/prices_clubmed.csv` contains 1,563 LP2C_WINTER rows (stubs) and 3,696 PLAC rows (real) — the LP2C rows are inert (filtered by resort_code param in checker)

### Open items for next session:
- **Articles 12–13 pending**: Grand Massif, Serre-Chevalier per-resort guides
- **Site UI restructure** — 11 ski + 9 summer resorts displayed; 14 new summer + 8 international ski tracked in CSV only. Needs design decision. MW summer data is now accumulating — should eventually power a /markwarner tracker page.
- Review PLAN_V2.md tasks B1–B15 — especially B6 (hero pull quote), B7 (copy rewrite), B2 (section reorder)
- `post.html` footer still links to `/privacy.html` — should be `/privacy/`
- **Note on LP2C stubs in CSV**: The 1,563 LP2C_WINTER rows are append-only and remain in CSV. They are correctly filtered during inject-only runs. Do not delete them. Future content writers: always filter to `resort_code == "PLAC"` when analysing La Plagne data, exclude rows where price is blank or 2874/3322 (known stubs).

---

## Context

**whentobook.co.uk** — Club Med price intelligence site (ski resorts). Built by Drop Media Ltd. Root URL is a brand landing page; Club Med tracker lives at `/clubmed`. Future operators: `/markwarner`, `/sandals` etc.

- **Repo:** `~/booking-window/` / `git@github.com:215781/booking-window.git`
- **Live site:** GitHub Pages — DNS live as of 2026-05-04. HTTP working; HTTPS cert may now be provisioned — check and tick "Enforce HTTPS" in Pages Settings if available.
- **HTML files:** `clubmed/index.html` (Club Med tracker — checker writes here), `index.html` (root brand landing page), `WhentoBook.html` (redirect → /clubmed)
- **Price checker:** `clubmed_checker.py` — runs daily at 06:00 UTC via GitHub Actions, writes to `clubmed/index.html`
- **Mark Warner ski checker:** `markwarner_checker.py` — runs daily at 07:00 UTC, appends to `_data/prices_markwarner.csv`. Dormant in summer (0 ski dates May–Aug) — resumes ~Aug/Sep 2026.
- **Mark Warner summer checker:** `markwarner_summer_checker.py` — runs daily at 06:30 UTC, appends to `_data/prices_markwarner_summer.csv`. 4 beach resorts: Aeolian Village (26928), Lemnos (8), Paleros (19300), Phokaia (16797). Seeded 2026-06-22 (1,198 rows).
- **Price history:** `_data/prices_clubmed.csv` — append-only. In `_data/` so GitHub Pages won't serve it publicly. (Note: was incorrectly writing to `price_history.csv` until async rewrite fixed this on 2026-05-31.)
- **Mark Warner ski prices:** `_data/prices_markwarner.csv` — 400+ rows seeded 2026-05-07. Append-only. (Legacy file `markwarner_prices.csv` also exists — old schema, ignore.)
- **Mark Warner summer prices:** `_data/prices_markwarner_summer.csv` — 1,198 rows seeded 2026-06-22. Append-only.
- **Resorts:** 11 French Alps Club Med resorts, all codes verified
- **Signal state:** `DATA_SUFFICIENT = false` — badges show "Building data — check back in autumn". Do not change until autumn 2026.
- **Email:** Kit (ConvertKit) — Booking Alert form `7f784a323c`, Search popup form `f197f8f414`. Welcome sequence live.
- **Email alerts:** `clubmed_checker.py` only emails on genuine failures (>30% API error rate). All other alerts removed.
- **GA4:** `G-G2RES5DX0K` — live in both `clubmed/index.html` and `index.html`.
- **SSH key:** `~/.ssh/booking_window_deploy`
- **Checker flags:** `--test` (no writes), `--verify` (one API call), `--inject-only` (rebuild RESORT_DATA from CSV, no API calls)

Why prices are mostly empty: Club Med UK hasn't opened winter 2026/27 bookings fully yet. Booking window typically opens June/July 2026. Not a bug.

---

## Completed (full history)

- 2026-04-21 — Built single-file HTML/CSS/JS site
- 2026-04-21 — Python price checker built and verified
- 2026-04-21 — GitHub Actions workflow set up
- 2026-04-21 — All 6 original resort codes verified via GraphQL API
- 2026-04-22 — CNAME committed; SSH deploy key generated
- 2026-04-26 — Expanded to 11 resorts; all codes verified
- 2026-04-26 — Scheduled checker live — daily at 06:00 UTC
- 2026-04-26 — Signal system, three-mode date search, modal search, mobile layout, child age input
- 2026-04-26 — Cookie notice and `privacy.html` live
- 2026-04-26 — Season price calendar view in resort modal
- 2026-04-28 — `price_history.csv` at ~5,862 rows; 2,205 junk rows purged
- 2026-04-28 — Vercel deployment fixed
- 2026-04-28 — Kit forms configured, welcome sequence live
- 2026-05-04 — Multi-agent workflow: CLAUDE.md, ORCHESTRATOR.md, BUILDER.md, SCRIBE.md, PLAN.md
- 2026-05-04 — price_history.csv moved to `_data/` (hidden from Pages/Vercel)
- 2026-05-04 — Strategic planning: IMPROVEMENT_PLAN.md created
- 2026-05-04 — Agent .md files mirrored to vault at `When To Book/Agents/`
- 2026-05-04 — **URL restructure:** `clubmed/index.html` created; root `index.html` brand landing page built; checker + workflow + vercel.json + sitemap updated; `WhentoBook.html` → redirect
- 2026-05-04 — Deep-link CTAs verified — all `bookingUrl` already resort-specific
- 2026-05-04 — Data purge: 612 suspect LP2C/VDIC rows (Apr 23–25) removed; RESORT_DATA regenerated
- 2026-05-04 — `--inject-only` flag added to checker; `VMOC_WINTER` verified correct
- 2026-05-04 — `backfill_prices.py` built and run: 3,717 rows for Apr 27–May 3
- 2026-05-04 — Security review: `escapeHtml()` added; `BookingWindow_v1_2.html` removed; security headers in `vercel.json`; CSP meta tag in both HTML files
- 2026-05-04 — Data backup: `.github/workflows/backup.yml` — weekly GitHub Releases backup
- 2026-05-04 — DNS live (GitHub Pages IPs confirmed); GitHub Pages serving on HTTP
- 2026-05-04 — JSON-LD schema markup added to `clubmed/index.html` and `index.html`
- 2026-05-04 — OG image PNG created (1200×630). Both HTML files updated.
- 2026-05-04 — **GA4 wired up:** `G-G2RES5DX0K` live in both HTML files. CSP updated on root `index.html`.
- 2026-05-04 — **CLAUDE.md updated:** GA4 ID, planned MW/Sandals checkers, og-image.png, IMPROVEMENT_PLAN.md
- 2026-05-04 — **Mark Warner checker built and verified:** `markwarner_checker.py` uses POST `/resort/getresortsearchcriteria` API (resortId 957, LGW, 7 nights). Returns all 18 departure dates per party size in one call. 3 party sizes = 54 rows/run. Seeded. GitHub Actions at 07:00 UTC daily.
- 2026-05-04 — **Email alerts stripped:** `clubmed_checker.py` only emails on >30% API error rate. All signal/price-change/success emails removed.
- 2026-05-04 — **Blog promoted to high priority** in PLAN.md. 3 article ideas generated (see below).
- 2026-05-04 — **5 fixes applied:** (1) `markwarner_prices.csv` header corrected to 15-column schema; (2) `bookingUrl` added to all 11 Club Med resorts in `clubmed_checker.py` + emitted into JS; (3) 5 occurrences of "cheapest" replaced in `clubmed/index.html` (meta tags → "most favourable pricing", sort labels → "lowest price first"); (4) Mobile touch fixes: `touch-action: manipulation` on all interactive elements, `-webkit-overflow-scrolling: touch` on modals, party-size filter selector scoped to `[data-party]`; (5) Sort bar added below party size tabs — Lowest price first / Highest price first / Biggest price drop.
- 2026-05-20 — **4 copy/UX fixes:** How It Works section removed from tracker + added to about.md; 'in 14 days' qualifier removed from movement badges; Saturday departures note removed from alert form; modal chart crash fixed (dynamic midIdx/lastIdx). (commit 7e2efe8)
- 2026-05-20 — **La Plagne 2100 resort code fixed LP2C_WINTER → PLAC:** LP2C_WINTER silently fell back to ARPC_WINTER (Les Arcs) in Club Med API; 280 corrupt rows in CSV since May 7. PLAC confirmed correct (year-round /y, 7-night only, season opens Dec 13 2026). Per-resort `durations` override added to `make_windows`. Stale-code filter (`resort_code` param) added to `load_price_history_from_csv`. CLAUDE.md resorts table corrected. (commit 6a9e323, merged 168c5ad)
- 2026-05-20 — **Daily Google Drive backup:** `backup_to_gdrive.sh` + `co.whentobook.backup.plist` (launchd, 03:00 daily). Backs up `_data/`, `clubmed/index.html`, `_posts/`, `_layouts/`, `.github/`, `*.py`, and key `.md` files → `WhenToBook_Backups/YYYY-MM-DD/` in Google Drive for Desktop sync. First backup confirmed successful. `.gitignore` created (excludes `backup.log`). (commits 9acc37e, merged 79eab59)
- 2026-05-20 — **Kit.com form bug fix:** Both email signup forms were posting JSON to the Kit.com public form endpoint, which silently accepted the wrong Content-Type and returned 200 without creating a subscriber. Fixed to `application/x-www-form-urlencoded` + `URLSearchParams`. Affects search popup (`f197f8f414`) and mobile booking alert (`7f784a323c`). (commits e009b51, merged fe8e411)
- 2026-05-21 — **Hero label + CTA:** "Best available price" → "Most Favourable"; "View price history →" button → "Book Now →" anchor linking to `resort.bookingUrl`. (commit c07fa97)
- 2026-05-21 — **Price movement guard:** `getPriceMovement()` returns 0 when price is missing/zero — prevents any `-£X` display for unavailable departures. (commit c07fa97)
- 2026-05-21 — **Footer redesign:** Both `clubmed/index.html` and `index.html` — dark teal background, white text, copyright WhenToBook, contact email, Privacy Policy, Terms of Use links, tagline. (commit c07fa97)
- 2026-05-20 — **Summer resort images:** 9 Wikimedia Commons CC-licensed photos added to `images/` for all summer resorts. `RESORT_IMAGES` in `clubmed/index.html` wired up so summer cards display real photos instead of gradient placeholders. (commit 6fd54b8)
- 2026-05-21 — **Booking URLs corrected (all 15):** All ski + summer `bookingUrl` values fixed — correct Club Med slugs and /y vs /w suffixes for year-round resorts. Fallback URL in modal and JS fixed. Search modal now uses resort-specific `bookingUrl` from entries. (commit c5cd8dc)
- 2026-05-21 — **Mobile resort modal table overflow fixed:** Departure table wrapped in scrollable div (`dept-table-wrap`). Book column hidden on mobile via `@media max-width: 600px` — `.modal-cta` button handles booking on mobile. (commit c5cd8dc)
- 2026-05-21 — **Peisey-Vallandry resort guide published** — per-resort blog post added to `_posts/`. (commit 742a5b3)
- 2026-05-21 — **14 new summer resorts added to checker** — `clubmed_summer_checker.py` now 24 resorts. Summer inject-only bug fixed (RESORT_DATA_SUMMER→SUMMER_RESORT_DATA). RESORT_META region strings for all new resorts. (commits 52ec961, 60af5ca)
- 2026-05-21 — **International ski checker launched** — `clubmed_ski_international_checker.py` for 8 resorts (Pragelato Sestriere, St. Moritz, 3 × Japan, 2 × China). Separate CSV + 09:00 UTC workflow. Ixtapa Pacific confirmed permanently closed. (commit 86d28c9)
- 2026-05-31 — **Three rendering bugs fixed** — (1) Hero card blank: crash in `renderCards` when 4 resorts had empty `departures[]` prevented `renderHeroBestCard()` from running — fixed with `if (!dep) return` guard + null-check in `getPriceMovement`. (2) Sparkline invisible for stable prices: flat line was placed at bottom of chart (range=0 → fallback of 1 caused y≈bottom) — fixed to render at h/2 midpoint. (3) RESORT_DATA stale: regenerated with resort_code filter (excludes LP2C_WINTER contamination). All resorts now have 8 combos. (commit 9bc85d7)
- 2026-05-31 — **Winter checker async rewrite** — Root cause of 12-day data gap found and fixed: `CSV_FILE` was `price_history.csv` instead of `prices_clubmed.csv`. Full async aiohttp rewrite (~20 min vs 5+ hours). Per-resort commit+push. Two dead summer resorts disabled (AGAC, BALC). inject-only LP2C_WINTER filter added. (commit 704473f)
- 2026-06-22 — **build_site.yml daily cron added** — GITHUB_TOKEN pushes don't trigger on:push; added 08:00 UTC cron so site rebuilds daily regardless. (commit 880cc5d)
- 2026-06-22 — **Mark Warner summer beach checker launched** — `markwarner_summer_checker.py` tracks 4 beach resorts: Aeolian Village (Lesvos, ID 26928), Lemnos (ID 8), Paleros (ID 19300), Phokaia/Turkey (ID 16797). 7+14 night durations, 3 party sizes, all available airports per resort. ~1,200 rows/day. Separate CSV `_data/prices_markwarner_summer.csv`. Cron 06:30 UTC. Seeded 2026-06-22. Resort IDs found via `:resort-id` HTML attr (not nav hash IDs). (commit f545b5d)
- 2026-06-23 — **Stub price fix in 4 articles** — LP2C_WINTER stubs (£2,874/£3,322 flat across all dates) replaced with real PLAC data (£3,054–£5,466 with genuine seasonal curve). Val d'Isère vs La Plagne article rewritten; La Plagne best-time article rewritten with correct resort code PLAC, 7-night durations, full season price table; Les Arcs article updated with current New Year price (£6,642); ski holiday prices article updated with VDIC New Year movement. (commit ee1ea4e)

---

## Up Next (priority order)

### User actions required first
1. **Enforce HTTPS on GitHub Pages** — cert may now be provisioned. Go to `https://github.com/215781/booking-window/settings/pages`, tick "Enforce HTTPS".
2. **Decommission Vercel** — DNS no longer routes there. Safe to delete the Vercel project.

### Autonomous (next session)
3. **🔴 Build Jekyll blog infrastructure** — Create `_posts/` dir, `_layouts/post.html` (matching `#f5f0e8`/`#1a4a42` design), `blog/index.html` listing page. GitHub Pages supports Jekyll natively. Then publish the first article (idea #1 below).
4. **🔴 Research Sandals pricing API** — Open `sandals.co.uk` in a browser, use DevTools Network tab to capture XHR/Fetch calls when searching for holidays. Or use WebFetch to inspect page structure first. Build `sandals_checker.py` + `_data/sandals_prices.csv`. Add to Actions at 08:00 UTC.
5. **Content article #1** — See article idea #1 below. Publish to `_posts/2026-05-XX-when-to-book-club-med-ski.md` after blog is set up.
6. **Grand Massif + Serre-Chevalier departure day** — Let data accumulate; revisit when 4+ weeks available (target: late May 2026).
7. **Run backfill after any future gap** — `python backfill_prices.py && python clubmed_checker.py --inject-only`

---

## Blog article ideas (generated 2026-05-04)

### Article 1 — Quick win, publish first
**Title:** When to Book a Club Med Ski Holiday: The Price Window Explained
**Target term:** `when to book Club Med ski holiday`
**Covers:** How the Club Med booking window actually opens (typically June/July for the following winter), early-bird vs late availability pricing, the February flash sale moment. Uses site tracking data as evidence. CTA to booking alert signup.
**Why:** High-intent informational search. Direct match to the site's core promise.

### Article 2 — Comparison, earns links
**Title:** Club Med Tignes vs Les Arcs: Which Resort is Worth the Price?
**Target term:** `Club Med Tignes vs Les Arcs`
**Covers:** Side-by-side on altitude, terrain, who each suits. Price angle: "Tignes tends to run 8–12% higher than Les Arcs for the same week." Includes comparison table. Links to tracker for live data.
**Why:** Comparison searches have strong commercial intent. Tables often earn featured snippets. Natural backlink magnet for ski forums and parenting blogs.

### Article 3 — Purchase-intent, bottom of funnel
**Title:** Is Club Med Ski Worth the Money? What You Get (And When to Get It Cheaper)
**Target term:** `is Club Med ski worth it`
**Covers:** Full package breakdown vs DIY (lift pass, ski school, meals, childcare, entertainment). Honest value assessment. "Cheaper" angle: January and early March tend to be more favourable than Christmas/half term. CTA to tracker.
**Why:** "Worth the money" searches are at the final decision stage. Strong candidate for People Also Ask boxes. Exactly the audience: financially savvy families who want to feel confident.

---

## Mark Warner API reference (for future sessions)

```
POST https://www.markwarner.co.uk/resort/getresortsearchcriteria
Content-Type: application/json

{
  "resortId": 957,        # Chalet Hotel L'Écrin, Tignes
  "adults": 2,
  "children": 0,
  "infants": 0,
  "childAges": [],
  "infantAges": [],
  "airport": "LGW",
  "duration": 7,
  "checkIn": "2026-12-06",  # any date — response returns all season dates
  "adultNames": [],
  "childNames": [],
  "infantNames": []
}

Response: { success: true, model: { cacheKey, validDates: [{ d, pr, prpp, wp, wppp, u, pc, pb }] } }
  d = departure date, pr = promo total, prpp = promo pp, wp = was-total, wppp = was-pp
  u = room type string, pc = promo code, pb = promo benefit
```

Note: `resortId` (957) is embedded in the page HTML (`resort[_-]?id` regex). Update if site redesigns.

---

## Resort reference

### French Alps ski (11 — displayed in clubmed/index.html)

| Resort | Code | Departure |
|---|---|---|
| Tignes | `TIGC_WINTER` | Sunday |
| Les Arcs Panorama | `ARPC_WINTER` | Sunday |
| Peisey-Vallandry | `PVAC_WINTER` | Sunday |
| Valmorel | `VMOC_WINTER` | Sunday |
| Alpe d'Huez | `ALHC_WINTER` | Sunday |
| La Rosière | `LROC_WINTER` | Sunday |
| La Plagne 2100 | `PLAC` | Sunday (year-round /y, 7-night only) |
| Val d'Isère | `VDIC_WINTER` | Sunday |
| Grand Massif | `GMAC_WINTER` | TBC |
| Val Thorens Sensations | `VTHC` | Sunday (no `_WINTER` suffix) |
| Serre-Chevalier | `SECC_WINTER` | TBC |

### International ski (8 — CSV only, not yet displayed)

| Resort | Code | Region |
|---|---|---|
| Pragelato Sestriere | `PRAC_WINTER` | Italian Alps |
| St. Moritz Roi Soleil | `SMRC` | Swiss Alps (no `_WINTER` suffix) |
| Tomamu Hokkaido | `TOMC_WINTER` | Japan |
| Kiroro Peak | `KIPC_WINTER` | Japan |
| Kiroro Grand | `KIGC_WINTER` | Japan |
| Sahoro Hokkaido | `SAOC_WINTER` | Japan |
| Beidahu | `BEIC_WINTER` | China |
| Changbaishan | `CBAC_WINTER` | China |

---

## Kit reference

| Form | ID |
|---|---|
| Booking Alert (bottom of page) | `7f784a323c` |
| Search Results popup | `f197f8f414` |

- Custom field: `resort_interest` (text)
- Tags: `booking-alert`, `search-popup` (applied by Kit Rules)
- Welcome sequence: live

---

## Design rules (locked)

- Background `#f5f0e8` · Primary `#1a4a42` · Fonts: Playfair Display + Inter
- Never use: deals, discounts, cheap, vouchers, savings
- Always use: booking intelligence, optimal timing, historically favourable pricing
- `DATA_SUFFICIENT = false` — do not change until autumn 2026

---

## Security

- No Kit API key in the repo — public endpoints only
- GitHub secrets for email alerts: `GMAIL_ADDRESS`, `GMAIL_APP_PASS`, `ALERT_TO`
- SSH deploy key: `~/.ssh/booking_window_deploy`
- CSP meta tag in both HTML files (GitHub Pages doesn't support HTTP headers)
- Weekly backup: `.github/workflows/backup.yml` → GitHub Releases every Sunday

---

## Key files quick reference

```
clubmed/index.html                     — Club Med tracker (canonical live site)
index.html                             — Root brand landing page
WhentoBook.html                        — Redirect to /clubmed
clubmed_checker.py                     — Price checker (flags: --test, --verify, --inject-only)
markwarner_checker.py                  — Mark Warner ski checker (flags: --test, --verify); dormant May–Aug
markwarner_summer_checker.py           — Mark Warner summer beach checker (flags: --test, --verify)
backfill_prices.py                     — Gap-fill script (run after multi-day outage)
_data/prices_clubmed.csv               — Club Med price log (~27,000 rows, append-only)
_data/prices_markwarner.csv            — Mark Warner ski price log (append-only)
_data/prices_markwarner_summer.csv     — Mark Warner summer price log (1,198 rows seeded 2026-06-22, append-only)
vercel.json                 — Routing + security headers (Vercel only)
.github/workflows/
  price_checker.yml         — Club Med: daily 06:00 UTC
  markwarner_checker.yml    — Mark Warner: daily 07:00 UTC
  backup.yml                — Weekly CSV backup to GitHub Releases (Sundays 02:00 UTC)
When To Book/Agents/        — Agent .md files mirrored to vault (Obsidian)
```
