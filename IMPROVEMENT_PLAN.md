# When To Book — Improvement Plan

*Researched and written: 2026-05-04*
*Author: Orchestrator agent*
*This document guides development priorities for the next 6–12 months.*

---

## How to use this document

Items are grouped into four time horizons. Each item includes: what it is, why it matters, rough effort, and dependencies. Use **PLAN.md** as the active task list; this document is the strategic context behind it.

---

## Full audit: current state of the site

### What is working
- 11 French Alps ski resorts tracked daily via GitHub Actions
- Price history CSV at ~5,862 rows and growing
- Signal badge system built (Favourable / Watch / Hold) — disabled pending data
- Three-mode date search (month / specific date / all dates)
- Search results modal with best price, month comparison, price movement
- Resort detail modal with season calendar and SVG price chart (1 data point per departure — charts will improve as data accumulates)
- SVG sparklines on resort cards
- Kit email integration: two forms (Booking Alert + Search popup), welcome sequence live
- Cookie notice and privacy.html
- Vercel deployment live (GitHub Pages partially configured — DNS not set yet)
- Mobile layout present with media queries (modals slide up from bottom)

### What is placeholder or incomplete
- **Resort images**: All card images are CSS gradient placeholders. No real photography.
- **"Book on Club Med" CTAs**: Links go to the Club Med homepage, not specific resort booking pages. Each resort has a URL like `clubmed.co.uk/r/val-disere/y` — these should deep-link to the correct resort.
- **Signal system**: Disabled with "Building data — check back in autumn" until DATA_SUFFICIENT is set to true. Target: autumn 2026.
- **Grand Massif + Serre-Chevalier departure days**: Both show Sat+Sun return prices. Need data accumulation to confirm which day is the true departure. Currently TBC.
- **VMOC_WINTER code**: One session note flagged a space (`VMO C_WINTER`). Needs verification against the API.
- **Mobile responsiveness**: Layout has media queries but CSS Grid uses fixed column counts on the signals section. Needs thorough testing on real devices.
- **Party size 3A / 4A**: Only 2 adults, 2A+1C, 2A+2C supported.

### What is not built yet (from original vision)
- Booking-window analysis script (needs 6+ months of CSV data — target Oct 2026)
- Real resort photography on cards
- SEO content (individual resort landing pages, blog posts)
- Affiliate programme (Awin) — not yet applied
- Eurostar Snow ticket alert page (hard deadline: **9 July 2026**)
- Mark Warner / Neilson tracker (second site)
- Price history charts populated enough to show trends (need more data)
- Analytics (no tracking installed)

---

## Research findings

### Club Med resort catalogue

**Ski resorts available from UK (15 total)**
- French Alps (11) — all currently tracked ✓: Val d'Isère, Tignes, Les Arcs Panorama, Grand Massif Samoëns Morillon, Alpe d'Huez, Val Thorens Sensations, La Rosière, Peisey-Vallandry, Valmorel, Serre-Chevalier, La Plagne 2100
- Italian Alps (1) — not tracked: Pragelato Sestriere
- Swiss Alps (1) — not tracked: Saint-Moritz Roi Soleil
- Canada (1) — not tracked: Quebec Charlevoix

**Beach / summer resorts (~45–50 globally)**
- Mediterranean/Europe: Magna Marbella (Spain), Palmiye (Turkey), Cefalù (Sicily), Marrakech La Palmeraie (Morocco), Gregolimano (Greece), Da Balaia (Portugal), La Palmyre Atlantique (France)
- Caribbean: Cancún (Mexico), Les Boucaniers, Punta Cana (Dominican Republic), Miches/Playa Esmeralda (Dominican Republic)
- Indian Ocean: Kani (Maldives), La Plantation d'Albion (Mauritius), Finolhu Villas (Maldives), Albion Villas (Mauritius), Seychelles
- Asia-Pacific: Bali, Phuket, Bintan Island, Cherating Beach (Malaysia), Guilin (China), Kabira Ishigaki (Japan)
- Other: Rio Das Pedras (Brazil), South Africa Beach & Safari (opening July 2026), Borneo (opening Nov 2026)

