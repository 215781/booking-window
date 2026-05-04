# When To Book — Project Context

**whentobook.co.uk** — Club Med ski resort price intelligence site. Built by Drop Media Ltd.

## What the site does

Tracks live pricing across 11 Club Med French Alps ski resorts daily, builds a historical record, and shows visitors whether now is a good time to book. Signal states: **Favourable / Watch / Hold**. Email alerts via Kit (ConvertKit) when signals shift.

Founding insight: at Club Med La Plagne, two families paid £1,600 different prices for the same resort and same week. The site exists to give people the intelligence to be the cheaper family.

---

## Tech stack

| Layer | Technology |
|---|---|
| Frontend | `clubmed/index.html` — single-file HTML/CSS/JS. No frameworks, no build tools. |
| Brand landing page | `index.html` — root site landing page linking to operator trackers |
| Price data | `clubmed_checker.py` — Python 3.11, Club Med GraphQL API |
| Data storage | `_data/price_history.csv` — append-only, never delete rows. Jekyll/GitHub Pages won't serve `_data/`. |
| Scheduler | GitHub Actions cron — `.github/workflows/price_checker.yml` |
| Hosting | **GitHub Pages** (DNS live as of 2026-05-04). Vercel still exists but DNS no longer routes there. |
| Email | Kit (ConvertKit) — public form endpoints only, no API key in repo |
| SSH deploy key | `~/.ssh/booking_window_deploy` |

---

## Repo structure

```
clubmed/index.html                — Club Med tracker (canonical live site at /clubmed)
index.html                        — Root brand landing page (whentobook.co.uk)
WhentoBook.html                   — Redirect → /clubmed (legacy URL)
clubmed_checker.py                — Price checker (flags: --test, --verify, --inject-only)
backfill_prices.py                — Gap-fill script: run after multi-day outage
_data/price_history.csv           — Full price log (append-only — never delete rows)
vercel.json                       — Vercel routing + security headers (Vercel only; GitHub Pages ignores)
CNAME                             — GitHub Pages custom domain (whentobook.co.uk)
robots.txt
sitemap.xml
privacy.html
og-image.svg
.github/workflows/
  price_checker.yml               — Daily at 06:00 UTC — runs checker, commits HTML + CSV
  backup.yml                      — Weekly Sunday 02:00 UTC — GitHub Releases backup of price_history.csv
CLAUDE.md                         — this file (project context for all agents)
ORCHESTRATOR.md                   — orchestrator agent instructions
BUILDER.md                        — builder agent instructions
SCRIBE.md                         — scribe agent instructions
PLAN.md                           — current roadmap and task list
NEXT_SESSION_PROMPT.md            — session state (read first every session)
```

---

## Resorts (all 11 verified as of 26–27 Apr 2026)

| Resort | Code | Departure day |
|---|---|---|
| Tignes | `TIGC_WINTER` | Sunday |
| Les Arcs Panorama | `ARPC_WINTER` | Sunday |
| Peisey-Vallandry | `PVAC_WINTER` | Sunday |
| Valmorel | `VMOC_WINTER` | Sunday |
| Alpe d'Huez | `ALHC_WINTER` | Sunday |
| La Rosière | `LROC_WINTER` | Sunday |
| La Plagne 2100 | `LP2C_WINTER` | Sunday |
| Val d'Isère | `VDIC_WINTER` | Sunday |
| Grand Massif | `GMAC_WINTER` | TBC — both Sat+Sun return prices observed |
| Val Thorens Sensations | `VTHC` | Sunday — **no `_WINTER` suffix** (year-round resort) |
| Serre-Chevalier | `SECC_WINTER` | TBC — both Sat+Sun return prices observed |

---

## GitHub Actions

### `price_checker.yml`
- Runs daily at **06:00 UTC**
- 180-minute timeout
- Rotating User-Agent pool, random 2–8s delays between API calls, 15–30s pause between resorts, randomised resort order
- Commits updated `clubmed/index.html` and `_data/price_history.csv` back to main automatically
- Repository secrets required: `GMAIL_ADDRESS`, `GMAIL_APP_PASS`, `ALERT_TO`

