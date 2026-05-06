# Next Session Prompt — When To Book

**Read this file first at the start of every session, before doing anything else.**
Then read `PLAN.md` for the full task list.

---

## Context

**whentobook.co.uk** — Club Med price intelligence site (ski resorts). Built by Drop Media Ltd. Root URL is a brand landing page; Club Med tracker lives at `/clubmed`. Future operators: `/markwarner`, `/sandals` etc.

**✅ Card click bug RESOLVED (2026-05-06):** buildModalChart used hardcoded indices [0,6,13] which crashed with a silent TypeError when resorts had <14 price history points (~9 actual). Fixed with dynamic midIdx/lastIdx (877c0dd). Language violations ("cheapest" in meta/UI) also cleaned up (d4c59c6).

- **Repo:** `~/booking-window/` / `git@github.com:215781/booking-window.git`
- **Live site:** GitHub Pages — DNS live as of 2026-05-04. HTTPS live and enforced.
- **HTML files:** `clubmed/index.html` (Club Med tracker — checker writes here), `index.html` (root brand landing page), `WhentoBook.html` (redirect → /clubmed)
- **Price checker:** `clubmed_checker.py` — runs daily at 06:00 UTC via GitHub Actions, writes to `clubmed/index.html`
- **Mark Warner checker:** `markwarner_checker.py` — runs daily at 07:00 UTC via GitHub Actions, appends to `_data/markwarner_prices.csv`
- **Price history:** `_data/price_history.csv` — ~9,000 rows (328 LP2C placeholder rows purged 2026-05-05). Append-only. In `_data/` so GitHub Pages won't serve it publicly.
- **Mark Warner prices:** `_data/markwarner_prices.csv` — seeded 2026-05-04, daily runs active. Append-only.
- **Resorts:** 11 French Alps Club Med resorts, all codes verified
- **Signal state:** `DATA_SUFFICIENT = false` — badges show "Building data — check back in autumn". Do not change until autumn 2026.
- **Email:** Kit (ConvertKit) — Booking Alert form `7f784a323c`, Search popup form `f197f8f414`. Welcome sequence live.
- **Email alerts:** `clubmed_checker.py` only emails on genuine failures (>30% API error rate). All other alerts removed.
- **GA4:** `G-G2RES5DX0K` — live in both `clubmed/index.html` and `index.html`.
- **SSH key:** `~/.ssh/booking_window_deploy`
- **Checker flags:** `--test` (no writes), `--verify` (one API call), `--inject-only` (rebuild RESORT_DATA from CSV, no API calls)
- **Date format:** Resort dates display as "6–13 Dec 2026" (departure + 7 nights, cross-month handled: "27 Dec–3 Jan 2027"). Fixed 2026-05-05.
- **Branch `claude/nifty-shannon-d10066`:** Content (DATA_ANALYST.md, AGENT_LOG.md, data_quality_check.py) already on main (bb8587b). Branch can be deleted.

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
- 2026-05-05 — Reverted `clubmed/index.html` to d651c28 (working state). c500fb8 introduced touchstart/touchend handlers with `e.preventDefault()` that broke resort card clicks, party size tabs, and Show Optimal Dates button on both desktop and mobile.
- 2026-05-05 — JS crash fix: guard against resorts with empty departures in `openModal` (commit 668f35c).
- 2026-05-05 — Date display fix: removed stale `w/c` strip; dates now show as "6–13 Dec 2026" (departure + 7 nights, cross-month handled). Commit 7093c2e.
- 2026-05-05 — LP2C placeholder purge: 328 rows with £3,322 price removed from `price_history.csv`. Commit c8df916.
- 2026-05-05 — RESORT_DATA regenerated via `--inject-only`; La Plagne correctly shows no data.
- 2026-05-05 — TESTER.md QA agent created (commit d651c28). Verifies each Builder task.
- 2026-05-05 — DATA_ANALYST.md, AGENT_LOG.md, data_quality_check.py created — **on branch `claude/nifty-shannon-d10066`, NOT merged to main**. Review/merge before using.
- 2026-05-05 — Agent team coordination issues identified: simultaneous sessions cause git lock contention; Builder committed to worktree branch not main; sessions ran 150+ turns without committing.
- 2026-05-05 — HTTPS enforced on GitHub Pages
- 2026-05-05 — Vercel project decommissioned; DNS routes exclusively to GitHub Pages
- 2026-05-05 — Resort card click bug confirmed fixed: buildModalChart hardcoded indices [0,6,13] caused silent TypeError when pts had <14 entries; fixed with dynamic midIdx/lastIdx (877c0dd). Tester PASS.
- 2026-05-05 — Language rule violations fixed: "cheapest" removed from all 3 meta tags, search modal label, JS results label, modal narrative. console.log diagnostic removed. (d4c59c6)
- 2026-05-05 — AGENT_LOG.md Data Analyst health check entry committed (d4c59c6)
- 2026-05-06 — Resort card click bug confirmed fixed: buildModalChart hardcoded indices [0,6,13] caused silent TypeError; fixed with dynamic midIdx/lastIdx (877c0dd). Tester PASS.
- 2026-05-06 — Language rule violations fixed: "cheapest" removed from all 3 meta tags, search modal UI, JS results label, modal narrative; console.log diagnostic removed (d4c59c6)
- 2026-05-06 — AGENT_LOG.md Data Analyst health check entry committed (d4c59c6); nifty-shannon branch content confirmed already on main
- 2026-05-06 — Quality check gate fixed: `continue-on-error: true` added to data_quality_check.py step in price_checker.yml; check always logs but never blocks data collection (d549110)
- 2026-05-06 — Agent git rules tightened: `⚠️ GIT RULES — NON-NEGOTIABLE` section added to BUILDER.md and ORCHESTRATOR.md; check `git branch` before every commit, no simultaneous Builder sessions, commit per-task (bc975d1)
- 2026-05-06 — **Jekyll blog infrastructure set up:** `_posts/` directory created; blog nav link + footer link added to `index.html` (ba1a6a0)
- 2026-05-06 — **First blog article published:** "The £1,600 lesson: why when you book a Club Med ski holiday changes the price more than where you stay" live at `/blog/2026/05/06/why-timing-matters-when-booking-club-med/` (e6e1125)

