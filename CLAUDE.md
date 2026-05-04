# When To Book — Project Context

**whentobook.co.uk** — Club Med ski resort price intelligence site. Built by Drop Media Ltd.

## What the site does

Tracks live pricing across 11 Club Med French Alps ski resorts daily, builds a historical record, and shows visitors whether now is a good time to book. Signal states: **Favourable / Watch / Hold**. Email alerts via Kit (ConvertKit) when signals shift.

Founding insight: at Club Med La Plagne, two families paid £1,600 different prices for the same resort and same week. The site exists to give people the intelligence to be the cheaper family.

---

## Tech stack

| Layer | Technology |
|---|---|
| Frontend | Single-file HTML/CSS/JS — `WhentoBook.html`. No frameworks, no build tools. |
| Price data | `clubmed_checker.py` — Python 3.11, Club Med GraphQL API |
| Data storage | `_data/price_history.csv` — append-only, never delete rows |
| Scheduler | GitHub Actions cron — `.github/workflows/price_checker.yml` |
| Hosting | Vercel (live). GitHub Pages configured via `CNAME` but DNS not yet set. |
| Email | Kit (ConvertKit) — public form endpoints only, no API key in repo |
| SSH deploy key | `~/.ssh/booking_window_deploy` |

---

## Repo structure

```
WhentoBook.html                   — the live website (canonical file)
clubmed_checker.py                — price checker script
_data/price_history.csv           — full price log (append-only — never delete; Jekyll won't serve _data/)
vercel.json                       — Vercel output config and URL rewrite
CNAME                             — GitHub Pages custom domain (whentobook.co.uk)
robots.txt
sitemap.xml
privacy.html
og-image.svg
.github/workflows/
  price_checker.yml               — GitHub Actions: daily at 06:00 UTC
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

File: `.github/workflows/price_checker.yml`

- Runs daily at **06:00 UTC**
- 180-minute timeout
- Rotating User-Agent pool, random 2–8s delays between API calls, 15–30s pause between resorts, randomised resort order
- Commits updated `WhentoBook.html` and `_data/price_history.csv` back to main automatically
- Repository secrets required: `GMAIL_ADDRESS`, `GMAIL_APP_PASS`, `ALERT_TO`

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
- The checker injects `RESORT_DATA` directly into `WhentoBook.html` at runtime.
- `NEXT_SESSION_PROMPT.md` is the session handoff — the orchestrator reads it first every session.
- `PLAN.md` tracks the current roadmap — the scribe keeps it updated.
