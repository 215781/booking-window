# When To Book — Plan

Current roadmap. Scribe keeps this updated. Orchestrator reads this at the start of every session.

Last updated: 2026-05-04

---

## Active / Up Next

- [ ] **Configure DNS** — set CNAME `www` → `215781.github.io` and A records for apex at the registrar. **User action required.**
- [ ] **Decide: GitHub Pages vs Vercel** — both deployments exist. Vercel is live. GitHub Pages is configured but DNS not set. Decide which is canonical and point DNS accordingly. **Product decision.**
- [ ] **Confirm `VMOC_WINTER` code** — a space was noted (`VMO C_WINTER`) in one session note. Verify the actual code in `clubmed_checker.py` against the API.
- [ ] **Grand Massif + Serre-Chevalier departure day** — both show Sat+Sun prices. Needs data accumulation to confirm correct departure day, then lock it in the checker.

---

## Backlog (future work, not yet prioritised)

- [ ] **Booking-window analysis script** — target Oct 2026 when price_history.csv has 6+ months of data. Group by resort + departure date, plot price vs days_before_departure, find inflection points at 180d, 90d, 60d, 30d, 14d, 7d.
- [ ] **Party composition: 3-adult / 4-adult** — deferred. User noted people can infer from 2-adult price.
- [ ] **Mobile responsiveness** — layout uses CSS Grid with fixed column counts; needs media queries for mobile.
- [ ] **Real resort photography** — card image areas are currently gradient placeholders.
- [ ] **Deep-link Club Med CTA** — "Book on Club Med" links go to homepage; should deep-link to specific resort once URL structure is confirmed.
- [ ] **SEO content** — individual resort pages, long-tail blog content ("best time to book Club Med La Plagne" etc.)
- [ ] **Affiliate programme** — apply to Awin once ~100 click-throughs are happening. ~3% commission, ~£150 per £5,000 booking.
- [ ] **Eurostar Snow ticket alert page** — tickets go on sale 9 July 2026 at ~8am. Build alert page before that date.
- [ ] **Mark Warner / Neilson tracker** — same ski audience, natural second site.

---

## Completed

- [x] Built single-file HTML/CSS/JS site (`WhentoBook.html`) — 2026-04-21
- [x] Python price checker (`clubmed_checker.py`) built and verified — 2026-04-21
- [x] GitHub Actions workflow set up (`.github/workflows/price_checker.yml`) — 2026-04-21
- [x] All 6 original resort codes verified via GraphQL API — 2026-04-21
- [x] Expanded to 11 resorts; all codes verified — 2026-04-26 to 2026-04-27
- [x] Scheduled checker live — daily at 06:00 UTC — 2026-04-28
- [x] `price_history.csv` has ~5,862 rows; 2,205 junk rows purged — 2026-04-28
- [x] Signal system: Favourable / Watch / Hold — 2026-04-26
- [x] Three-mode date search, modal search results, mobile layout, alpine card gradients, child age input — 2026-04-26
- [x] CNAME committed (`whentobook.co.uk`) — 2026-04-22
- [x] Cookie notice and `privacy.html` live — 2026-04-26
- [x] Vercel deployment fixed — `vercel.json` committed, rewrite `/` → `/WhentoBook.html` — 2026-04-28
- [x] Kit Cowork session: both forms configured, custom field, tags, welcome sequence live — 2026-04-28
- [x] Search popup wired to correct Kit form (`f197f8f414`) — 2026-04-28
- [x] Season price calendar view added to resort modal — 2026-04-26
- [x] Multi-agent workflow set up: CLAUDE.md, ORCHESTRATOR.md, BUILDER.md, SCRIBE.md — 2026-05-04
