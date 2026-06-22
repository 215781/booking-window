# Business Audit — whentobook.co.uk

**Prepared:** 2026-05-18  
**Auditor:** Independent analysis (not the orchestrator or builder)  
**Purpose:** Honest appraisal of the site's current state, earning potential, business viability, and a set of business plan foundations.

---

## Executive Summary

whentobook.co.uk is a price intelligence site tracking Club Med ski and summer resort prices daily. It has a genuinely differentiated proposition, a working data pipeline, a live website, and 11 published blog articles — all within approximately four weeks of its first commit. That is real execution pace.

However: the site went live yesterday. It has no organic traffic, no affiliate approval, no signal data to actually show visitors, and no real evidence yet that anyone will search for what it offers. The founding thesis — that financially savvy holiday buyers want to know *when* to book, not just *where* — is compelling and the competitive gap is real. But a gap in a market and a business are very different things. This audit is designed to map the distance between them honestly.

---

## 1. Site & Product Audit

### What the site actually does today

The tracker at `/clubmed` displays 11 French Alps ski resorts and 10 summer resorts in a card grid. Each card shows the resort name, a gradient placeholder image, a price movement badge (`↓ £X (−Y%)` or `— Stable`), and the current price for a 2-adult 7-night stay on the date with the biggest recent price drop. Clicking a card opens a modal with a price chart, a season calendar, and a booking CTA.

The signal system — the core product promise — is permanently disabled. Every resort shows "Building data — check back in autumn" instead of Favourable/Watch/Hold. This means visitors arrive at a site whose headline value proposition is explicitly not available. They see price movement numbers but no context for whether those movements are meaningful.

The hero section now shows a "best opportunity" card — the resort with the biggest recent price drop — which is a reasonable piece of editorial intelligence. The blog has 11 articles, all published in the last 12 days.

### Quality of the user experience

**What works well:**
- The visual design is clean and genuinely premium. The teal/amber/off-white palette, Playfair Display headings, and Inter body text hold up well against travel media comparables.
- The price movement badges (↓ £438 (−9%)) are the most scannable and compelling element on the page. They convey real information at a glance.
- The modal with a sparkline chart and season calendar is the right architecture — it rewards deeper investigation.
- The language discipline (no "deals/cheap/discounts") is consistently applied and correctly targeted at the audience.

**What doesn't work yet:**
- **Gradient placeholders everywhere.** Ten of eleven resort cards have CSS gradient images rather than photography. On a premium site targeting people who spend £5,000–£15,000 on a holiday, this reads as unfinished. It undercuts the trust signals the design is trying to build.
- **"Building data" on every resort.** Visitors arrive at a site that says, in effect, "come back in autumn." There is no reason to return without a prompt. Email capture is the only mechanism retaining anyone who lands today, and it depends on visitors trusting a site with no apparent track record enough to hand over their email address.
- **Thin sparklines.** Price charts in the modal currently have between 9 and 25 data points (roughly 26 days of real data, the rest backfilled from a single API snapshot). These charts show price variation across departure dates on a single day, not price change over time for a single departure. A visitor who reads the x-axis carefully will realise this is a price list, not a price history. That distinction matters enormously to the site's credibility.
- **No resort photography and no real-world credibility signals.** There is no "About" content, no author attribution, no founding story on the site itself (only in the content strategy documents). A financially savvy person encountering this site for the first time has no way to establish whether it is trustworthy or a placeholder.
- **Mobile audit outstanding.** The hero best-opportunity card was added yesterday and has not been verified on iOS Safari or Android Chrome. This is a known open item.

### How compelling is the core proposition to a ski holiday buyer?

Very compelling in theory. The founding story — two families, same resort, same week, £1,600 difference — is the kind of anecdote that lodges. Anyone who has ever felt stung by overpaying for a holiday will feel it.

But visitors cannot verify the proposition today. The signal system is off. The charts look like price lists. There is no "last year, we showed our subscribers this resort was rising — here's what happened to prices." There is nothing that proves the intelligence works. This is a trust problem that time and data will solve, but right now the site is asking visitors to trust a promise rather than evidence.