**Expansion pace**: Club Med plans to double in size by 2035. ~3–5 new resort openings/renovations per year, including one new mountain resort annually. Getting data collection started early is a strategic advantage.

### Booking window patterns

**Ski (Winter 2026/27)**
- Booking window opened: **early February 2026** — 9–10 months before first departures (Nov 2026)
- Launch offer: up to 20% early booking discount (15% on superior rooms, 20% on deluxe/suites)
- Offer had a hard deadline: **6 February 2026** — 4-day flash window
- After early window: prices typically stable through spring, then last-minute availability deals may appear

**Summer 2026**
- Booking window opened: **14 October 2025** — 7 months before first summer departures (May 2026)
- Flash sale window: **4 days only** (Oct 14–17, 2025)
- Discounts: up to 15% on superior rooms, 20% on deluxe/suites/villas
- Pre-booking form available from Oct 11 to lock in your quote before sale opens

**Pattern — what this means for the site:**
- There are two well-defined annual flash sale events (ski ~Feb, summer ~Oct)
- The site should specifically alert subscribers ahead of these sale windows
- The "best time to book" answer for Club Med is: *during the 4-day early booking flash sale*
- Data collected now will enable us to tell users: "This date has dropped from X to Y — now is a good moment relative to last year's opening price"

### Competitors

No direct competitor exists doing what WhenToBook does. This is a genuine gap.

The closest alternatives:
- **IgluSki / SnowTrex / WeSki** — general ski comparison; search hundreds of operators, no historical tracking, no booking intelligence
- **Club Med's own comparison tool** (`ski-comparison-tool.clubmed.co.uk`) — compares Club Med vs DIY; not a price tracker
- **Travel agents** (Ski Solutions, Iglu, Travel Club Elite, Born2Ski) — sell Club Med but have no price intelligence layer
- **Voucher sites** (weather2travel.com deals, travelclubelite.com) — discount code aggregators; different product

The WhenToBook value proposition is unique: *daily price tracking, historical context, booking signals, resort-specific intelligence*. No one else does this.

### Affiliate programme

- Club Med is on **Awin** (UK market), also TradeDoubler, Sale Gains, FlexOffers
- **Cookie duration**: 45 days (UK)
- **Commission rate**: Not publicly disclosed. Awin travel programmes typically run 2–4%. On a £5,000 booking at 3% = £150 per conversion.
- **Application threshold**: Apply once generating ~100 click-throughs. Don't mention the price tracking mechanism — position as a Club Med specialist content site.
- Currently, all "Book on Club Med" buttons link to clubmed.co.uk with `rel="noopener"`. When approved, swap to affiliate tracking links.

### Club Med GraphQL API

The existing endpoint (`https://graphql.dcx.clubmed/`) almost certainly works for all Club Med resorts — ski and summer — since it uses a resort code as the ID parameter. The original project briefing already confirmed `MMAC` (Magna Marbella) returns a price. The key differences for summer resorts:
- Different resort codes (need to discover via DevTools on clubmed.co.uk)
- Different departure patterns (some Saturday departures, some flexible, some 7 or 14 nights)
- Prices open earlier (October of prior year) so more data before first departures
- No concept of a "winter season" — pricing is year-round for beach resorts

---

## Quick wins
*1–2 sessions each. High value, relatively low effort.*

### QW-1: Fix deep-link Club Med CTAs
**What**: Every "Book on Club Med" button currently links to the Club Med homepage. Each resort has a known URL (`clubmed.co.uk/r/resort-slug/y`). Update the `bookingUrl` in RESORT_DATA and the modal CTA to link directly to the correct resort booking page.

**Why it matters**: Every visitor who clicks "Book" is a potential affiliate conversion. Sending them to the homepage loses the resort context and likely reduces conversion. Deep links also improve the user's experience. This is pre-work for the affiliate programme.

**Effort**: 1 hour. All `bookingUrl` values in RESORT_DATA already exist — they just need to be verified and formatted as direct booking pages rather than informational resort pages.

**Dependencies**: None. Does not require affiliate approval.

