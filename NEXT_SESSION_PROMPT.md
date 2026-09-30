# Next Session Prompt — When To Book

**Read this file first at the start of every session, before doing anything else.**
Then read `PLAN_V2.md` (active plan; start with the "STATUS UPDATE — 2026-09-30" section). `PLAN.md` is superseded history.

---

## ⚠️ START-OF-SESSION CHECKS — DO THESE BEFORE ANYTHING ELSE

Bots push price data to `main` every day, so any local clone is stale within hours.

```bash
cd ~/booking-window && git fetch && git status -sb        # expect to be behind origin; pull before working
curl -s "https://api.github.com/repos/215781/booking-window/actions/runs?per_page=30" | python3 -c "import sys,json;[print(r['created_at'][:16],r['name'],r['conclusion']) for r in json.load(sys.stdin)['workflow_runs']]"
```

Check that every workflow is `success`. As of 2026-09-30 three are NOT (see below). Do not assume the live HTML is current — check the newest `build:` commit date.

---

## State as of 2026-09-30 (full audit: vault `When To Book/Session Notes/2026-09-30-site-and-data-audit.md`)

**Site is live and healthy** (HTTPS OK, `/_data/*` returns 404). **Data pipeline is partly broken:**

| Job | Status |
|---|---|
| `build_site.yml` | Cancelled at 30-min limit almost daily since ~23 Jul → live `/clubmed` HTML data last regenerated **2 Sep** |
| `clubmed_summer_checker.yml` | Cancelled at 60-min limit daily since ~11 Aug → only ~6 of 24 resorts get rows per day |
| `markwarner_checker.yml` (ski) | Failing daily since 12 Aug; no rows since 10 Jun |
| winter price_checker, intl ski, MW summer, backup | Healthy |

Other facts:
- Club Med winter 2026/27 is **now on sale** (Dec–Apr all priced). The old "prices empty / not on sale yet" note is obsolete.
- `_data/prices_clubmed.csv` ≈ 54 MB / 535k rows; `prices_clubmed_summer.csv` ≈ 58 MB. Both hit GitHub's 100 MB file limit ~Jan 2027. 47% of winter rows are 6-night rows (30% priced). HTML is 10.7 MB.
- Grand Massif and Serre-Chevalier track Sat + Sun; all other resorts Sunday only (21 weeks, 6 Dec → 25 Apr).
- **Article prices are stale.** A full audit on 2026-06-22/23 (`verify_article_prices.py` — NOT in the repo, rebuild or recover it; 14 articles) set prices "as of June 2026". Winter prices have moved since. Re-audit due now (PLAN_V2 C11). Val d'Isère article wrongly says "42 departure dates" (should be 21).
- 280 junk `LP2C_WINTER` rows remain in the CSV (append-only; filtered by `resort_code`). For La Plagne always use `PLAC`.
- `DATA_SUFFICIENT = false` still — autumn decision now due (PLAN_V2 C9).
- Open plan work: PLAN_V2 **C1–C11 (pipeline/data, urgent)** then remaining B-tasks (B1, B6, B7, B8, B10, B12; `post.html` links `/privacy.html` → `/privacy/`). Awin application status unknown — owner to confirm.
- Owner is running a strategy rethink (Cowork) — expect the plan to change; treat PLAN_V2 C-group as the safe, direction-independent work.

## HANDOVER — end of Cowork session 2026-09-30 (read this first)