---

## Up Next (priority order)

### Data health — monitor
1. **Investigate data staleness** — Data Analyst health check found data 44h old at session start (2026-05-06). Check GitHub Actions run log for the 06:00 UTC run on 2026-05-05 and 2026-05-06.
2. **Monitor VDIC_WINTER price swings** — 108% overnight jump (£10,430→£21,678) flagged by Data Analyst. Could be legitimate new bookings opening or API noise. Monitor 2–3 more days before acting.

### 🔴 HIGH PRIORITY — Data collection
3. **Build Sandals price checker** — Reverse-engineer `sandals.co.uk` API via DevTools. Build `sandals_checker.py` + `_data/sandals_prices.csv`. Add to Actions at 08:00 UTC.

### Blog / editorial content
4. **Publish articles 2 and 3** — Blog infra done (e6e1125); `_posts/` is live. Write "Club Med Tignes vs Les Arcs: Which Resort is Worth the Price?" and "Is Club Med Ski Worth the Money?". Full briefs in the Blog article ideas section below.
5. **Create CONTENT_WRITER.md agent file** — agent for researching and publishing SEO posts to `_posts/`.

### Cleanup
6. **Delete branch `claude/nifty-shannon-d10066`** — content already on main; branch is stale.
7. **Grand Massif + Serre-Chevalier departure day** — needs 4+ weeks of data; revisit late May 2026.

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

| Resort | Code | Departure |
|---|---|---|
| Tignes | `TIGC_WINTER` | Sunday |
| Les Arcs Panorama | `ARPC_WINTER` | Sunday |
| Peisey-Vallandry | `PVAC_WINTER` | Sunday |
| Valmorel | `VMOC_WINTER` | Sunday |
| Alpe d'Huez | `ALHC_WINTER` | Sunday |
| La Rosière | `LROC_WINTER` | Sunday |
| La Plagne 2100 | `LP2C_WINTER` | Sunday |
| Val d'Isère | `VDIC_WINTER` | Sunday |
| Grand Massif | `GMAC_WINTER` | TBC |
| Val Thorens Sensations | `VTHC` | Sunday (no `_WINTER` suffix) |
| Serre-Chevalier | `SECC_WINTER` | TBC |

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
_data/markwarner_prices.csv — Mark Warner price log (seeded, append-only)
vercel.json                 — Routing + security headers (Vercel only)
.github/workflows/
  price_checker.yml         — Club Med: daily 06:00 UTC
  markwarner_checker.yml    — Mark Warner: daily 07:00 UTC
  backup.yml                — Weekly CSV backup to GitHub Releases (Sundays 02:00 UTC)
When To Book/Agents/        — Agent .md files mirrored to vault (Obsidian)
TESTER.md                   — QA agent: verifies each Builder task
BUILDER.md                  — Builder agent: implements code, commits to main
ORCHESTRATOR.md             — Orchestrator: plans, delegates, verifies
SCRIBE.md                   — Scribe: documentation only

DATA_ANALYST.md             — Data Analyst agent: placeholder detection, quality scoring 0–100
AGENT_LOG.md                — Inter-agent communication log (Orchestrator reads at session start)
data_quality_check.py       — Reads price_history.csv, detects CRITICAL/WARNING/INFO, appends to AGENT_LOG.md
```

Note: `claude/nifty-shannon-d10066` branch content is now on main (bb8587b). Branch can be deleted.