### QW-2: Verify VMOC_WINTER and TBC departure days
**What**: Confirm `VMOC_WINTER` is correct in `clubmed_checker.py`. Separately, determine the correct departure day for Grand Massif and Serre-Chevalier by checking the API and clubmed.co.uk, then lock them in the checker.

**Why it matters**: If VMOC_WINTER has a typo, Valmorel prices are not being collected correctly. Grand Massif and Serre-Chevalier showing "TBC" is sloppy and may mean we're checking the wrong day.

**Effort**: 1–2 hours (DevTools inspection + checker update).

**Dependencies**: None.

### QW-2b: URL architecture restructure — move Club Med to `/clubmed`
**What**: The site currently serves at the root (`whentobook.co.uk/`). Restructure so the Club Med tracker lives at `whentobook.co.uk/clubmed` and the root becomes a brand landing page listing all tracked operators. This mirrors how a portfolio brand grows: whentobook.co.uk → portal; `/clubmed`, `/markwarner`, `/sandals` → operator-specific trackers.

**Technical steps**:
1. Create `clubmed/` subfolder in the repo
2. Move `WhentoBook.html` → `clubmed/index.html`
3. Update `clubmed_checker.py` to write back to `clubmed/index.html` (not root `WhentoBook.html`)
4. Update `vercel.json` to serve `/clubmed` correctly and add 301 redirects from old paths
5. Update `sitemap.xml` and canonical URL tags inside the HTML
6. Build a minimal root `index.html` — brand landing page listing Club Med tracker (more operators added as they launch)
7. Update GitHub Pages config if applicable (Pages may need `clubmed/` configured)

**Why it matters**: This is a foundational architectural decision that becomes increasingly painful to change the longer the site generates backlinks and indexed pages. Doing it now (while traffic is minimal) costs almost nothing. Doing it in 12 months means a complex URL migration. The root URL structure also sets visitor expectations: `whentobook.co.uk` is a platform, not a single-operator site.

**Effort**: 2–3 hours. Most complex part is updating the checker script path and ensuring the Vercel routing is correct.

**Dependencies**: Should be done before any significant SEO work (MT-3), before deep-linking affiliate links (MT-1), and before any backlinks are acquired. Priority: near-term.

### QW-3: Eurostar Snow alert page
**What**: Build a standalone page (or section within WhenToBook) that: (a) explains Eurostar Snow tickets and why they sell out fast, (b) captures emails from people who want to be notified when tickets go live, (c) sends an alert on/before 9 July 2026 at ~8am.

**Why it matters**: Hard deadline of **9 July 2026** — 36 days away. Tickets go on sale at ~8am and cheapest fares (£99–125 each way) disappear within hours. There is no equivalent alert service. This is a genuine user need for anyone planning to ski via Eurostar.

**Effort**: 1 session — the Kit infrastructure is already in place, just need a new form + a simple page + a plan for sending the alert email.

**Dependencies**: Kit account (already set up). New form ID needed. Manual email send on 9 July.

### QW-4: Analytics
**What**: Add Plausible Analytics (privacy-friendly, no cookie consent required, £9/month or self-host free) or Fathom. At minimum, add a basic Google Analytics 4 tag.

**Why it matters**: Currently flying blind. No visitor data, no understanding of which resorts get most interest, which search queries drive conversions, or how the Kit email funnel performs. This is critical for prioritising future work.

**Effort**: 30 minutes to add a tracking script.

**Dependencies**: Choose a tool. Plausible recommended — matches the site's privacy-conscious positioning and doesn't require cookie consent banner update.

### QW-5: Real resort photography
**What**: Source real photography for the 11 resort card images. Club Med has a press kit; alternatively, use high-quality Unsplash ski resort imagery. Each card needs a hero image (approx 400x250px).

**Why it matters**: The gradient placeholders look unfinished. Real photography makes the site feel premium and trustworthy, which matters for the audience (financially savvy people who take Club Med holidays). Photography is also important for social sharing via the OG image.

**Effort**: 2–3 hours to source, optimise, and integrate images.