The strongest version of today's pitch is: *"Prices are already varying across the season — here's the cheapest date to book right now, and we'll tell you if they drop further."* That is useful. It just isn't the booking intelligence platform the site aspires to be.

### Known issues and gaps

- No resort photography
- Signal system disabled until autumn 2026
- Price charts show cross-date variation, not over-time trends (for most resorts)
- La Plagne 2100 shows no prices at all (booking window not yet open)
- Mobile layout unverified after hero card changes (2026-05-18)
- Summer tracker has zero data rows as of today (first run expected 2026-05-18 at 07:30 UTC)
- No affiliate links (not yet approved)
- No "About" page or trust signals beyond the cookie notice and privacy policy
- 10+ accumulated `.claude/worktrees/` directories in the repo (operational overhead; harmless to visitors but messy)

---

## 2. Data Collection Architecture

### How robust is it?

Reasonably robust for a solo-built MVP. The architecture is clean: GitHub Actions runs the checker daily, writes to a CSV, triggers an HTML rebuild. Separation of concerns is good (checker → CSV only; build workflow → HTML only). The async rewrite with rotating User-Agents and 429 backoff is sensible engineering.

The main structural risks:

**API dependency.** The Club Med GraphQL endpoint (`https://graphql.dcx.clubmed/`) has no auth requirement and no published API contract. Club Med could add auth, change the schema, or block GitHub Actions IPs at any time without notice. The checker already notes it is blocked from standard VPS IPs — which means Club Med is actively managing API access. GitHub Actions has worked so far because it uses shared IP ranges that haven't been blocked, not because there is any permission to scrape.

**Mark Warner is similarly fragile.** The `resortId` is scraped from page HTML and the endpoint is undocumented. One site redesign breaks the checker.

**Data continuity gaps.** The CSV has 24,380 rows spanning 2026-04-22 to 2026-05-17. Of those, 14,857 rows have actual prices — the remainder are empty (booking window not yet open for those departure dates). A significant portion of early data was backfilled from a single historical snapshot rather than daily collection, meaning the "price history" for some resorts is largely synthetic.

