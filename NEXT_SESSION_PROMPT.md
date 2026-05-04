# Next Session Prompt — When To Book

**Read this file first at the start of every session, before doing anything else.**
Then read `PLAN.md` for the full task list.

---

## Context

**whentobook.co.uk** — Club Med price intelligence site (ski resorts). Built by Drop Media Ltd. Root URL is a brand landing page; Club Med tracker lives at `/clubmed`. Future operators: `/markwarner`, `/sandals` etc.

- **Repo:** `~/booking-window/` / `git@github.com:215781/booking-window.git`
- **Live site:** GitHub Pages — DNS live as of 2026-05-04. HTTP working; HTTPS cert auto-provisioning (check within 24h then enable "Enforce HTTPS" in Pages Settings). Vercel still exists but DNS no longer routes to it.
- **HTML files:** `clubmed/index.html` (Club Med tracker — checker writes here), `index.html` (root brand landing page), `WhentoBook.html` (redirect → /clubmed)
- **Price checker:** `clubmed_checker.py` — runs daily at 06:00 UTC via GitHub Actions, writes to `clubmed/index.html`
- **Price history:** `_data/price_history.csv` — 8,967 rows (5,250 real + 3,717 backfill). Append-only. In `_data/` so GitHub Pages won't serve it publicly.
- **Resorts:** 11 French Alps resorts, all codes verified
- **Signal state:** `DATA_SUFFICIENT = false` — badges show "Building data — check back in autumn". Do not change until autumn 2026.
- **Email:** Kit (ConvertKit) — Booking Alert form `7f784a323c`, Search popup form `f197f8f414`. Welcome sequence live.
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
- 2026-05-04 — GA4 analytics script added (placeholder `G-XXXXXXXXXX` — needs real ID)
- 2026-05-04 — Data purge: 612 suspect LP2C/VDIC rows (Apr 23–25) removed; RESORT_DATA regenerated
- 2026-05-04 — `--inject-only` flag added to checker; `VMOC_WINTER` verified correct
- 2026-05-04 — `backfill_prices.py` built and run: 3,717 rows for Apr 27–May 3
- 2026-05-04 — Security review: `escapeHtml()` added; `BookingWindow_v1_2.html` removed; security headers in `vercel.json`; CSP meta tag in both HTML files
- 2026-05-04 — Data backup: `.github/workflows/backup.yml` — weekly GitHub Releases backup
- 2026-05-04 — DNS live (GitHub Pages IPs confirmed); GitHub Pages serving on HTTP
- 2026-05-04 — JSON-LD schema markup added to `clubmed/index.html` and `index.html`
- 2026-05-04 — Mark Warner + Sandals data collection added as high-priority plan items

---

## Up Next (priority order)

### User actions required first
1. **Enforce HTTPS on GitHub Pages** — HTTPS cert usually provisions within a few hours of DNS going live. Go to `https://github.com/215781/booking-window/settings/pages`, tick "Enforce HTTPS" once available.
2. **Wire up GA4 measurement ID** — Create a property at analytics.google.com. Replace both `G-XXXXXXXXXX` placeholders in `clubmed/index.html` (~lines 26–33). Commit and push.
3. **Decommission Vercel** — DNS no longer routes there. Safe to delete the Vercel project.

### Autonomous (next session)
4. **🔴 Research Mark Warner pricing API** — Open `markwarner.co.uk`, browse to a holiday search, use DevTools Network tab to find the pricing/availability API endpoint. Build `markwarner_checker.py` modelled on `clubmed_checker.py`. Store in `_data/markwarner_prices.csv`. Add to GitHub Actions.
5. **🔴 Research Sandals pricing API** — Same approach for `sandals.co.uk`. Build `sandals_checker.py` + `_data/sandals_prices.csv`. Add to Actions.
6. **OG image** — Create a proper 1200×630 PNG OG image (current SVG not supported by Twitter/X or Facebook). Can use `qlmanage -t -s 1200 -o /tmp/ og-image.svg` then crop/resize with `sips`.
7. **Update CLAUDE.md** — Reflect new structure: `clubmed/index.html` is canonical (not `WhentoBook.html`), GitHub Pages is the host (not Vercel), two new checker scripts planned.
8. **Grand Massif + Serre-Chevalier departure day** — Let data accumulate; revisit when 4+ weeks of data available.
9. **Run backfill after any future gap** — `python backfill_prices.py && python clubmed_checker.py --inject-only`

---

## Backlog

**Quick wins:**
- Real resort photography — gradient placeholders on all 11 cards
- OG image PNG (see Up Next #6)

**Medium term:**
- Affiliate programme (Awin) — apply once ~100 click-throughs; 45-day cookie, ~3% commission
- 3-adult party size option in search form
- Mobile responsiveness improvements
- SEO foundations — JSON-LD schema done ✓; next: individual resort landing pages
- Blog / content section — `whentobook.co.uk/blog` via Jekyll `_posts/`
- Content Writer agent (`CONTENT_WRITER.md`)
- Email sequence expansion — extend Kit welcome from 1 email to 4–6
- Flash sale notification — alert when Club Med annual early booking window opens
- Booking-window analysis script — target Oct 2026 (6+ months CSV data needed)

**Summer resort expansion:**
- Phase 1: European summer resorts — Magna Marbella (`MMAC` verified), Cefalù, Gregolimano, Palmiye, Marrakech

**Long term:**
- Mark Warner / Neilson full site (after data collection running)
- Sandals full site (after data collection running)
- Annual Club Med price report — Sep/Oct email broadcast
- Drop Media Ltd Companies House registration (£12, 15 mins)
- `DATA_SUFFICIENT = true` — autumn 2026 only
- Eurostar Snow alert page — lowest priority

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
backfill_prices.py          — Gap-fill script (run after multi-day outage)
_data/price_history.csv     — Append-only price log (8,967 rows as of 2026-05-04)
vercel.json                 — Routing + security headers (Vercel only; GitHub Pages ignores)
.github/workflows/
  price_checker.yml         — Daily checker at 06:00 UTC
  backup.yml                — Weekly CSV backup to GitHub Releases (Sundays 02:00 UTC)
When To Book/Agents/        — Agent .md files mirrored to vault (Obsidian)
```