- **Push status:** owner to run: `export GIT_SSH_COMMAND="ssh -i ~/.ssh/booking_window_deploy"; git pull --no-rebase --no-edit; git push origin main; git push origin rebuild`. Check `git log origin/main -1` and that `origin/rebuild` exists before any work.
- **New site:** branch `rebuild`, folder `site/` (Astro). Preview: https://claude.ai/artifact/TKPUwYjAm1PYAh5sgqgUaT. Do NOT merge to main or change DNS without owner sign-off.
- **Ikos decision (owner, 30 Sep):** route 2 — use Kenwood Travel's Awin product feed once Awin approves. Do NOT scrape ikosresorts.swapsystems.com (robots.txt disallows all).
- **Owner set up:** Neon, Cloudflare, Healthchecks accounts; Kit API key in GitHub secrets; Chrome extension connected; network allowlist updated (check it works in the new session: neon.tech, kit.com, cloudflare.com, healthchecks.io).
- **Next:** verify 10:30 UTC build + 3-batch summer run; end-to-end Kit signup test; move data to Neon; Cloudflare Pages preview of `rebuild`; Turnstile + cookieless analytics; Sandals checker (respect robots.txt); review Val d'Isère +55% jump (C6); mark outbound_click + sign_up as GA4 key events once they arrive.
- **Plan doc:** https://claude.ai/code/artifact/d085e5de-6b1e-406d-ba4f-edd4d3c1f596

---

## Last session

- **Date:** 2026-09-30 (Cowork strategy rethink + pipeline fixes)
- **HEAD:** PUSH PENDING — commits made in a cloud clone; push blocked until the repo is added to the Cowork session's GitHub sources. Update this line with the pushed hash.
- **Commits:**
  - C1: build_site timeout fix — one-pass price-history index in `clubmed_checker.py`; synthetic "today" price point removed; build cron 08:00 → 10:30 UTC; `clubmed/index.html` regenerated (data to 29 Sep)
  - C2: summer checker — one-pass history cache, `--batch/--batches` args, workflow matrix of 3 sequential batches, concurrency 4
  - Legal: honest `WhenToBookBot/1.0` UA in all checkers (rotation removed)
  - Legal: "Drop Media Ltd" → "Connor Martin, trading as When To Book" (owner is a sole trader)
  - Scribe: CLAUDE.md non-negotiables, PLAN_V2 C1/C2 ticked + D-group, this file
- **Open:** verify first live runs of build_site (10:30 UTC) and 3-batch summer checker; C3 Mark Warner ski still failing; D3–D8 in PLAN_V2.
- **Strategy:** affiliate + agent referral first (no paid membership). Owner has applied to Awin. Plan doc: https://claude.ai/code/artifact/d085e5de-6b1e-406d-ba4f-edd4d3c1f596

---

## Last recorded repo state
Newest non-bot commit: `20d778bd` (2026-06-29, La Rosière vs Valmorel article). Everything since is bot data/build commits plus the 2026-09-30 audit docs.

---

## Context

**whentobook.co.uk** — Club Med price intelligence site (ski resorts). Built by Drop Media Ltd. Root URL is a brand landing page; Club Med tracker lives at `/clubmed`. Future operators: `/markwarner`, `/sandals` etc.

