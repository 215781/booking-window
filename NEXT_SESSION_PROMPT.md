# Next Session Prompt — When To Book

**Read this file first at the start of every session, before doing anything else.**
Then read `PLAN.md` for the full task list.

---

## Context

**whentobook.co.uk** — Club Med ski resort price intelligence site. Built by Drop Media Ltd.

- **Repo:** `~/booking-window/` / `git@github.com:215781/booking-window.git`
- **Live site:** Vercel deployment (auto-deploys from main). GitHub Pages configured via `CNAME` but DNS not yet set at registrar.
- **HTML file:** `WhentoBook.html` (single-file site — also the data file the checker writes into)
- **Price checker:** `clubmed_checker.py` runs daily at 06:00 UTC via GitHub Actions
- **Price history:** `price_history.csv` — ~5,862 rows as of 28 Apr 2026. Append-only, never delete.
- **Resorts:** 11 French Alps resorts, all codes verified
- **Signal state:** `DATA_SUFFICIENT = false` — all badges show "Building data — check back in autumn". Do not change until autumn 2026.
- **Email:** Kit (ConvertKit) — Booking Alert form `7f784a323c`, Search popup form `f197f8f414`. Welcome sequence live.
- **SSH key:** `~/.ssh/booking_window_deploy`

Why prices are mostly empty: Club Med UK hasn't opened winter 2026/27 bookings yet. Only Easter dates (Apr 2027) are currently on sale. Booking window typically opens June/July 2026. Not a bug.

---

## Completed

- 2026-04-21 — Built single-file HTML/CSS/JS site (`WhentoBook.html`)
- 2026-04-21 — Python price checker (`clubmed_checker.py`) built and verified
- 2026-04-21 — GitHub Actions workflow set up
- 2026-04-21 — All 6 original resort codes verified via GraphQL API
- 2026-04-22 — CNAME committed (`whentobook.co.uk`); SSH deploy key generated
- 2026-04-22 — First automated checker run; orphaned placeholder data fixed
- 2026-04-26 — Expanded to 11 resorts; all codes verified (26–27 Apr)
- 2026-04-26 — Scheduled checker live — daily at 06:00 UTC, 180-min timeout
- 2026-04-26 — Signal system: Favourable / Watch / Hold implemented
- 2026-04-26 — Three-mode date search, modal search results, mobile layout, alpine card gradients, child age input
- 2026-04-26 — Cookie notice and `privacy.html` live
- 2026-04-26 — Season price calendar view added to resort modal
- 2026-04-28 — `price_history.csv` at ~5,862 rows; 2,205 junk rows purged
- 2026-04-28 — Vercel 404 fixed — `vercel.json` committed, rewrite `/` → `/WhentoBook.html`
- 2026-04-28 — Kit Cowork session: both forms configured, custom field, tags, welcome sequence live
- 2026-04-28 — Search popup wired to correct Kit form (`f197f8f414`)
- 2026-05-04 — Multi-agent workflow set up: CLAUDE.md, ORCHESTRATOR.md, BUILDER.md, SCRIBE.md, PLAN.md

---

## Up Next

1. **Configure DNS** — set CNAME `www` → `215781.github.io` and A records for apex. User action — not a code task.
   - A records: `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`
   - After DNS: GitHub Pages > Settings > confirm custom domain + Enforce HTTPS
2. **Decide: GitHub Pages vs Vercel** — both live; pick canonical deployment and point DNS there.
3. **Verify `VMOC_WINTER` code** — a space was noted (`VMO C_WINTER`) in one session note; confirm in the actual checker file.
4. **Grand Massif + Serre-Chevalier departure day** — let data accumulate; revisit in a few weeks to confirm Sat vs Sun.

---

## Backlog

- Booking-window analysis script — target Oct 2026 (6+ months of CSV data needed)
- Party composition: 3-adult / 4-adult (deferred — user noted people can infer from 2-adult)
- Mobile responsiveness improvements
- Real resort photography for card image areas
- Deep-link "Book on Club Med" CTAs to specific resort pages
- SEO content — individual resort pages, long-tail blog posts
- Affiliate programme (Awin) — apply once ~100 click-throughs
- Eurostar Snow ticket alert page — **tickets go on sale 9 July 2026** at ~8am; build before that date
- Mark Warner / Neilson tracker — natural second site in the portfolio

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
- Tags: `booking-alert`, `search-popup` (applied by Kit Rules — not in POST payload)
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
