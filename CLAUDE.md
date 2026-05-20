# When To Book — Project Context

**whentobook.co.uk** — Club Med ski resort price intelligence site. Built by Drop Media Ltd.

---

## ⚠️ THE MOST IMPORTANT INVARIANT — READ THIS FIRST

**Every session ends with `git push origin main` confirmed. No exceptions.**

A session is not complete until the Scribe has pushed and reported the HEAD commit hash. The next session must verify its HEAD matches that recorded hash before doing any work. This rule exists because every regression in this project's history — resort images deleted, hero best-card wiped, CSS reverted — was caused by stale commits being cherry-picked onto `main` without verifying the result was pushed and correct.

**Start of session:** `git log main -1 --oneline` → must match `HEAD:` in `NEXT_SESSION_PROMPT.md`  
**End of session:** `git push origin main` → Scribe records confirmed hash in `NEXT_SESSION_PROMPT.md`

See `ORCHESTRATOR.md` and `SCRIBE.md` for the full protocol.

---

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
| Data storage | `_data/prices_clubmed.csv` — append-only, never delete rows. Jekyll/GitHub Pages won't serve `_data/`. |
| Scheduler | GitHub Actions cron — `price_checker.yml` (CSV only) + `build_site.yml` (HTML rebuild, triggered by CSV changes) |
| Hosting | **GitHub Pages** (DNS live as of 2026-05-04). Vercel project exists but DNS no longer routes there — pending decommission. |
| Analytics | Google Analytics 4 — measurement ID `G-G2RES5DX0K` (not a secret; public in HTML) |
| Email | Kit (ConvertKit) — public form endpoints only, no API key in repo |
| SSH deploy key | `~/.ssh/booking_window_deploy` |

---

## Repo structure

```
clubmed/index.html                — Club Med tracker (canonical live site at /clubmed)
index.html                        — Root brand landing page (whentobook.co.uk)
WhentoBook.html                   — Redirect → /clubmed (legacy URL)
clubmed_checker.py                — Price checker (flags: --test, --verify, --inject-only); writes CSV only
backfill_prices.py                — Gap-fill script: run after multi-day outage
_data/prices_clubmed.csv          — Club Med price log (append-only — never delete rows)
_data/prices_markwarner.csv       — Mark Warner price log (placeholder; checker active)
_data/prices_sandals.csv          — Sandals price log (placeholder; checker not yet built)
vercel.json                       — Vercel routing + security headers (Vercel only; GitHub Pages ignores)
CNAME                             — GitHub Pages custom domain (whentobook.co.uk)
robots.txt
sitemap.xml
privacy.html
og-image.svg
og-image.png                          — OG image (1200×630 PNG — Twitter/Facebook compatible)
.github/workflows/
  price_checker.yml               — Daily at 06:00 UTC — runs checker, commits CSV only
  build_site.yml                  — Triggered by prices_*.csv changes — rebuilds clubmed/index.html via --inject-only
  backup.yml                      — Weekly Sunday 02:00 UTC — GitHub Releases backup of prices_clubmed.csv
CLAUDE.md                         — this file (project context for all agents)
ORCHESTRATOR.md                   — orchestrator agent instructions
BUILDER.md                        — builder agent instructions
SCRIBE.md                         — scribe agent instructions
PLAN.md                           — current roadmap and task list
IMPROVEMENT_PLAN.md               — strategic improvement plan (reference for PLAN.md items)
NEXT_SESSION_PROMPT.md            — session state (read first every session)

## Planned (not yet built)
markwarner_checker.py             — Mark Warner price checker (1 resort: Chalet Hotel L'Écrin, Tignes; product ID SKI-24314)
sandals_checker.py                — Sandals price checker
_data/markwarner_prices.csv       — Mark Warner price log (append-only)
_data/sandals_prices.csv          — Sandals price log (append-only)
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
- 60-minute timeout (async rewrite, 15–20 min actual runtime)
- aiohttp + asyncio, Semaphore(8) concurrency, rotating User-Agent pool, 429 backoff, push retry
- Commits `_data/prices_clubmed.csv` only — HTML rebuild delegated to `build_site.yml`
- Repository secrets required: `GMAIL_ADDRESS`, `GMAIL_APP_PASS`, `ALERT_TO`

### `build_site.yml`
- Triggered by pushes that modify any `_data/prices_*.csv` file
- Runs `clubmed_checker.py --inject-only` to regenerate `clubmed/index.html` from CSV
- Concurrency-queued (one run at a time per branch)

### `backup.yml`
- Runs every **Sunday at 02:00 UTC** (manual trigger also available)
- Creates a GitHub Release tagged `backup-YYYY-MM-DD` with `prices_clubmed.csv` as artifact
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

- **`git push origin main` must succeed before any session ends.** Scribe records the HEAD hash in `NEXT_SESSION_PROMPT.md`. Next session verifies it matches before starting work. See the top of this file and `SCRIBE.md`.
- `_data/prices_clubmed.csv` (and all `_data/prices_*.csv` files) are **append-only** — the historical record is the product. Never delete rows.
- The checker injects `RESORT_DATA` directly into `clubmed/index.html` at runtime. **Never run `--inject-only` from a worktree** — always run from the main repo after pulling latest `main`, or it regenerates from a stale template and wipes newer work.
- `DATA_SUFFICIENT = false` — do not change until autumn 2026.
- `NEXT_SESSION_PROMPT.md` is the session handoff — the orchestrator reads it first every session AND verifies the HEAD hash.
- `PLAN.md` tracks the current roadmap — the scribe keeps it updated.
- Never use "deals", "discounts", "cheap", "vouchers", or "savings" anywhere in the site copy.
- Before any push touching `clubmed/index.html`, verify: `grep -c "RESORT_IMAGES" clubmed/index.html` > 0 and `grep -c "renderHeroBestCard" clubmed/index.html` > 0. If either is 0, the file has regressed — do not push.