### `backup.yml`
- Runs every **Sunday at 02:00 UTC** (manual trigger also available)
- Creates a GitHub Release tagged `backup-YYYY-MM-DD` with `price_history.csv` as artifact
- Releases are marked pre-release to keep them out of the changelog

---

## Kit email integration

| Form | ID | Endpoint |
|---|---|---|
| Booking Alert (bottom of page) | `7f784a323c` | `https://app.kit.com/forms/7f784a323c/subscriptions` |
| Search Results popup | `f197f8f414` | `https://app.kit.com/forms/f197f8f414/subscriptions` |

- Custom field: `resort_interest` (text — resort name or resort + date)
- Tags: `booking-alert` and `search-popup` applied automatically by Kit Rules
- Welcome sequence: live, fires immediately on signup to either form
- **No Kit API key in the repo** — public endpoints only, ever

---

## Design tokens (locked — do not change)

| Token | Value |
|---|---|
| Background | `#f5f0e8` (warm off-white) |
| Primary | `#1a4a42` (deep teal) |
| Secondary | `#8a6a2a` (warm amber) |
| Display font | Playfair Display (serif) |
| Body font | Inter (sans-serif) |
| Favourable badge | teal `#1a4a42` |
| Watch badge | amber `#8a6a2a` |
| Hold badge | grey `#bbb5aa` |

---

## Language rules (locked — violation is a bug)

**Never use:** deals, discounts, cheap, vouchers, savings

**Always use:** booking intelligence, optimal timing, historically favourable pricing, smart booking, pricing shift

Audience: financially savvy people. Overpaying stings not just financially but because it undermines the story they told themselves about making a curated choice.

---

## Signal / data state

`DATA_SUFFICIENT = false` until at least autumn 2026. While false, all signal badges display "Building data — check back in autumn" instead of Favourable/Watch/Hold. Do not change this flag until several months of real price movement data has accumulated.

---

## Club Med GraphQL API

```
POST https://graphql.dcx.clubmed/
```

- No auth required
- Needs browser-like headers: `Origin: https://www.clubmed.co.uk`, proper `User-Agent`
- **Blocked from datacenter IPs** — GitHub Actions works; standard VPS does not
- Use `departureCity: "NO"` — accommodation only, flights excluded intentionally (too volatile)
- Returns `bestPriceValue` as integer (e.g. `3240` = £3,240)

---

## Checker flags

| Flag | Behaviour |
|---|---|
| (none) | Normal run: makes API calls, writes to `clubmed/index.html`, appends to CSV |
| `--test` | Dry run — no writes |
| `--verify` | One API call to confirm connectivity |
| `--inject-only` | Rebuild `RESORT_DATA` from CSV without making any API calls |

---

## Security

- No secrets in repo — GitHub Actions secrets: `GMAIL_ADDRESS`, `GMAIL_APP_PASS`, `ALERT_TO`
- `escapeHtml()` function guards against XSS in search param injection
- CSP meta tag in `clubmed/index.html` and `index.html` (GitHub Pages doesn't support HTTP headers)
- Security headers in `vercel.json`: X-Frame-Options, X-Content-Type-Options, Referrer-Policy, Permissions-Policy, CSP

---

## Git / push

SSH key: `~/.ssh/booking_window_deploy`
Remote: `git@github.com:215781/booking-window.git`

If push fails:
```bash
git remote set-url origin git@github.com:215781/booking-window.git
git push
```

---

## Important invariants

- `_data/price_history.csv` is **append-only** — the historical record is the product. Never delete rows.
- The checker injects `RESORT_DATA` directly into `clubmed/index.html` at runtime.
- `DATA_SUFFICIENT = false` — do not change until autumn 2026.
- `NEXT_SESSION_PROMPT.md` is the session handoff — the orchestrator reads it first every session.
- `PLAN.md` tracks the current roadmap — the scribe keeps it updated.
- Never use "deals", "discounts", "cheap", "vouchers", or "savings" anywhere in the site copy.