**Dependencies**: Hosting decision (images can be in the repo or referenced externally). Avoid very large images in the single-file HTML — reference external URLs or add to repo as separate files.

### QW-6: Improve OG image
**What**: The current OG image (`og-image.svg`) is an SVG that may not render correctly in all social preview contexts. Create a proper 1200x630 PNG OG image with the site's design language.

**Why it matters**: When someone shares the site on WhatsApp, X, or a Facebook group (where the audience lives), the preview image is the first impression. A good OG image dramatically improves click-through.

**Effort**: 30–60 minutes to design and add.

**Dependencies**: None.

---

## Medium term
*3–5 sessions each. Meaningful new features.*

### MT-1: Affiliate programme — apply and integrate
**What**: Apply to Club Med's Awin programme. Once approved, replace all "Book on Club Med" links with affiliate tracking links. Add a subtle "affiliate disclosure" line to the footer.

**Why it matters**: This is the primary monetisation path. A £5,000 booking at ~3% = £150 per conversion. The site sends people with genuine booking intent directly to Club Med — this is a very warm lead. Even 2–3 conversions per month = £300–450/month passive income.

**Effort**: Application takes 1 hour. Integration (swapping links) takes 2–3 hours. Approval typically takes 2–4 weeks.

**Dependencies**: Need ~100 organic click-throughs first (track with Analytics from QW-4). Apply once the site is live and has real traffic.

### MT-2: 6-night stay option and party size 3 adults
**What**: Add 3-adult party size to the search form and resort data. Also verify the 6-night stay data is being collected correctly (the checker may only query 7-night stays).

**Why it matters**: Many ski parties are 3 adults (e.g., two couples + a third wheel, or adult + two grown-up kids). The 6-night stay is a real option at Club Med and was already added to the UI — verify the checker queries it.

**Effort**: 2–4 hours (checker update for 3A party data, UI update for party size selector).

**Dependencies**: Requires checker changes → more data collection time before results appear.

### MT-3: SEO foundations — schema markup
**What**: Add proper schema markup (JSON-LD) for the site: `WebSite`, `TravelAgency`, and individual `Resort` entities. Also ensure JS-rendered resort content is available to search engines (static fallback or pre-rendered HTML).

**Why it matters**: Schema markup is a quick win for search engine understanding. Without it, Google doesn't know the site is a travel intelligence tool, not just a generic website.

**Effort**: 2 hours.

**Dependencies**: Do after URL architecture restructure (QW-2b) so canonical URLs are correct.

### MT-3b: Blog / content section
**What**: Build a blog at `whentobook.co.uk/blog` (or `whentobook.co.uk/clubmed/blog`). Since the repo is already on GitHub Pages (which runs Jekyll), the `_posts/` folder works natively. Each post is a Markdown file with Jekyll front matter.

**Key decisions**:
- Use Jekyll's native `_posts/` folder — zero additional infrastructure
- Create a `_layouts/post.html` that matches the site's design (Playfair Display headings, Inter body, `#f5f0e8` background, `#1a4a42` teal)
- Create a `blog/index.html` listing page
- RSS feed generated automatically by Jekyll

**Initial articles to write** (5 posts):
1. "When does Club Med release ski prices? The complete guide to the booking window"
2. "Best time to book Club Med Val d'Isère — price patterns explained"
3. "Club Med La Plagne 2100 vs Les Arcs Panorama — which offers better value?"
4. "Club Med ski holidays 2026/27: everything you need to know about pricing"
5. "Eurostar Snow 2026 guide: everything about the ski train from London"

**Why it matters**: Each well-ranked article is a recurring source of warm organic traffic. Target keywords have very low competition. A single article ranking on page 1 for "best time to book Club Med La Plagne" could generate 200–500 monthly visits from people in active booking research.

**Effort**: Blog infrastructure = 2–3 hours. Each article = 1–2 hours with AI assistance (see MT-3c below).

**Dependencies**: URL architecture restructure (QW-2b) first.

