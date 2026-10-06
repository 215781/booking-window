# When To Book - Project Context

**whentobook.co.uk** - an email-first price-watch site for UK families booking all-inclusive school-holiday trips (Club Med ski + sun, Mark Warner). Owner: **Connor Martin, trading as When To Book** (sole trader).

**The single source of truth is the vault plan `When To Book/PLAN_V3.md`** (Connor's Knowledge Vault) plus the latest file in `Session Notes/`. Read it first. This file only holds stable project rules. Older files in this repo (`PLAN.md`, `PLAN_V2.md`, `NEXT_SESSION_PROMPT.md`, `ORCHESTRATOR.md`, `SCRIBE.md`, `BUILDER.md`) are history and may be wrong.

Writing style for everything (site, emails, docs): UK English, plain and direct, hyphens not em dashes.

---

## NON-NEGOTIABLES (owner-set 2026-09-30) - above every feature

1. **Legal** - collect politely: one honest bot user agent (`WhenToBookBot/1.0`), modest concurrency, respect robots.txt, stop if blocked, never evade blocks (no UA/IP rotation). Never publish or sell the raw dataset - show analysis and a few example prices. "Checked [time], guidance only" on prices. Affiliate disclosure by every affiliate link. Cookie consent before analytics cookies. Owner is a **sole trader** (Connor Martin, trading as When To Book) - never write "Ltd" or "Drop Media Ltd" on the site.
2. **Secure** - store no customer data ourselves (emails + preferences live in Kit); secrets only in GitHub/host secret stores; bot protection on forms; security headers + CSP.
3. **Works and true** - every signup/preference verified stored; no synthetic or stale data shown as current; sanity checks before publishing; "updated" time on every page.
4. **Analytics solid** - funnel tracked end to end (visit, signup, email click, affiliate click, commission); numbers reconciled weekly.
5. **Backed up** - 3-2-1 backups for price data, subscribers and code; monthly restore test; alarm on missed backup.

Business model (confirmed 2026-09-30): affiliate + specialist-agent referral first, newsletter sponsorship second, no paid membership. Full plan: https://claude.ai/code/artifact/d085e5de-6b1e-406d-ba4f-edd4d3c1f596

---


---

## How the system fits together (updated 6 Oct 2026)

| Part | Where |
|---|---|
| Live site | Astro, branch **`rebuild`**, folder `site/`. Hosted on **Cloudflare Pages** (project `whentobook`), live on whentobook.co.uk since 1 Oct 2026; www 301s to the root. DNS on Cloudflare |
| Deploy | `.github/workflows/deploy_site.yml` (identical on `main` and `rebuild`): builds `rebuild:site` with `main:_data`, runs all site checks, deploys only if they pass. Runs twice daily, on push to `rebuild`, or by hand |
| Price data | Branch **`main`**, `_data/prices_*.csv`, append-only, written by the checkers below |
| Checkers | `clubmed_checker.py` (Alps ski), `clubmed_ski_international_checker.py`, `clubmed_summer_checker.py` (sun, 3 batches), `markwarner_summer_checker.py`, `markwarner_checker.py` (ski). One honest UA `WhenToBookBot/1.0` |
| Email | Kit (free plan). `site/email/` on `rebuild`, run by `email.yml` on `main` with the `KIT_API` secret. Alerts are Kit drafts until repo variable `ALERT_MODE=send`; weekly digest is always a draft |
| Analytics | GA4 `G-G2RES5DX0K`, only after cookie consent (`site/src/components/CookieConsent.astro`) |
| Backups | `backup.yml`: every price CSV + email state, Sun + Wed, as a release `backup-data-YYYY-MM-DD`, with an automatic restore test; keeps 16 |
| Alarm | `data_health.yml` + `tools/data_health.py`: daily freshness/coverage/size/deploy/backup check; opens a `health-alarm` issue on failure |
| Old site | `index.html`, `clubmed/index.html`, `build_site.yml`, Jekyll files on `main`: the pre-Oct 2026 GitHub Pages site. Retired; do not edit |

Site data: `site/scripts/build_summary.py` turns the CSVs into `site/src/data/summary.json` (only real collected prices; past departures dropped; stale data flagged). School-holiday windows live in `site/src/lib/weeks.ts`, resorts and booking URLs in `site/src/lib/resorts.ts`. Blog posts are `_posts/*.md` on `rebuild` (future-dated posts publish themselves on their date).

Local build/test: `cd site && npm ci && WTB_DATA_DIR=<main checkout>/_data python3 scripts/build_summary.py && npx astro build && npm test` then, with `npx astro preview` running, `node scripts/test_events.mjs`.

## Data rules

- `_data/prices_*.csv` are **append-only**: never delete or rewrite rows. The history is the product.
- Since 6 Oct 2026 the checkers skip departures that have never had a price (not on sale yet), to slow CSV growth. A departure priced before is still logged when it goes empty (sold out).
- GitHub rejects files over 100 MB. The big CSVs are ~60 MB; moving price history to Neon is planned (PLAN_V3).
- Old `LP2C_WINTER` rows are junk: always use `PLAC` for La Plagne (`build_summary.py` filters by current codes).
- Price moves over 25% are nearly always a room type selling out or returning: shown with a caveat, kept out of headlines and emails.
- Club Med booking URLs: `https://www.clubmed.co.uk/r/<slug>/w` (winter) or `/y` (sun/year-round). Source of truth: `https://www.clubmed.co.uk/pages/sitemap.xml`.
- Do not scrape Ikos (robots.txt disallows everything). Sandals and Ikos come via Awin feeds only.

## Resorts (all 11 verified as of 26–27 Apr 2026)

| Resort | Code | Departure day |
|---|---|---|
| Tignes | `TIGC_WINTER` | Sunday |
| Les Arcs Panorama | `ARPC_WINTER` | Sunday |
| Peisey-Vallandry | `PVAC_WINTER` | Sunday |
| Valmorel | `VMOC_WINTER` | Sunday |
| Alpe d'Huez | `ALHC_WINTER` | Sunday |
| La Rosière | `LROC_WINTER` | Sunday |
| La Plagne 2100 | `PLAC` | Sunday - **no `_WINTER` suffix** (year-round resort); **7-night only** |
| Val d'Isère | `VDIC_WINTER` | Sunday |
| Grand Massif | `GMAC_WINTER` | Saturday and Sunday |
| Val Thorens Sensations | `VTHC` | Sunday - **no `_WINTER` suffix** (year-round resort) |
| Serre-Chevalier | `SECC_WINTER` | Saturday and Sunday |

---


Grand Massif and Serre-Chevalier sell both Saturday and Sunday departures; the site uses the first priced departure in each school-holiday week.

## Club Med API

`POST https://graphql.dcx.clubmed/` - no auth. Works from GitHub Actions, not from datacentre VPSs. `departureCity: "NO"` (accommodation only, no flights). Checkers still send `Origin: https://www.clubmed.co.uk` - a grey area to review with the owner (PLAN_V3 §8).

## Design tokens (locked - do not change)

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

## Language rules (locked - violation is a bug)

**Never use:** deals, discounts, cheap, vouchers, savings

**Always use:** booking intelligence, optimal timing, historically favourable pricing, smart booking, pricing shift

Audience: financially savvy people. Overpaying stings not just financially but because it undermines the story they told themselves about making a curated choice.

---


## Git

- Work on `main` (checkers, data, workflows) or `rebuild` (site, emails, posts). Keep `deploy_site.yml` identical on both.
- Commit as "When To Book <admin@whentobook.co.uk>". Pull with rebase before pushing: bots push data to `main` many times a day.
- Connor's Mac auto-pushes local `main`/`rebuild` every 5 minutes (`tools/autopush.sh`), so sessions working in `~/booking-window` can commit locally.
- Never force-push. Never run `git worktree prune` from a Cowork VM.

## Secrets

Only in GitHub/Cloudflare secret stores: `KIT_API`, `CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_ACCOUNT_ID`, `GMAIL_*` (checker failure emails). Never in the repo.
