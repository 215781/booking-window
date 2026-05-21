# Next Session Prompt — When To Book

**Read this file first at the start of every session, before doing anything else.**
Then read `PLAN.md` for the full task list.

---

## ⚠️ START-OF-SESSION VERIFICATION — DO THIS BEFORE ANYTHING ELSE

Run:
```bash
git merge-base --is-ancestor 86d28c9 HEAD && echo "OK — HEAD is ahead of last recorded state" || echo "MISMATCH — investigate before starting work"
```

Last recorded push: **`86d28c9`** (feat: international ski price checker — 8 resorts)

If the check prints MISMATCH: stop, do not begin work, diagnose what diverged and why.

Note: the verification uses ancestry (`--is-ancestor`) rather than exact match because the Scribe's own documentation commits always advance HEAD past the recorded hash. What matters is that `b63c202` is in the ancestry — meaning all prior work was safely pushed.

---

## Last session (2026-05-21)

**HEAD: 86d28c9** — International ski price checker (8 resorts: Italian Alps, Swiss Alps, Japan, China)

### Commits made this session (newest first):
```
86d28c9  feat: international ski price checker — 8 resorts (Italian Alps, Swiss Alps, Japan, China)
60af5ca  fix: summer inject-only variable name + RESORT_META for 14 new resorts
52ec961  feat: add 14 new summer resorts to summer checker (24 total)
742a5b3  content: add Peisey-Vallandry resort guide
```

### What was done this session:

**Resort expansion — 22 new resorts now tracked in CSV:**

**Summer resorts (14 new — commit 52ec961):** `clubmed_summer_checker.py` expanded from 10 to 24 resorts. New codes confirmed via GraphQL productId probe: Cefalù (CFAC), Opio en Provence (OPIC), Bodrum (BODC), Djerba La Douce (DDOC), Bali (BALC), Phuket (PHUC), Cherating Beach (CHEC), The Finolhu Villas (KANV), La Plantation d'Albion (ALBC), La Pointe aux Canonniers (MAUC), Seychelles (SEYC), Punta Cana (PCAC), Cancún (CANC), Michès Playa Esmeralda (MPEC). RESORT_META region strings added for all new resorts.

**Summer inject-only bug fixed (commit 60af5ca):** `clubmed_summer_checker.py` was generating/searching for `RESORT_DATA_SUMMER` but `clubmed/index.html` uses `SUMMER_RESORT_DATA`. The inject-only step in `build_site.yml` was silently doing nothing for the summer block. Variable name corrected.

**International ski checker (commit 86d28c9):** New `clubmed_ski_international_checker.py` for 8 non-French-Alps ski resorts (all confirmed via GraphQL probe). Separate CSV (`_data/prices_clubmed_ski_international.csv`), separate workflow at 09:00 UTC (no conflict with French Alps 06:00 or summer 07:30). Uses `SKI_INTERNATIONAL_DATA` as JS variable for future HTML injection. Ixtapa Pacific (Mexico) confirmed permanently closed — not tracked.

**Content (commit 742a5b3):** Peisey-Vallandry per-resort guide published to `_posts/`.

**Note:** `clubmed/index.html` has NOT been updated to display international ski resorts or all new summer resorts. The HTML still shows 11 ski + 9 original summer resorts. New resorts are being collected to CSV only. A UI restructure decision is needed before adding them to the display (see Open items).

### What exists on main now (verified):
- `clubmed/index.html` — updated cookie banner, affiliate-ready copy, "Monitoring" badge, iOS zoom fix, dark teal header/footer, hero "Most Favourable" + "Book Now" CTA, 11 ski + 9 summer resorts displayed (all with real photos). New resorts tracked in CSV but not yet displayed.
- `index.html` — cookie consent banner added, updated hero copy, dark teal footer
- `privacy.md` → renders at `/privacy/` via Jekyll (full UK GDPR policy)
- `terms.md` → renders at `/terms/` via Jekyll (terms of use) — footer 404 now resolved
- `_layouts/page.html` — Jekyll page layout for static pages
- `images/` — 11 ski + 9 summer resort images (all Wikimedia CC-licensed)
- `backup_to_gdrive.sh` — daily backup to Google Drive via launchd (03:00 daily)
- `clubmed_checker.py` — French Alps ski checker, 11 resorts, daily 06:00 UTC. PLAC code correct.
- `clubmed_summer_checker.py` — summer beach checker, 24 resorts, daily 07:30 UTC
- `clubmed_ski_international_checker.py` — international ski checker, 8 resorts, daily 09:00 UTC
- `_data/prices_clubmed.csv` — French Alps ski price log (280 corrupt LP2C_WINTER rows present but filtered at query time)
- `_data/prices_clubmed_summer.csv` — summer resort data (24 resorts collecting)
- `_data/prices_clubmed_ski_international.csv` — international ski data (header-only, collecting from 2026-05-21)
- `markwarner/index.html` — Mark Warner tracker live at /markwarner/

