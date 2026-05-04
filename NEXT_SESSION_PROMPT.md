# Next Session Prompt — When To Book

**Read this file first at the start of every session, before doing anything else.**
Then read `PLAN.md` for the full task list.

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
_data/markwarner_prices.csv — Mark Warner price log (54 rows seeded, append-only)
vercel.json                 — Routing + security headers (Vercel only)
.github/workflows/
  price_checker.yml         — Club Med: daily 06:00 UTC
  markwarner_checker.yml    — Mark Warner: daily 07:00 UTC
  backup.yml                — Weekly CSV backup to GitHub Releases (Sundays 02:00 UTC)
When To Book/Agents/        — Agent .md files mirrored to vault (Obsidian)
```
