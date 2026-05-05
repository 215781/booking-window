# Next Session Prompt — When To Book

**Read this file first at the start of every session, before doing anything else.**
Then read `PLAN.md` for the full task list.

---

## Context

**whentobook.co.uk** — Club Med price intelligence site (ski resorts). Built by Drop Media Ltd. Root URL is a brand landing page; Club Med tracker lives at `/clubmed`. Future operators: `/markwarner`, `/sandals` etc.

**⚠️ CRITICAL BUG (as of 2026-05-05, unresolved):** Resort cards do not open when clicked. `openModal` is defined and the click handler is attached, but calling `openModal` produces NO output — an `alert()` placed at the top of `openModal` was never triggered during debug. Either: (a) the click event never reaches `openModal`, or (b) a JS error throws before the alert line. Suspected: `DATA_SUFFICIENT = false` may be gating handler attachment inside `renderCards`. Fix this before any other autonomous work.

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
- **Unmerged branch:** `claude/nifty-shannon-d10066` — contains DATA_ANALYST.md, AGENT_LOG.md, data_quality_check.py, updated ORCHESTRATOR.md. Created during 2026-05-05 session but NOT merged to main. Review/merge or re-create on main before using these agents.

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

---

## Up Next (priority order)

### 🚨 CRITICAL — Fix first, block everything else
1. **Fix resort card click bug** — Resort cards do not open when clicked. Known facts: click handler IS attached; `openModal` IS defined; `alert()` at top of `openModal` produced NO alert when card clicked. Either: (a) the click event never reaches `openModal`, or (b) a JS error fires before the alert. Start by inspecting `renderCards` — check if `DATA_SUFFICIENT = false` is preventing handler attachment. Then open DevTools console on the live site and click a card to catch any JS errors.

### Merge unmerged work from 2026-05-05 session
2. **Merge or cherry-pick `claude/nifty-shannon-d10066` to main** — contains DATA_ANALYST.md, AGENT_LOG.md, data_quality_check.py, and ORCHESTRATOR.md update (reads AGENT_LOG.md at session start). Review, then `git cherry-pick <commit>` or merge.

### Verification
3. **Verify Show Optimal Dates button** — was broken pre-revert; may now work after d651c28 revert. Check on live site.

### Autonomous (next session, after card bug fixed)
4. **🟡 DECISION PENDING — Quality check gate** — `data_quality_check.py` is a hard gate before the commit step in `price_checker.yml`. If it exits CRITICAL (e.g. checker writes no rows), the data update is lost. Recommend `continue-on-error: true` — logs always, never blocks. Awaiting user approval.
5. **🔴 Build Jekyll blog infrastructure** — Create `_posts/` dir, `_layouts/post.html` (matching `#f5f0e8`/`#1a4a42` design), `blog/index.html` listing page. GitHub Pages supports Jekyll natively. Then publish the first article (idea #1 below).
6. **🔴 Research Sandals pricing API** — Open `sandals.co.uk` in a browser, use DevTools Network tab to capture XHR/Fetch calls when searching for holidays. Or use WebFetch to inspect page structure first. Build `sandals_checker.py` + `_data/sandals_prices.csv`. Add to Actions at 08:00 UTC.
7. **Content article #1** — See article idea #1 below. Publish to `_posts/2026-05-XX-when-to-book-club-med-ski.md` after blog is set up.
8. **Grand Massif + Serre-Chevalier departure day** — Let data accumulate; revisit when 4+ weeks available (target: late May 2026).
9. **Run backfill after any future gap** — `python backfill_prices.py && python clubmed_checker.py --inject-only`

### Agent coordination (high priority)
10. **Write tighter git operating rules for agents** — Agents must: commit directly to main (not worktree branches); commit after every completed task (not at 150-turn mark); never run simultaneously in the same repo (git lock contention). Add these as explicit rules to BUILDER.md and ORCHESTRATOR.md.

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

--- NOT YET ON MAIN (branch claude/nifty-shannon-d10066) ---
DATA_ANALYST.md             — Data Analyst agent: placeholder detection, quality scoring 0–100
AGENT_LOG.md                — Inter-agent communication log (Orchestrator reads at session start)
data_quality_check.py       — Reads price_history.csv, detects CRITICAL/WARNING/INFO, appends to AGENT_LOG.md
```