### MT-3c: Content Writer agent
**What**: Add a `CONTENT_WRITER.md` agent file to the repo. This agent's job is to research relevant topics, write SEO-optimised blog posts and guides, and publish them to the `_posts/` folder. Key instructions: target booking intent keywords, use the site's language rules (never "deals/discounts/cheap"), write in the brand voice, and add internal links between articles and relevant resort sections.

**Agent structure**:
- Research phase: use web search to understand what searchers want for a given keyword
- Drafting phase: write a 1,000–2,000 word article in Markdown with Jekyll front matter
- Publication: save to `_posts/YYYY-MM-DD-slug.md`, commit, and report back with target keyword and estimated search volume

**Why it matters**: SEO content is the single biggest long-term traffic driver but it's time-intensive. Having a dedicated agent with clear instructions means content can be produced in parallel with product development, without requiring the orchestrator to manage every word.

**Effort**: 1–2 hours to write CONTENT_WRITER.md. Each article ~30–60 mins of agent time.

**Dependencies**: Blog infrastructure (MT-3b) must exist first.

**Target**: 2 articles per month once the blog is set up.

### MT-4: Email sequence expansion
**What**: The welcome sequence currently fires on signup. Expand it to a 4–6 email series over 2–3 weeks:
1. Welcome (live) — what the site does, founding story
2. Week 1 — "How Club Med pricing works" — the early booking flash sale pattern
3. Week 2 — "Which resort is right for you" — brief resort comparison
4. Week 3 — "What to watch for in the next 30 days" — real data from the site

**Why it matters**: Email is the primary asset. A longer sequence means more touchpoints before someone books, and it positions the site as an authority, not just a data dashboard.

**Effort**: 2–3 hours to write and configure in Kit.

**Dependencies**: Kit account (already set up). Writing effort.

### MT-5: Price alert trigger — booking flash sale notification
**What**: Build a mechanism to send an email to all subscribers when Club Med opens its annual early booking flash sale. Specifically:
- Ski: Alert subscribers in late January/early February to watch for the ~4-day sale window
- Summer: Alert subscribers in mid-October to watch for the summer sale window

**Why it matters**: The single most valuable thing the site can do is tell people: "The Club Med sale opens tomorrow — here's what prices look like now vs. what they'll be at the discount." This is exactly what a financially savvy user wants.

**Effort**: 3–4 hours — build the alert logic in the checker or manually, configure a Kit broadcast.

**Dependencies**: Analytics (QW-4) for understanding audience size. Kit already set up.

### MT-6: Booking-window analysis script
**What**: A Python script that analyses `price_history.csv` and produces: (a) a chart of price vs. days-before-departure per resort, (b) identification of inflection points (180d, 90d, 60d, 30d, 14d, 7d).

**Why it matters**: This is the core intellectual output of the site — data-driven proof of *when* to book. Currently the site shows signals but can't yet explain *why* because data is insufficient. Once this runs, the site has genuinely proprietary insight.

**Effort**: 3–5 hours for the script. Results need 6+ months of data.

**Dependencies**: Must wait until at least October 2026. Target: autumn 2026.

---

## Expansion to summer resorts

### Why expand to summer/beach resorts?

1. **Same API** — the GraphQL endpoint works for all Club Med resorts. We already have the hard part.
2. **4× the audience** — ski is a winter hobby for a minority. Club Med beach resorts serve the full all-inclusive luxury travel market.
3. **Same audience psychology** — financially savvy people who hate overpaying, booking premium holidays direct with the operator.
4. **Longer data window** — summer prices open in October (~7 months before travel), giving more data before the booking window closes.
5. **First mover advantage** — no competitor is doing this for summer resorts either.

### Challenges

- **Volume**: ~45–50 summer resorts vs. 11 ski. Checking all of them daily would be ~4× the API calls and data volume. Start with a curated shortlist.
- **Data structure**: Departures vary more — some resorts offer flexible durations (7 or 14 nights), some Saturday departures. The checker would need to handle this.
- **UX complexity**: Users need a way to filter ski vs. beach, by region, by travel type. The current all-resorts design doesn't scale to 50+ resorts without navigation help.
- **Data accumulation lag**: Summer resort prices are brand new data — no historical comparison until year 2.
- **Audience expansion**: May bring a different audience who needs slightly different communication (less ski-specific framing).

