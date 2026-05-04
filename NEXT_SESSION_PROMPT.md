# Next Session Prompt — When To Book

**Read this file first at the start of every session, before doing anything else.**
Then read `PLAN.md` for the full task list.

---

## Context

**whentobook.co.uk** — Club Med price intelligence site (ski resorts). Built by Drop Media Ltd. Root URL is a brand landing page; Club Med tracker lives at `/clubmed`. Future operators: `/markwarner`, `/neilson` etc.

- **Repo:** `~/booking-window/` / `git@github.com:215781/booking-window.git`
- **Live site:** Vercel deployment (auto-deploys from main). GitHub Pages configured via `CNAME` but DNS not yet set at registrar.
- **HTML files:** `clubmed/index.html` (live Club Med tracker — checker writes here), `index.html` (root brand landing page), `WhentoBook.html` (redirect → /clubmed)
- **Price checker:** `clubmed_checker.py` runs daily at 06:00 UTC via GitHub Actions — writes to `clubmed/index.html`
- **Price history:** `_data/price_history.csv` — ~5,862+ rows. Append-only, never delete. In `_data/` so Jekyll/Pages won't serve it publicly.
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
- 2026-05-04 — price_history.csv moved to _data/price_history.csv (Jekyll hides it from Pages); Vercel block added; all path refs updated
- 2026-05-04 — Strategic planning session: full vault + HTML audit, web research on Club Med catalogue/affiliate/booking patterns, `IMPROVEMENT_PLAN.md` created, PLAN.md expanded with full roadmap
- 2026-05-04 — Agent .md files mirrored to vault at `When To Book/Agents/` for Obsidian access
- 2026-05-04 — **URL restructure complete:** `clubmed/index.html` created (canonical → /clubmed), root `index.html` brand landing page built, `clubmed_checker.py` updated to write `clubmed/index.html`, GitHub Actions workflow updated, `vercel.json` updated (new routing + 301 from /WhentoBook.html), `sitemap.xml` updated, `WhentoBook.html` converted to redirect page
- 2026-05-04 — Deep-link Club Med CTAs confirmed working — all `bookingUrl` values already point to resort-specific pages (`clubmed.co.uk/r/[slug]/y`)
- 2026-05-04 — GA4 analytics script added to `clubmed/index.html` with placeholder `G-XXXXXXXXXX`
- 2026-05-04 — Data purge: 612 suspect rows (LP2C_WINTER + VDIC_WINTER, Apr 23–25) removed from CSV; RESORT_DATA regenerated
- 2026-05-04 — `VMOC_WINTER` verified correct (no space); `--inject-only` flag added to checker
- 2026-05-04 — Data gap backfill task added to PLAN.md as high priority
- 2026-05-04 — Security review: `escapeHtml()` added to site JS; `BookingWindow_v1_2.html` removed; security headers (CSP, X-Frame-Options, X-Content-Type-Options, Referrer-Policy, Permissions-Policy) added to `vercel.json`
- 2026-05-04 — Data backup: `.github/workflows/backup.yml` added — weekly GitHub Releases backup of `price_history.csv` every Sunday at 02:00 UTC

---

## Up Next

1. **Wire up GA4 measurement ID** — create a GA4 property at analytics.google.com, get the Measurement ID (`G-XXXXXXXXXX`), replace the placeholder in `clubmed/index.html` (two occurrences, lines ~25–32). **User action required to create the property.**
2. **Activate GitHub Pages in repo Settings** — Source: "Deploy from a branch" → `main` → `/ (root)`. CNAME already committed. User action.
3. **Configure DNS at Squarespace** — 4 × A records (`@` → `185.199.108.153 / .109 / .110 / .111`) + CNAME (`www` → `215781.github.io`). User action.
4. **Decommission Vercel** (after Pages DNS is live).
5. ~~**Verify `VMOC_WINTER` code**~~ — verified correct 2026-05-04. ✓
6. **Grand Massif + Serre-Chevalier departure day** — let data accumulate, revisit in a few weeks.
7. ~~**Cybersecurity review**~~ — completed 2026-05-04. ✓
8. ~~**Data backup**~~ — weekly GitHub Releases backup live. ✓
9. **Eurostar Snow alert page** — lowest priority. Build page + Kit form to alert when Eurostar Snow tickets go live.

---

## Backlog

See `IMPROVEMENT_PLAN.md` for full strategic context on all items below.

**Quick wins:**
- Real resort photography — gradient placeholders on all 11 cards
- Improve OG image — current SVG may not render in social preview contexts

**Medium term:**
- Cybersecurity review (see Up Next #7)
- Data backup automation (see Up Next #8)
- Affiliate programme (Awin) — apply once ~100 click-throughs; 45-day cookie, ~3% commission
- 3-adult party size option in search form
- Mobile responsiveness improvements
- SEO foundations — JSON-LD schema markup (URL restructure now done — can proceed)
- Blog / content section — `whentobook.co.uk/blog` via Jekyll `_posts/` (GitHub Pages native). Target 5 initial articles.
- Content Writer agent — add `CONTENT_WRITER.md` to repo; agent researches, writes, and publishes SEO posts to `_posts/`. Target 2 posts/month.
- Email sequence expansion — extend Kit welcome from 1 email to 4–6 over 2–3 weeks
- Flash sale notification — alert subscribers when Club Med opens annual early booking windows (ski ~Feb, summer ~Oct)
- Booking-window analysis script — target Oct 2026 (6+ months of CSV data needed)

**Summer resort expansion (target: before Oct 2026 booking window):**
- Phase 1: European summer resorts — Magna Marbella (`MMAC` verified), Cefalù, Gregolimano, Palmiye, Marrakech
- Phase 2+: Caribbean, Indian Ocean, Asia (after Phase 1 stable)
- Requires: resort code discovery, checker update, ski/beach UI toggle, date range expansion

**Long term:**
- Mark Warner / Neilson tracker — second site in portfolio
- Annual Club Med price report — email broadcast each Sep/Oct
- Drop Media Ltd Companies House registration (£12, 15 mins)
- Eurostar Snow alert page + full price tracker — lowest priority

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
</content>
</invoke>