**Single point of failure.** One GitHub repository, one set of Actions, one person who understands the stack. If the checker silently fails (a bug that doesn't trigger the >30% error-rate email), data gaps accumulate without anyone noticing.

### Coverage

| Operator | Resorts | Data since | Rows | Notes |
|---|---|---|---|---|
| Club Med ski | 11 | 2026-04-22 | ~24,000 | ~26 days real + backfill |
| Club Med summer | 10 | 2026-05-18 | 0 | First run today |
| Mark Warner ski | 1 | 2026-05-07 | ~594 | One resort (Tignes only) |
| Sandals | 0 | — | 0 | Checker not built |

This is early-stage data collection. The moat of historical data — the site's core long-term asset — does not yet exist. It begins accumulating now.

### Data quality risks

The most significant quality risk is **stub prices**: prices that are present in the API but represent a placeholder rather than a real bookable offer. The LP2C_WINTER purge (328 rows at exactly £3,322) and the earlier 2,205-row junk purge illustrate this. If stub prices accumulate undetected in the live data, they will corrupt signal calculations and potentially mislead visitors.

The `data_quality_check.py` script exists to detect these anomalies, but it was built as an optional quality gate (with `continue-on-error: true`) so it never blocks data collection. That is the right call for uptime, but it means quality issues will land in production and require manual review to spot.

### What would production-grade look like?

- API responses validated against expected price ranges before writing to CSV
- Anomaly detection that flags (not just logs) sudden 100%+ price changes or prices that exactly match known stub values
- A monitoring dashboard (even a simple one) showing daily run status, row counts, and coverage across resorts and party sizes
- A second data source per operator (cross-validation) to detect when an API is returning stale or stub data
- Formal API access agreements — without which any data collection can be terminated at any time

---

## 3. Earning Potential

### Affiliate model viability

Club Med operates an affiliate programme through Awin (UK market). Commission rates are not publicly disclosed by Awin, but the ski travel affiliate market benchmarks run between 2% and 4% of booking value, with most operators at the lower end. The IMPROVEMENT_PLAN estimates 3% — that is a reasonable working assumption.

At 3% commission on an average Club Med ski holiday of £5,000 (two adults, one week):
- Per conversion: **£150**
- Per month at 1 conversion: £150
- Per month at 10 conversions: £1,500
- Per month at 30 conversions: £4,500

The challenge is conversion volume. Conversion rates for travel affiliate traffic typically run 1–3% of clicks, not visits. A visitor who clicks "Book on Club Med" from the site enters Club Med's own checkout flow, subject to Club Med's UX, pricing, and availability. The affiliate cookie is 45 days — good, but not infinite.

Mark Warner has a smaller addressable audience (one resort tracked, UK ski niche) and lower average booking values. It is a secondary consideration for now.

**Critical constraint:** The affiliate programme has not been applied for. Application requires demonstrable traffic (a suggested threshold of ~100 click-throughs). The site has been live for one day.

### Traffic requirements to generate meaningful revenue

Working backwards from revenue targets, with assumed conversion rates:

| Target | Affiliate conversions/month | Clicks required (at 2% click-to-book) | Visits required (at 5% click-through rate) |
|---|---|---|---|
| £1k/month | ~7 | ~350 | ~7,000 |
| £5k/month | ~33 | ~1,650 | ~33,000 |
| £10k/month | ~67 | ~3,350 | ~67,000 |

These are monthly visit targets. The site has zero measurable organic traffic today. Building to 7,000 monthly visits from SEO alone takes 6–18 months in a niche with any competition at all. The blog's 11 articles are a reasonable start, but ranking requires backlinks, time, and correct keyword targeting — none of which have been validated yet.

The traffic numbers above also assume visitors arrive in booking mode. Many will arrive in research mode (reading blog articles), which converts at a lower rate than someone actively comparing resorts.

### Email list as an asset

The Kit email list is the site's most valuable early asset because it converts casual visitors into a retainable audience. A subscriber who signed up eight months before their booking window opens has a very different lifetime value to a visitor who bounced.

The monetisation path for the email list:
1. Broadcast alerts when the Club Med flash sale opens (the 4-day early booking window) — high-intent moment, very likely to convert
2. Affiliate links in email (Kit allows this) — drives revenue without requiring return visits
3. Annual price intelligence reports — list growth mechanic, authority builder

An email list of 1,000 engaged subscribers in the ski audience is a more valuable commercial asset than 1,000 monthly visitors, because it can be reached directly at the exact moment they are making a booking decision.

**Current list size is unknown** — no data was captured in the files reviewed. This is a critical gap. The list size and engagement rate should be tracked and treated as a primary KPI from day one.

### What £1k/month, £5k/month, £10k/month requires

**£1,000/month:** Achievable within 12–18 months if SEO gains traction, the affiliate programme is live, and the email list reaches 500–1,000 subscribers. Requires consistent content output and one good ranking article.

**£5,000/month:** Requires 30,000+ monthly visits or a combination of 15,000+ visits plus a highly engaged email list of 2,000–3,000 subscribers. Probably 24–36 months from now, assuming no major setbacks and consistent execution.

**£10,000/month:** This is meaningful media business territory. Requires either very high traffic (60,000+ monthly visits), a much larger email list (5,000+), or diversification into additional operators and revenue streams (premium content, direct advertiser relationships, B2B data licensing). Not a near-term target.

---

## 4. Business Potential

### What kind of business is this?

It is currently a content and affiliate site with an intelligent data layer. Calling it a SaaS is premature — there is no subscription, no paywall, no API. Calling it a media property is more accurate, but the media model (advertising revenue) is not what is being built here.

The most accurate framing is: **a specialist affiliate publisher with a proprietary data moat.** The blog content drives SEO traffic; the tracker drives email signups; the email list drives affiliate conversions. The data moat (daily price history that competitors cannot instantly replicate) is the long-term defensible asset.

This business model is well-established and can generate significant passive income at modest traffic levels. It is not a venture-scale opportunity. It is an excellent lifestyle business, potentially a sellable media asset.

### Who are the natural acquirers or partners?

**Ski travel agencies** (Ski Solutions, Iglu Ski, Travel Club Elite, Born2Ski): These companies spend heavily on paid search to acquire Club Med leads. A site that pre-qualifies buyers with price intelligence and then routes them is worth money to these companies, either as an affiliate partner or acquisition target.

**Club Med itself:** Club Med's own data on price sensitivity and booking window behaviour is limited. A site that has independently built a longitudinal price database and an engaged audience is both a threat (it shows pricing volatility that Club Med might prefer not to be visible) and an asset (warm leads, audience insights). A direct commercial relationship or acquisition is plausible if the site reaches meaningful scale.

**Price comparison platforms** (Skiplagged, IgluSki, SnowTrex): The booking intelligence angle is differentiated from their offering, but they have the traffic infrastructure. Acquisition by a larger comparison platform is a realistic exit if the content and email list are substantial.

**Travel media companies** (Condé Nast Traveller, Ski+Board, The Times Travel): Brand partnership or white-label data relationships are possible if the data becomes genuinely predictive.

### Competitive landscape

There is no direct competitor doing what whentobook.co.uk does. This is confirmed by independent research. The closest alternatives are general ski price comparison sites (IgluSki, WeSki) which search current availability across many operators but have no historical tracking and no booking intelligence layer.

The absence of competition is both an opportunity and a warning sign. Markets often lack a product not because no one thought of it but because the economics don't support it. The lack of competitors could mean the addressable market is too small, the audience doesn't search for this, or the idea is genuinely novel and underserved. Based on the keyword research available, the latter appears most likely — but it has not been validated with real traffic data yet.

### What would make this defensible?

**Data depth.** Two years of daily price data for 11 resorts is very hard for a competitor to replicate quickly. One year of data is useful; two years of data across multiple booking cycles is genuinely proprietary.

**Email list quality.** An email list of 2,000+ subscribers who have opted in specifically for Club Med price alerts is a commercial asset that cannot be scraped or SEO-competed away.

**Content authority.** A site with 40–60 well-ranked articles on Club Med booking intelligence becomes the de facto reference in that niche. Once established, rankings are sticky.

**Brand.** A recognisable name in the ski community (ski forum mentions, travel agency word-of-mouth, Facebook Group recommendations) creates distribution that search algorithms cannot replicate.

**Multi-operator coverage.** A site tracking Club Med, Mark Warner, and Neilson simultaneously is much more useful to a ski buyer than one that tracks only Club Med. The operational complexity of building this also raises the barrier to imitation.

---

## 5. Risks & Drawbacks

### API dependency risk — HIGH

This is the most serious structural risk. The Club Med GraphQL endpoint has no published API contract and no commercial relationship with Drop Media Ltd. Club Med can and might:

- Add authentication (most likely scenario)
- Rate-limit or block GitHub Actions IP ranges
- Change the GraphQL schema
- Send a cease and desist letter

If Club Med blocks the scraper, the product stops working entirely. The data already collected retains value, but new data collection ceases. There is no fallback data source.

The Mark Warner API is equally fragile and additionally depends on a `resortId` embedded in page HTML.

**Mitigation options:** Explore official API or data partnership with Club Med; build a manual fallback (even monthly manual spot-checks); diversify to operators where APIs are more stable or licensed.

### Data accuracy and liability

The site makes implicit claims about prices. If a visitor relies on the displayed price data to make a booking decision and the data is wrong — due to API stub prices, data gaps, or stale cache — there is a reputational risk and potentially a legal risk (misleading information, particularly if affiliate income creates a commercial motive).

The current privacy policy and disclaimer situation should be reviewed: does it disclaim data accuracy? Is there any language that could be read as a guarantee of price accuracy?

This risk is manageable but not yet managed.

### Seasonal business model

Club Med ski bookings are seasonal: the booking window opens in February, departures run November through April, and the period of peak booking research activity is approximately August through January. Summer resort bookings overlap but do not fully compensate.

This creates real problems:
- **Revenue is lumpy.** Affiliate commissions will spike in the booking window and disappear in May–June.
- **Motivation risk.** Working on a site with no meaningful traffic in May–August, when the ski season is over and summer bookings are plateauing, is genuinely hard to sustain.
- **Competitor window.** Anyone who copies the idea has an 8-month window to build something before the next ski booking season.

The summer resort expansion is strategically important specifically because it fills the seasonal gap. But summer data collection has just started today (zero rows as of this audit), meaning summer signal data is at least a year away.

### SEO competition

The keyword space is not dominated by large incumbents, which is good. However:

- Club Med's own content team produces resort guides and booking advice. They have enormous domain authority.
- Ski media outlets (Ski+Board, Snow Magazine, the Telegraph Ski section) have strong backlink profiles and existing authority for ski keywords.
- Travel aggregators (IgluSki, SnowTrex) have commercial relationships and domain authority in ski booking keywords.

The "when to book Club Med [resort]" keyword cluster is low-competition and specific enough to rank with good content. But the broader "Club Med ski" space is contested. The site's best chance is to own the booking intelligence niche very specifically rather than competing broadly on generic ski content.

There is also an SEO timing concern: all 11 resort articles were published on 2026-05-17, the same day the site went live. Google will treat these as a cluster of new content from a new domain, not as evidence of topical authority built over time. The articles may not see meaningful ranking until the domain has accumulated age and backlinks.

### Legal and structural exposure

- **No company registration.** The site is operated under "Drop Media Ltd" but Companies House registration has not yet happened (per PLAN.md, it is a backlog item). Without registration, contracts cannot be signed, affiliate programme applications are personal rather than corporate, and the business has no legal existence separate from the individual.
- **No terms of service.** A site that displays price data and earns affiliate commissions from referrals arguably needs a ToS covering data accuracy, affiliate disclosure, and limitations of liability.
- **No affiliate disclosure.** The "Book on Club Med" CTAs are not currently flagged as affiliate links (they are not yet affiliate links), but once the programme is approved and links go live, ASA/FCA rules in the UK require clear affiliate disclosure.

### Single-founder / agent-built bus factor

The site is entirely dependent on one person who understands the stack (you) and a set of AI agents. If you step away, the GitHub Actions continue collecting data indefinitely, but:
- No one can interpret anomalies in the data
- No one can fix the checker when Club Med changes its API
- The blog stalls
- The email list depreciates

This is a standard solo-project risk. It becomes a material business risk only if the site reaches a scale worth protecting (£1,000+/month revenue). At that point, documentation and potentially a technical collaborator become important.

---

## 6. Business Plan Foundations

### One-line pitch

*"We track Club Med prices daily so you can book at the right moment — not just the right resort."*

### Target audience

**Primary:** UK-based families planning a Club Med ski holiday at premium French Alps resorts (Val d'Isère, Tignes, Les Arcs), with a household income sufficient to consider £5,000–£12,000 packages. Likely 35–55, may have been to Club Med before and are planning a return trip. They are not looking for the cheapest option — they are looking to avoid the frustration of overpaying for what they believe is a quality-consistent product.

**Secondary:** Couples (no children) at premium ski resorts; UK-based families considering Club Med summer beach resorts.

**Not the audience:** First-time ski holiday shoppers; budget-focused buyers; people who do not already know about Club Med.

### Revenue model

**Primary — Affiliate commissions (via Awin):**
Club Med ski bookings at approximately 3% commission, average booking value £5,000–£8,000. Target: 5–15 conversions per month at peak season. Revenue potential: £750–£2,250/month at peak, ~£500/month annualised in year two.

**Secondary — Email broadcast affiliate revenue:**
Direct links in email broadcasts during the Club Med flash sale window (February for ski, October for summer). A single well-timed broadcast to 1,000+ engaged subscribers at exactly the moment the sale opens could generate as many conversions as a month of organic traffic.

**Tertiary (future) — Expanded operator portfolio:**
Mark Warner and Neilson tracking pages, with separate affiliate relationships. Each operator adds incremental revenue from the same audience.

**Not currently viable but worth tracking:**
- Display advertising (requires 50,000+ monthly pageviews)
- Premium newsletter (subscription model requires 2,000+ subscribers with high engagement)
- B2B data licensing (requires much more data depth and a commercial relationship)

### 6-month milestones (May–November 2026)

**By end of June 2026:**
- Affiliate programme application submitted to Awin
- Companies House registration completed
- Terms of service and affiliate disclosure added to the site
- Resort photography in place (at least top 5 resorts by traffic)
- Mobile responsiveness verified and fixed
- Eurostar Snow alert page live (hard deadline: 9 July 2026)
- Email list size documented and tracked weekly

**By end of August 2026:**
- Affiliate programme approved and links live
- 20+ blog articles published (current: 11)
- Email list at 200+ subscribers
- First GA4 data showing which resorts and keywords drive traffic
- Summer data collection running cleanly (10 resorts, ~90 days of data)
- Mark Warner tracker UI built (even minimal) and data collection stable

**By end of October 2026 (critical milestone):**
- `DATA_SUFFICIENT = true` flag enabled — this is the moment the product actually delivers its core promise
- Booking-window analysis script producing the first real "when to book" intelligence output
- Club Med ski flash sale period: email broadcast to full list, first real affiliate revenue test
- Email list at 500+ subscribers
- Site has 6 months of consistent price data for all 11 ski resorts

**By end of November 2026:**
- First full ski season booking window open — this is peak revenue season
- Affiliate commissions flowing (target: first £500 in a single month)
- Annual price report drafted for email broadcast

### What needs to be true for this to be a real business vs a side project?

**It is a side project if:**
- The signal system never produces distinctive intelligence (i.e., the data shows that Club Med prices are flat or random, with no predictable booking window)
- Organic traffic fails to materialise after 12 months and 30+ articles (the keyword space may be smaller than it appears)
- Club Med blocks the scraper before sufficient data is collected
- The email list stalls below 200 subscribers (insufficient base for affiliate conversion volume)

**It becomes a real business (£1,000–£5,000/month) if:**
- The signal system activates in autumn 2026 and shows demonstrably useful patterns
- The email list reaches 500–1,000 subscribers with strong open rates (>40%)
- 2–3 blog articles rank on page 1 for their target keywords
- Affiliate commissions convert during the February 2027 flash sale window
- Summer resort expansion adds a year-round audience

**It becomes a sellable asset if:**
- Two+ years of clean price data across 20+ resorts
- 2,000+ email subscribers with documented engagement
- £3,000+/month consistent affiliate revenue
- A recognisable brand in the UK ski community

The window to make this decision is essentially now through autumn 2026. If the data from the first full ski booking cycle (opening June/July 2026) shows meaningful price variation and the signal system activates to produce genuine insight, the business case is strong. If prices are flat and the signals are uninformative, the core proposition needs rethinking.

---

## Summary Assessment

| Dimension | Rating | Notes |
|---|---|---|
| Product idea | Strong | Genuine gap, compelling proposition, financially savvy audience |
| Execution pace | Strong | Site live in 4 weeks, data pipeline running, 11 articles |
| Product readiness | Weak | Core promise (signals) disabled; no photos; charts misleading |
| Data depth | Early | 26 days real data; summer at zero; MW at 1 resort |
| Revenue readiness | Not ready | No affiliate approval; no traffic; no list size known |
| Architecture robustness | Moderate | Fragile API dependency; no commercial data agreement |
| Competitive position | Strong | No direct competitor; data moat compounds over time |
| Business risk | Moderate-High | API risk, seasonality, solo operator, no legal structure yet |
| 12-month revenue potential | £500–£2,000/month | If affiliate live + SEO gains traction |
| 3-year ceiling (realistic) | £3,000–£8,000/month | If expanded to multi-operator + summer |
| Acquirability | Possible | After 2 years data + email list + proven revenue |

**The honest bottom line:** This is a well-conceived, well-built, early-stage affiliate content business with a genuine data moat in the making. The founding thesis is sound. The execution quality is high. The commercial reality is that it is at day one of what will be an 18–24 month build before it generates meaningful revenue. The biggest risks are API fragility (outside your control) and SEO uncertainty (knowable within 6–9 months). The decision point is autumn 2026: if `DATA_SUFFICIENT = true` and the signals are interesting, double down. If the data turns out to be flat and uninformative, the site's value proposition needs recalibration — it would become a content and affiliate site rather than an intelligence platform, which is still viable but less distinctive.

The most important thing to do in the next 30 days is not build more features. It is: register the company, submit the affiliate application, get the Eurostar Snow alert page live before 9 July, and — critically — understand what your email list looks like today.