- **Repo:** `~/booking-window/` / `git@github.com:215781/booking-window.git`
- **Live site:** GitHub Pages — DNS live as of 2026-05-04. HTTPS working (verified 2026-09-30).
- **HTML files:** `clubmed/index.html` (Club Med tracker — checker writes here), `index.html` (root brand landing page), `WhentoBook.html` (redirect → /clubmed)
- **Price checker:** `clubmed_checker.py` — runs daily at 06:00 UTC via GitHub Actions, writes to `clubmed/index.html`
- **Mark Warner ski checker:** `markwarner_checker.py` — runs daily at 07:00 UTC, appends to `_data/prices_markwarner.csv`. Dormant in summer; currently FAILING daily since 12 Aug (see state table).
- **Mark Warner summer checker:** `markwarner_summer_checker.py` — runs daily at 06:30 UTC, appends to `_data/prices_markwarner_summer.csv`. 4 beach resorts: Aeolian Village (26928), Lemnos (8), Paleros (19300), Phokaia (16797). Seeded 2026-06-22 (1,198 rows).
- **Price history:** `_data/prices_clubmed.csv` — append-only. In `_data/` so GitHub Pages won't serve it publicly. (Note: was incorrectly writing to `price_history.csv` until async rewrite fixed this on 2026-05-31.)
- **Mark Warner ski prices:** `_data/prices_markwarner.csv` — 400+ rows seeded 2026-05-07. Append-only. (Legacy file `markwarner_prices.csv` also exists — old schema, ignore.)
- **Mark Warner summer prices:** `_data/prices_markwarner_summer.csv` — 1,198 rows seeded 2026-06-22. Append-only.
- **Resorts:** 11 French Alps Club Med resorts, all codes verified
- **Signal state:** `DATA_SUFFICIENT = false` — badges show "Building data — check back in autumn". Do not change until autumn 2026.
- **Email:** Kit (ConvertKit) — Booking Alert form `7f784a323c`, Search popup form `f197f8f414`. Welcome sequence live.
- **Email alerts:** `clubmed_checker.py` only emails on genuine failures (>30% API error rate). All other alerts removed.
- **GA4:** `G-G2RES5DX0K` — live in both `clubmed/index.html` and `index.html`.
- **SSH key:** `~/.ssh/booking_window_deploy`
- **Checker flags:** `--test` (no writes), `--verify` (one API call), `--inject-only` (rebuild RESORT_DATA from CSV, no API calls)