### Open items for next session:
- **Site UI restructure needed** — `clubmed/index.html` still only displays 11 French Alps ski + 9 original summer resorts. 14 new summer resorts + 8 international ski resorts tracked in CSV but not yet displayed. Needs regional navigation design decision before HTML work: see PLAN.md backlog item "Site UI restructure — accommodate full resort portfolio".
- `build_site.yml` only rebuilds `clubmed/index.html` — should also handle summer CSV injection when `prices_clubmed_summer.csv` changes. The `build_site.yml` does NOT yet call `clubmed_ski_international_checker.py --inject-only` — not needed until the HTML block is added.
- Review PLAN_V2.md tasks B1–B15 for next priority — especially B6 (hero pull quote), B7 (copy rewrite), B2 (section reorder)
- Review `claude/naughty-noyce-f4276b` branch: "copy: signal-first reframe — lead with £saved/% down" (May 10) — decide whether to merge
- `post.html` footer still links to `/privacy.html` — should be updated to `/privacy/`
- Articles 12–13 still pending: Grand Massif, Serre-Chevalier per-resort guides (Peisey-Vallandry published this session)

---

## Context

**whentobook.co.uk** — Club Med price intelligence site (ski resorts). Built by Drop Media Ltd. Root URL is a brand landing page; Club Med tracker lives at `/clubmed`. Future operators: `/markwarner`, `/sandals` etc.

- **Repo:** `~/booking-window/` / `git@github.com:215781/booking-window.git`
- **Live site:** GitHub Pages — DNS live as of 2026-05-04. HTTP working; HTTPS cert may now be provisioned — check and tick "Enforce HTTPS" in Pages Settings if available.
- **HTML files:** `clubmed/index.html` (Club Med tracker — checker writes here), `index.html` (root brand landing page), `WhentoBook.html` (redirect → /clubmed)
- **Price checker:** `clubmed_checker.py` — runs daily at 06:00 UTC via GitHub Actions, writes to `clubmed/index.html`
- **Mark Warner checker:** `markwarner_checker.py` — runs daily at 07:00 UTC via GitHub Actions, appends to `_data/markwarner_prices.csv`
- **Price history:** `_data/price_history.csv` — ~9,000 rows. Append-only. In `_data/` so GitHub Pages won't serve it publicly.
- **Mark Warner prices:** `_data/markwarner_prices.csv` — 54 rows seeded 2026-05-04. Append-only.
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
clubmed/index.html          — Club Med tracker (canonical live site)
index.html                  — Root brand landing page
WhentoBook.html             — Redirect to /clubmed
clubmed_checker.py          — Price checker (flags: --test, --verify, --inject-only)
markwarner_checker.py       — Mark Warner price checker (flags: --test, --verify)
backfill_prices.py          — Gap-fill script (run after multi-day outage)
_data/price_history.csv     — Club Med price log (~9,000 rows, append-only)
_data/markwarner_prices.csv — Mark Warner price log (54 rows seeded, append-only)
vercel.json                 — Routing + security headers (Vercel only)
.github/workflows/
  price_checker.yml         — Club Med: daily 06:00 UTC
  markwarner_checker.yml    — Mark Warner: daily 07:00 UTC
  backup.yml                — Weekly CSV backup to GitHub Releases (Sundays 02:00 UTC)
When To Book/Agents/        — Agent .md files mirrored to vault (Obsidian)
```