### What needs to change technically

1. **Resort code discovery**: Each summer resort needs its code found via DevTools (same method as ski). The original project briefing already verified `MMAC` for Magna Marbella.
2. **Checker update**: Add summer resorts to `RESORTS` list in `clubmed_checker.py`. Handle variable departure days.
3. **Data model**: Add a `type` field to RESORT_DATA (`'ski'` / `'beach'`), a `region` field (already exists), and `season` field for when the resort is open.
4. **UI filter**: Add a tab or toggle for Ski / Beach / All at the top of the resort grid.
5. **Date dropdowns**: Summer resort dates need different month ranges (May–November typically).

### Phased approach

**Phase 1 — European summer resorts (2–3 sessions)**
Best starting point: 5–7 resorts that are closest to the existing UK ski audience.
- Magna Marbella (Spain) — verified in original API test, code `MMAC`
- Cefalù (Sicily, Italy)
- Gregolimano (Greece)
- Palmiye (Turkey)
- Marrakech La Palmeraie (Morocco)
- Da Balaia (Portugal)
- La Palmyre Atlantique (France)

These are the most accessible / budget-appropriate for a UK family-of-4 audience (shorter flights, lower total cost than Caribbean/Indian Ocean). They're also UK-facing resorts with pricing in GBP.

**Phase 2 — Caribbean (1–2 sessions)**
Once Phase 1 is established:
- Cancún (Mexico)
- Punta Cana (Dominican Republic)
- Les Boucaniers

**Phase 3 — Indian Ocean and Asia (1–2 sessions)**
Longer-haul, higher-spend audience. Potentially different visitor:
- Kani and Finolhu Villas (Maldives)
- La Plantation d'Albion and Albion Villas (Mauritius)
- Phuket, Bali

**Phase 4 — Remaining ski resorts (1 session)**
- Pragelato Sestriere (Italy) — adds Italian Alps
- Saint-Moritz Roi Soleil (Switzerland) — adds Swiss Alps

### UI changes needed for summer expansion

1. **Resort type filter**: "Ski" / "Beach & Sun" tabs above the resort grid
2. **Season indicator**: Each resort card should show when it's open (e.g., "Oct 2026 – May 2027" for ski; "May – Nov 2026" for summer)
3. **Region filter**: Once 20+ resorts are tracked, a region dropdown (French Alps / Mediterranean / Caribbean / Indian Ocean) helps users navigate
4. **Date range update**: The month dropdown needs to cover May–November for summer resorts
5. **Hero copy update**: Change "Club Med ski resort price intelligence" to "Club Med price intelligence" once beach resorts are live

---

## Long term and growth
*Beyond 6 months. Strategic and revenue-generating.*

### LT-1: SEO content expansion
**What**: 20–40 long-form articles targeting booking intent keywords:
- "best time to book Club Med [resort name]"
- "Club Med [resort] price history"
- "Club Med Val d'Isère vs Tignes — which is better?"
- "When does Club Med release ski prices for 2027?"
- "Is Club Med ski worth it in 2027?"

**Why it matters**: Each well-ranked article is a recurring source of warm organic traffic. A site ranking for 30 low-competition ski keywords could generate 1,000–5,000 organic visits/month. These visitors are in research mode — exactly when they're most receptive to booking intelligence.

**Effort**: Ongoing. 2–4 hours per article.

### LT-2: Affiliate income at scale
**What**: Once Awin-approved and generating 200–500 clicks/month, negotiate directly with Club Med's affiliate team for better rates or exclusive offers. Explore secondary affiliate options (ski insurance via InsureandGo/Direct Line, Eurostar, Geneva transfer services).

**Why it matters**: 500 clicks/month × 3% conversion × £150 average commission = **£2,250/month** in affiliate income. At scale this is a significant passive income stream.

**Effort**: Ongoing relationship management. No additional code changes.

### LT-3: Mark Warner / Neilson tracker (second site)
**What**: Apply the same model to Mark Warner and Neilson Holidays — two ski operators with similar premium all-inclusive positioning and a direct-booking model. Both serve the same Club Med audience.