(Resolved: winter 2026/27 bookings opened; prices now present for Dec–Apr.)

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
- 2026-05-04 — **5 fixes applied:** (1) `markwarner_prices.csv` header corrected to 15-column schema; (2) `bookingUrl` added to all 11 Club Med resorts in `clubmed_checker.py` + emitted into JS; (3) 5 occurrences of "cheapest" replaced in `clubmed/index.html` (meta tags → "most favourable pricing", sort labels → "lowest price first"); (4) Mobile touch fixes: `touch-action: manipulation` on all interactive elements, `-webkit-overflow-scrolling: touch` on modals, party-size filter selector scoped to `[data-party]`; (5) Sort bar added below party size tabs — Lowest price first / Highest price first / Biggest price drop.
- 2026-05-20 — **4 copy/UX fixes:** How It Works section removed from tracker + added to about.md; 'in 14 days' qualifier removed from movement badges; Saturday departures note removed from alert form; modal chart crash fixed (dynamic midIdx/lastIdx). (commit 7e2efe8)
- 2026-05-20 — **La Plagne 2100 resort code fixed LP2C_WINTER → PLAC:** LP2C_WINTER silently fell back to ARPC_WINTER (Les Arcs) in Club Med API; 280 corrupt rows in CSV since May 7. PLAC confirmed correct (year-round /y, 7-night only, season opens Dec 13 2026). Per-resort `durations` override added to `make_windows`. Stale-code filter (`resort_code` param) added to `load_price_history_from_csv`. CLAUDE.md resorts table corrected. (commit 6a9e323, merged 168c5ad)
- 2026-05-20 — **Daily Google Drive backup:** `backup_to_gdrive.sh` + `co.whentobook.backup.plist` (launchd, 03:00 daily). Backs up `_data/`, `clubmed/index.html`, `_posts/`, `_layouts/`, `.github/`, `*.py`, and key `.md` files → `WhenToBook_Backups/YYYY-MM-DD/` in Google Drive for Desktop sync. First backup confirmed successful. `.gitignore` created (excludes `backup.log`). (commits 9acc37e, merged 79eab59)
- 2026-05-20 — **Kit.com form bug fix:** Both email signup forms were posting JSON to the Kit.com public form endpoint, which silently accepted the wrong Content-Type and returned 200 without creating a subscriber. Fixed to `application/x-www-form-urlencoded` + `URLSearchParams`. Affects search popup (`f197f8f414`) and mobile booking alert (`7f784a323c`). (commits e009b51, merged fe8e411)
- 2026-05-21 — **Hero label + CTA:** "Best available price" → "Most Favourable"; "View price history →" button → "Book Now →" anchor linking to `resort.bookingUrl`. (commit c07fa97)
- 2026-05-21 — **Price movement guard:** `getPriceMovement()` returns 0 when price is missing/zero — prevents any `-£X` display for unavailable departures. (commit c07fa97)
- 2026-05-21 — **Footer redesign:** Both `clubmed/index.html` and `index.html` — dark teal background, white text, copyright WhenToBook, contact email, Privacy Policy, Terms of Use links, tagline. (commit c07fa97)
- 2026-05-20 — **Summer resort images:** 9 Wikimedia Commons CC-licensed photos added to `images/` for all summer resorts. `RESORT_IMAGES` in `clubmed/index.html` wired up so summer cards display real photos instead of gradient placeholders. (commit 6fd54b8)
- 2026-05-21 — **Booking URLs corrected (all 15):** All ski + summer `bookingUrl` values fixed — correct Club Med slugs and /y vs /w suffixes for year-round resorts. Fallback URL in modal and JS fixed. Search modal now uses resort-specific `bookingUrl` from entries. (commit c5cd8dc)
- 2026-05-21 — **Mobile resort modal table overflow fixed:** Departure table wrapped in scrollable div (`dept-table-wrap`). Book column hidden on mobile via `@media max-width: 600px` — `.modal-cta` button handles booking on mobile. (commit c5cd8dc)
- 2026-05-21 — **Peisey-Vallandry resort guide published** — per-resort blog post added to `_posts/`. (commit 742a5b3)
- 2026-05-21 — **14 new summer resorts added to checker** — `clubmed_summer_checker.py` now 24 resorts. Summer inject-only bug fixed (RESORT_DATA_SUMMER→SUMMER_RESORT_DATA). RESORT_META region strings for all new resorts. (commits 52ec961, 60af5ca)
- 2026-05-21 — **International ski checker launched** — `clubmed_ski_international_checker.py` for 8 resorts (Pragelato Sestriere, St. Moritz, 3 × Japan, 2 × China). Separate CSV + 09:00 UTC workflow. Ixtapa Pacific confirmed permanently closed. (commit 86d28c9)
- 2026-05-31 — **Three rendering bugs fixed** — (1) Hero card blank: crash in `renderCards` when 4 resorts had empty `departures[]` prevented `renderHeroBestCard()` from running — fixed with `if (!dep) return` guard + null-check in `getPriceMovement`. (2) Sparkline invisible for stable prices: flat line was placed at bottom of chart (range=0 → fallback of 1 caused y≈bottom) — fixed to render at h/2 midpoint. (3) RESORT_DATA stale: regenerated with resort_code filter (excludes LP2C_WINTER contamination). All resorts now have 8 combos. (commit 9bc85d7)
- 2026-05-31 — **Winter checker async rewrite** — Root cause of 12-day data gap found and fixed: `CSV_FILE` was `price_history.csv` instead of `prices_clubmed.csv`. Full async aiohttp rewrite (~20 min vs 5+ hours). Per-resort commit+push. Two dead summer resorts disabled (AGAC, BALC). inject-only LP2C_WINTER filter added. (commit 704473f)
- 2026-06-22 — **build_site.yml daily cron added** — GITHUB_TOKEN pushes don't trigger on:push; added 08:00 UTC cron so site rebuilds daily regardless. (commit 880cc5d)
- 2026-06-22 — **Mark Warner summer beach checker launched** — `markwarner_summer_checker.py` tracks 4 beach resorts: Aeolian Village (Lesvos, ID 26928), Lemnos (ID 8), Paleros (ID 19300), Phokaia/Turkey (ID 16797). 7+14 night durations, 3 party sizes, all available airports per resort. ~1,200 rows/day. Separate CSV `_data/prices_markwarner_summer.csv`. Cron 06:30 UTC. Seeded 2026-06-22. Resort IDs found via `:resort-id` HTML attr (not nav hash IDs). (commit f545b5d)
- 2026-06-23 — **Stub price fix in 4 articles** — LP2C_WINTER stubs (£2,874/£3,322 flat across all dates) replaced with real PLAC data (£3,054–£5,466 with genuine seasonal curve). Val d'Isère vs La Plagne article rewritten; La Plagne best-time article rewritten with correct resort code PLAC, 7-night durations, full season price table; Les Arcs article updated with current New Year price (£6,642); ski holiday prices article updated with VDIC New Year movement. (commit ee1ea4e)