**Why it matters**: Natural second site in the portfolio. Much of the infrastructure (checker design, CSV logging, signal system) can be reused. New moat: their APIs/pricing mechanisms.

**Effort**: 2–3 sessions to build. Requires new domain, new API research.

**Dependencies**: WhenToBook must be stable and generating some revenue first.

### LT-4: Eurostar Snow seasonal service
**What**: Beyond the one-time ticket alert (QW-3), build a proper Eurostar Snow price tracker — tracking prices for the ski train routes across the season, showing when tickets are released, and sending alerts for flash sales.

**Why it matters**: The existing audience (Club Med ski bookers) is exactly the audience for Eurostar Snow. Natural cross-sell. Eurostar tickets are released in tranches and have complex pricing — the same intelligence gap that exists for Club Med exists here.

**Effort**: 2–3 sessions. Requires API research on Eurostar pricing.

### LT-5: Price comparison editorial content
**What**: Annual "Club Med price report" — published each September/October — showing how prices for each resort have moved over the summer. Distributed via email to the whole list. Designed to be shared.

**Why it matters**: High-value email content that cements the site's authority and drives sharing. If 10% of readers forward it or share it, it compounds the list growth.

**Effort**: 1–2 hours to compile + write per year (once booking-window analysis script is built).

### LT-6: Drop Media Ltd portfolio development
**What**: Register Drop Media Ltd on Companies House (£12, 15 mins). Build a simple portfolio page (dropmedia.co.uk) linking the sites. This enables cross-portfolio email marketing with a single consent statement.

**Why it matters**: Legitimises the business structure. Enables email cross-selling between portfolio sites (Club Med audience → Eurostar Snow → Mark Warner etc.) under a single legal entity.

**Effort**: Companies House registration = 30 mins. Portfolio site = 1–2 hours.

---

## Priority order for the next 6 months

| Priority | Item | Deadline / Target |
|---|---|---|
| 🔴 URGENT | QW-3: Eurostar Snow alert page | Before 9 July 2026 |
| 🟡 Soon | QW-2b: URL architecture restructure (`/clubmed`) | Before SEO work starts |
| 🟡 Soon | QW-2: Verify VMOC_WINTER + departure days | Next session |
| 🟡 Soon | QW-1: Fix deep-link Club Med CTAs | Next session |
| 🟡 Soon | QW-4: Analytics | Next session |
| 🟢 Next month | QW-5: Real resort photography | May–June 2026 |
| 🟢 Next month | QW-6: OG image | May–June 2026 |
| 🟢 Next month | MT-3: SEO schema markup | May–June 2026 |
| 🟢 Next month | MT-3b: Blog/content section + Jekyll setup | May–June 2026 |
| 🟢 Next month | MT-3c: Content Writer agent (CONTENT_WRITER.md) | May–June 2026 |
| 🟢 Next month | MT-4: Email sequence expansion | June 2026 |
| 🔵 Autumn 2026 | MT-1: Affiliate programme | When ~100 click-throughs |
| 🔵 Autumn 2026 | MT-6: Booking-window analysis script | Oct 2026 (6 months data) |
| 🔵 Autumn 2026 | DATA_SUFFICIENT = true | Autumn 2026 |
| 🔵 Autumn 2026 | Summer resort expansion Phase 1 | Oct 2026 (before summer 2027 booking window) |

---

## Key strategic insight

The founding thesis is sound and the market gap is real. No competitor tracks Club Med prices over time or gives booking intelligence. The data collection advantage compounds: every day WhenToBook collects prices, it widens its moat against anyone who might try to copy the idea.

The most important near-term action is the **Eurostar Snow alert page** — this is a one-time event with a hard deadline and a guaranteed interested audience. Miss July 9 and the opportunity is gone for a year.

The most important medium-term action is **affiliate integration** — this converts the value WhenToBook is delivering (warm leads to Club Med) into revenue.

The most important long-term action is **summer resort expansion** — this transforms the site from a ski niche into a full Club Med intelligence platform, multiplying the addressable audience by 4×.