- 2026-09-30 — **C1 build_site timeout fixed** (one-pass history index; inject-only ~5 s; build at 10:30 UTC)
- 2026-09-30 — **C2 summer checker split into 3 sequential batches**, concurrency 4, one-pass history cache
- 2026-09-30 — **Polite collection:** honest WhenToBookBot UA in all checkers
- 2026-09-30 — **Sole trader wording** across site, privacy and terms; CLAUDE.md non-negotiables added

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

### French Alps ski (11 — displayed in clubmed/index.html)

| Resort | Code | Departure |
|---|---|---|
| Tignes | `TIGC_WINTER` | Sunday |
| Les Arcs Panorama | `ARPC_WINTER` | Sunday |
| Peisey-Vallandry | `PVAC_WINTER` | Sunday |
| Valmorel | `VMOC_WINTER` | Sunday |
| Alpe d'Huez | `ALHC_WINTER` | Sunday |
| La Rosière | `LROC_WINTER` | Sunday |
| La Plagne 2100 | `PLAC` | Sunday (year-round /y, 7-night only) |
| Val d'Isère | `VDIC_WINTER` | Sunday |
| Grand Massif | `GMAC_WINTER` | TBC |
| Val Thorens Sensations | `VTHC` | Sunday (no `_WINTER` suffix) |
| Serre-Chevalier | `SECC_WINTER` | TBC |

### International ski (8 — CSV only, not yet displayed)

| Resort | Code | Region |
|---|---|---|
| Pragelato Sestriere | `PRAC_WINTER` | Italian Alps |
| St. Moritz Roi Soleil | `SMRC` | Swiss Alps (no `_WINTER` suffix) |
| Tomamu Hokkaido | `TOMC_WINTER` | Japan |
| Kiroro Peak | `KIPC_WINTER` | Japan |
| Kiroro Grand | `KIGC_WINTER` | Japan |
| Sahoro Hokkaido | `SAOC_WINTER` | Japan |
| Beidahu | `BEIC_WINTER` | China |
| Changbaishan | `CBAC_WINTER` | China |

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
clubmed/index.html                     — Club Med tracker (canonical live site)
index.html                             — Root brand landing page
WhentoBook.html                        — Redirect to /clubmed
clubmed_checker.py                     — Price checker (flags: --test, --verify, --inject-only)
markwarner_checker.py                  — Mark Warner ski checker (flags: --test, --verify); dormant May–Aug
markwarner_summer_checker.py           — Mark Warner summer beach checker (flags: --test, --verify)
backfill_prices.py                     — Gap-fill script (run after multi-day outage)
_data/prices_clubmed.csv               — Club Med price log (~27,000 rows, append-only)
_data/prices_markwarner.csv            — Mark Warner ski price log (append-only)
_data/prices_markwarner_summer.csv     — Mark Warner summer price log (1,198 rows seeded 2026-06-22, append-only)
vercel.json                 — Routing + security headers (Vercel only)
.github/workflows/
  price_checker.yml         — Club Med: daily 06:00 UTC
  markwarner_checker.yml    — Mark Warner: daily 07:00 UTC
  backup.yml                — Weekly CSV backup to GitHub Releases (Sundays 02:00 UTC)
When To Book/Agents/        — Agent .md files mirrored to vault (Obsidian)
```
