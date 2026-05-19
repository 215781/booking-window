# When To Book — Plan V2

**Created:** 2026-05-18  
**Source:** Full business audit + site, language, visual, and content review  
**Purpose:** Comprehensive action plan to prepare the site for affiliate programme application and establish it as a credible, partner-positioned intelligence platform.

This document is split into two halves:

- **Section A — Owner actions:** Things only you can do. Agents cannot proceed with several of the agent tasks below until these are complete.
- **Section B — Agent tasks:** Fully scoped instructions ready to hand to Builder or Content Writer agents.

---

## SECTION A — OWNER ACTIONS

*These cannot be delegated to an agent. They are ordered by when they need to happen — not all are urgent right now. Read the timeline at the bottom of this document before starting.*

---

### A1 — Tax and legal status: nothing to do yet
You are operating as a sole trader under the UK trading allowance. The first £1,000 of self-employment income per tax year requires no registration with HMRC and no formal business structure. Given the realistic revenue trajectory — affiliate income unlikely before autumn 2026 — you will almost certainly remain below this threshold in the current financial year.

**What to do now:** Nothing.  
**What to watch:** Once affiliate commissions start arriving, track your cumulative income for the tax year. If you approach £1,000, register for self-assessment at https://www.gov.uk/register-for-self-assessment — it takes 10 minutes and is free. If revenue grows significantly (£3,000+/month consistently), revisit whether a Ltd company structure becomes tax-efficient at that point.  
**Blocker for:** Nothing currently.

---

### A2 — Set up a @whentobook.co.uk email address
**Status: ✅ COMPLETE — hello@whentobook.co.uk created via Zoho Mail (EU). DNS records added to Squarespace: 3×MX (mx.zoho.eu/10, mx2.zoho.eu/20, mx3.zoho.eu/50), SPF TXT (v=spf1 include:zohomail.eu ~all), DKIM TXT (zmail._domainkey). Allow up to 24 hours for full propagation. Verify at mailadmin.zoho.eu once propagated.**  
**Blocker for:** B3 (About page), B5 (footer update), A7 (Awin application)

---

### A3 — Write your founding story
**Status: ✅ COMPLETE — Founding story written and saved as `about.md` in repo root. Full page with styling, founding story, "What the site does today" section, and CTA. Agent task B3 should complete this page by adding the "What we track" and "Who we are / hello@whentobook.co.uk" sections per the original spec.**  
**Blocker for:** ~~B3 (About page)~~ (partially unblocked — agent completes it), B6 (hero pull quote)

---

### A4 — Decide on one header design for the whole site
**Status: ✅ DECIDED — Option 1 (dark teal header everywhere)**  
Apply the dark teal header currently used on blog/articles across the tracker (`clubmed/index.html`) as well. See agent task B1 for full implementation brief.

---

### A5 — Check your Kit email list size
**When:** This week — takes 5 minutes and the answer affects priorities.  
**Why:** The business audit flagged that list size is unknown. The email list is your most important early asset — more valuable at this stage than traffic. You need to know the baseline before anything else.  
**How:** Log in to Kit at app.kit.com → Subscribers → filter by tag (booking-alert, search-popup). Note: total subscribers, open rate on the welcome email, and which form is converting better.  
**What to do with the numbers:**
- Below 50 subscribers → email capture UX is a priority; consider whether the signup prompt is prominent enough
- 50–200 → on track; focus on content and traffic to grow it
- Above 200 → consider deepening the welcome sequence (backlog item MT-4) sooner  
**Blocker for:** Nothing — but informs priorities.

---

### A6 — Eurostar Snow (9 July 2026 deadline)
**Status: ✅ CONFIRMED — 9 July 2026 is the sale date.**  
Approach: blog articles only (already scheduled with Content Writer — no separate landing page build needed). No further action required from owner on this item.

---

### A7 — Apply to the Awin affiliate programme
**When:** Not until the site work in Phase 2 and Phase 3 (see timeline below) is complete. This is approximately 3–4 weeks away. Do not apply before the About page, expanded footer, unified header, and all 14 resort articles are live.  
**Why the wait matters:** An affiliate manager reviews your site at the moment of application. If they visit and find gradient placeholder images, a missing About page, an inconsistent header, and a thin footer, the application is weaker. The site needs to look like a complete, professionally maintained platform — not a work in progress. The copy fixes and structural work in this plan make a material difference to how the site reads to a reviewer.  
**How to apply:**
1. Go to https://www.awin.com/gb — create a publisher account in your own name, trading as "When To Book" or "Drop Media"
2. Search for the Club Med programme within Awin's advertiser directory
3. Apply describing the site as: *"A Club Med specialist booking intelligence platform. We track daily pricing across all 11 French Alps ski resorts and 10 summer resorts, and publish editorial content helping UK families understand the optimal booking window. We send warm, purchase-intent traffic directly to Club Med's booking pages."*
4. Do not mention scraping, API access, or automated data collection
5. Website URL to submit: `https://whentobook.co.uk/clubmed`

**Commission to expect:** ~3% of booking value, 45-day cookie window  
**Blocker for:** B14 (affiliate link integration — agent task, post-approval)

---

*(Duplicate A4/A5/A6 entries removed — see the live versions above.)*

---

## SECTION B — AGENT TASKS

*Each task below is fully scoped for a Builder or Content Writer agent. Tasks are grouped by theme and ordered by priority. Include the relevant task number when briefing an agent.*

---

## B-GROUP 1: STRUCTURAL & VISUAL

### B1 — Unify the site header across tracker and blog
**Agent:** Builder  
**File(s):** `clubmed/index.html`, `_layouts/post.html`, `blog/index.html`  
**Blocked by:** Owner must complete A6 first (design decision)  

**Brief:**  
The tracker (`clubmed/index.html`) uses a light sticky nav with the logo as serif text: `When To <span class="italic teal">Book</span>`. The blog (`_layouts/post.html`) and blog index use a dark teal `<header>` with a square "W" logo-mark box.

These must be unified into one consistent header used everywhere.

**If owner chose Option 1 (dark teal header everywhere):**  
Take the dark teal header from `_layouts/post.html` and apply it to `clubmed/index.html`. The nav links on the tracker header should be: Club Med Tracker · Blog · Set Alert (primary button). Remove the current light sticky nav from the tracker entirely. Ensure the dark header is not sticky (or if sticky, that it collapses to a slim bar on scroll — do not just copy the full-height header into a sticky context).

**If owner chose Option 2 (light nav everywhere):**  
Take the light sticky nav from `clubmed/index.html` and apply it to `_layouts/post.html` and `blog/index.html`. The nav links on the blog header should be: Club Med Tracker · Blog.

**Acceptance criteria:**  
- A visitor navigating from a blog article to the tracker sees the same header style  
- Logo links to `/` on all pages  
- No visual jarring or layout shift between pages  
- Mobile: header collapses cleanly on viewports below 600px  

---

### B2 — Reorder tracker page sections
**Agent:** Builder  
**File(s):** `clubmed/index.html`  

**Brief:**  
The current section order is:
1. Hero
2. Resort grid (signals)
3. Signal guide (Favourable/Watch/Hold explanation)
4. Email alerts (signup form)
5. How it works
6. Footer

This order is wrong for a site where all signals currently say "Building data — check back in autumn." The signal guide explains a feature that isn't active, before the method is explained or trust is established.

**Reorder to:**
1. Hero
2. Resort grid (signals) — keep here, it's the product
3. How it works — move up from last to third position
4. Email alerts (signup form) — now follows the method explanation
5. Signal guide — move to last (it will be most relevant once signals are live)
6. Footer

**Acceptance criteria:**  
- Sections appear in the new order in the rendered page  
- All anchor links in the nav (`#signals`, `#how-it-works`, `#alerts`) still resolve correctly after the reorder  
- No CSS or JS breaks from the reordering  
- Signal guide section is still present and complete — just repositioned  

---

### B3 — Build an About page
**Agent:** Builder  
**File(s):** Create `about.html` at root  
**Blocked by:** A2 (contact email), A4 (founding story from owner)  

**Brief:**  
The site has no About page. This is a critical gap for the Awin affiliate application — a reviewer needs to see who is behind the site and why it exists. Build a standalone `about.html` page matching the site's design.

**Content to include (owner provides the founding story text via A4 — agent formats and publishes):**

Structure:
1. **Header/nav** — same as the unified header (task B1, or use whichever is current pending B1)
2. **Page headline:** "About When To Book" (Playfair Display, teal)
3. **Section: The founding story** — owner's personal text, formatted in the site's body style. Lead with the two-families anecdote.
4. **Section: What we track** — two short paragraphs: Club Med French Alps ski (11 resorts, daily since April 2026), Club Med summer (10 resorts, from May 2026), Mark Warner ski (Tignes, from May 2026). Factual, neutral tone.
5. **Section: Who we are** — "When To Book is published by Drop Media Ltd, a UK media company. [hello@whentobook.co.uk](mailto:hello@whentobook.co.uk)" — use the email from A2.
6. **Footer** — same as site footer (see B5)

**Add About link to:**
- The tracker footer (`clubmed/index.html`)
- The blog footer (`_layouts/post.html`)
- The root landing page footer (`index.html`)

**Acceptance criteria:**  
- `about.html` exists and is accessible at `https://whentobook.co.uk/about`  
- Page uses the site's design tokens (teal, amber, Playfair Display, Inter, `#f5f0e8` background)  
- Contact email is linked with `mailto:`  
- About link appears in footers on tracker, blog, and root page  
- Sitemap updated to include `/about`

---

### B4 — Build an affiliate disclosure page
**Agent:** Builder  
**File(s):** Create `affiliate-disclosure.html` at root  
**Blocked by:** Nothing — can be built now. Uses "When To Book / Drop Media" as the entity name.  

**Brief:**  
Once the Awin programme is approved and affiliate links go live, UK ASA/CAP rules require clear disclosure. Build this page now so it is ready to activate immediately on approval.

**Content:**
- **Headline:** "Affiliate Disclosure"
- **Body (two paragraphs):**

  *"When To Book is an independent booking intelligence platform published by Drop Media Ltd. Our editorial content — including price tracking, resort analysis, and booking timing guidance — is produced independently and is not commissioned or influenced by any travel operator."*

  *"Some links on this site are affiliate links. When you click through and make a booking, we may receive a commission from the operator at no additional cost to you. This commission does not affect the price you pay, the resorts we track, or the signals we display. We only link to operators whose pricing we actively track and whose products we genuinely cover."*

- **Footer** — same as site footer

**Once built:**
- Add "Affiliate Disclosure" link to site footer (tracker, blog, root) — but do NOT activate this footer link until affiliate links are actually live. Add the link in an HTML comment for now: `<!-- <a href="/affiliate-disclosure.html">Affiliate Disclosure</a> -->` and note in PLAN.md that this should be uncommented when Awin approval comes through.

**Acceptance criteria:**  
- `affiliate-disclosure.html` exists  
- Page uses site design tokens  
- Footer link is present but commented out, with a clear code comment explaining why  

---

### B5 — Expand the site footer
**Agent:** Builder  
**File(s):** `clubmed/index.html`, `_layouts/post.html`, `blog/index.html`, `index.html`  
**Blocked by:** A2 (contact email), B3 (About page must exist first)  

**Brief:**  
The current footer on the tracker is: `© 2026 Drop Media Ltd · Blog · Privacy`. This is too thin for a site applying to an affiliate programme.

**Replace all footers with a unified footer containing:**
```
© 2026 Drop Media Ltd  ·  About  ·  Blog  ·  Privacy  ·  hello@whentobook.co.uk
```

- "About" links to `/about`  
- "Blog" links to `/blog`  
- "Privacy" links to `/privacy.html`  
- The email address is a `mailto:` link  
- Keep the same footer styling (teal background or minimal depending on which page)  

Note: the affiliate disclosure link will be added here later (see B4) — leave a code comment placeholder.

**Acceptance criteria:**  
- Footer is consistent across all four template files  
- All links resolve correctly  
- Email `mailto:` works  

---

### B6 — Add founding story pull quote to hero
**Agent:** Builder  
**File(s):** `clubmed/index.html`  
**Blocked by:** A4 (owner provides the story text)  

**Brief:**  
The hero section's left column has: section label → headline → hero subtitle. Below the subtitle there is a `.hero-quote` element (styled with a teal left border). This element exists in the CSS but may be empty or absent in the HTML.

Add a pull quote in the `.hero-quote` div using the founding story. Example text (owner should confirm or replace with A4 text):

> *"Two families. Same Club Med resort. Same week. One paid £1,600 more — not because they booked something different, but because they booked at a different moment in the cycle. This site exists to close that gap."*

**Acceptance criteria:**  
- Pull quote appears below the hero subtitle, above the best-opportunity card area  
- Uses the existing `.hero-quote` CSS styling (teal left border, Playfair Display italic)  
- Does not push the hero card below the fold on desktop viewports  

---

## B-GROUP 2: COPY & LANGUAGE

### B7 — Rewrite hero subtitle and Hold/Favourable signal descriptions
**Agent:** Builder  
**File(s):** `clubmed/index.html`  

**Brief:**  
Four specific copy changes across the tracker. Apply all four in a single commit.

**Change 1 — Hero subtitle**  
Find: `"We track Club Med availability and pricing so you can see if a resort is about to sell out, or if prices have recently dropped and now is a good time to book."`  
Replace with: `"We track Club Med availability and pricing daily — so you can see whether now is a well-timed moment to book, or whether the picture is likely to improve if you wait a little longer."`

**Change 2 — Hold signal summary text**  
Find: `"Stable conditions. Further drops are likely."`  
Replace with: `"The picture hasn't yet resolved in your favour."`

**Change 3 — Hold signal body text**  
Find: `"Price has risen recently, availability is comfortable, and the booking window suggests further drops are likely before the season closes. Patience is the rational position here."`  
Replace with: `"Prices are at or near a recent high and availability remains comfortable. The data suggests patience is the rational position — conditions are likely to become more favourable before the booking window closes."`

**Change 4 — Favourable signal body text**  
Find: `"Price is stable or has plateaued at a historically favourable level, or availability signals suggest further drops are unlikely. The data points toward acting now — but timing is yours to judge."`  
Replace with: `"Price has stabilised at a historically reasonable level, or availability signals suggest the booking window is narrowing. The data points toward acting now — but the decision is always yours."`

**Change 5 — How It Works Step 2**  
Find: `"the signals that Club Med's own site cannot give you"`  
Replace with: `"the kind of longitudinal context that only consistent daily tracking over time can reveal"`

**Acceptance criteria:**  
- All five strings replaced exactly as specified  
- No other copy changed  
- Commit message: "Copy: reframe signal descriptions and hero sub for partner positioning"

---

### B8 — Fix JS-generated modal narrative language
**Agent:** Builder  
**File(s):** `clubmed/index.html` (JS section, function `buildPriceNarrative`)  

**Brief:**  
The JS function `buildPriceNarrative` generates copy inside the resort modal. Two phrases use bargain-hunting language that contradicts the site's positioning.

**Change 1 — "lowest-priced week"**  
Find in `buildPriceNarrative`: `"The lowest-priced week currently available is"`  
Replace with: `"The most competitively priced week currently available is"`

**Change 2 — "seen a price drop"**  
Find: `` `${recentDrops} departure${recentDrops > 1 ? 's have' : ' has'} seen a price drop since the last check.` ``  
Replace with: `` `${recentDrops} departure${recentDrops > 1 ? 's have' : ' has'} moved in your favour since the last check.` ``

**Change 3 — Search modal results label**  
Find: `"All Sunday departures — ranked by price, lowest first"`  
Replace with: `"All Sunday departures — most favourable pricing first"`

**Change 4 — Search modal Kit form intro copy**  
Find: `"Let me know if there are improvements on these results."`  
Replace with: `"We'll notify you if conditions shift in your favour."`

**Acceptance criteria:**  
- All four strings replaced exactly  
- No JS logic changed — only string literals  
- Commit message: "Copy: fix JS modal narrative language for partner positioning"

---

### B9 — Fix article closing lines and standardise CTA boxes
**Agent:** Content Writer  
**File(s):** `_posts/2026-05-06-when-to-book-club-med-ski-holiday.md`, `_posts/2026-05-17-is-club-med-ski-worth-it.md`, and all other articles missing the CTA box  

**Brief:**  
Two copy fixes in existing articles, plus a standardisation pass across all articles to ensure every one ends with the teal CTA box.

**Fix 1 — "When to Book" article closing paragraph**  
File: `_posts/2026-05-06-when-to-book-club-med-ski-holiday.md`  
Find the final paragraph: `"The families who consistently pay less for the same Club Med resorts and the same ski weeks are not lucky..."`  
Replace "consistently pay less" with "consistently book at the right point in the cycle" — adjust surrounding sentence for flow.

**Fix 2 — "Is Club Med Worth It" article closing paragraph**  
File: `_posts/2026-05-17-is-club-med-ski-worth-it.md`  
Find: `"Booking a Christmas half-term week at full peak pricing without monitoring the cycle is how families end up paying £1,600 more than the family in the next chalet."`  
Replace with: `"The families who book with confidence are the ones who understand where current pricing sits in the cycle — not those who booked the same week without that context."`

**CTA box standardisation — apply to every article missing it:**  
The Val d'Isère article has the correct pattern. Every other article should end with the same teal CTA box before the `---` and related reading footer. Template:

```html
<div style="background:#f0ebe0;border-left:4px solid #1a4a42;padding:16px 20px;margin:32px 0;border-radius:0 6px 6px 0;">
<strong>Track [Resort] prices daily.</strong> The When To Book tracker monitors all departure dates across the 2026/27 season. <a href="/clubmed" style="color:#1a4a42;font-weight:600;">View live prices →</a>
</div>
```

For non-resort-specific articles (e.g. "When to Book", "Is It Worth It"):
```html
<div style="background:#f0ebe0;border-left:4px solid #1a4a42;padding:16px 20px;margin:32px 0;border-radius:0 6px 6px 0;">
<strong>Track prices before you book.</strong> The When To Book tracker monitors Club Med ski resort prices daily across all eleven French Alps resorts. <a href="/clubmed" style="color:#1a4a42;font-weight:600;">View the tracker →</a>
</div>
```

**Articles to check and fix:** All 11 articles in `_posts/`. Apply the CTA box to any that don't already have it.

**Acceptance criteria:**  
- Two closing-line edits applied  
- All 11 articles end with the teal CTA box in consistent format  
- No other content changed  
- Commit message: "Content: fix closing copy, standardise CTA boxes across all articles"

---

### B10 — Verify Val d'Isère "22 departure dates" claim
**Agent:** Builder (data check, not content)  
**File(s):** `_posts/2026-05-17-best-time-to-book-club-med-val-disere.md`, `_data/prices_clubmed.csv`  

**Brief:**  
The Val d'Isère article states: *"our tracker monitors Val d'Isère prices daily across all 22 departure dates in the 2026/27 season."* Verify this number is accurate.

Run: `grep "VDIC_WINTER,2A," _data/prices_clubmed.csv | awk -F',' '{print $5}' | sort -u | wc -l`

This counts unique departure start dates tracked for Val d'Isère, 2-adult party. If the count differs from 22, update the article to use the correct number.

**Acceptance criteria:**  
- Correct departure date count confirmed from CSV  
- Article updated if the number is wrong  
- Commit message includes the verified count  

---

## B-GROUP 3: NEW PAGES & SEO

### B11 — Write articles 11–13: Peisey-Vallandry, Grand Massif, Serre-Chevalier
**Agent:** Content Writer  
**File(s):** Create three new posts in `_posts/`  
**Blocked by:** B9 (CTA box standardisation — establish the template first)  

**Brief:**  
Complete the per-resort guide series for the three remaining ski resorts. Follow the exact format of the Val d'Isère article (`_posts/2026-05-17-best-time-to-book-club-med-val-disere.md`) — real price data from the CSV, seasonal breakdown table, value windows, booking timing advice, CTA box, related reading footer.

Before writing, pull current price data from the CSV for each resort:
- Peisey-Vallandry: `PVAC_WINTER`
- Grand Massif Samoëns Morillon: `GMAC_WINTER`
- Serre-Chevalier: `SECC_WINTER`

Target keywords:
- "best time to book Club Med Peisey-Vallandry"
- "best time to book Club Med Grand Massif"
- "best time to book Club Med Serre-Chevalier"

Each article: ~900–1,100 words. UK English. No banned words (deals, discounts, cheap, vouchers, savings). Update `sitemap.xml` after publishing all three.

**Acceptance criteria:**  
- Three new posts committed and pushed  
- Each uses real price data from the CSV (not invented figures)  
- Each includes a seasonal price table, value window analysis, and teal CTA box  
- Sitemap updated  
- Related reading footer links to at least two other articles  

---

### B12 — Mobile audit: hero best-opportunity card
**Agent:** Builder  
**File(s):** `clubmed/index.html`  

**Brief:**  
The hero section uses a two-column grid (`grid-template-columns: 1fr 1fr`). The right column contains the JS-rendered `#hero-best-card`. This layout was introduced in commit `5d7d42f` and has not been verified on small viewports.

Using browser DevTools responsive mode, check the hero section at:
- 375px width (iPhone SE / standard mobile)
- 390px width (iPhone 14)
- 414px width (iPhone Plus / Android)

Issues to look for and fix:
- Does the two-column grid collapse to single column on mobile? If not, add a media query at ≤768px: `grid-template-columns: 1fr`
- Does the best-opportunity card render below the headline on mobile (correct), or does it sit beside it, compressing both (wrong)?
- Is the "View price history →" CTA button large enough to tap (minimum 44px height)?
- Does the hero headline wrap gracefully at 375px, or does it overflow?

Fix any issues found. Test the resort card grid (3-column) also collapses correctly to 1-column on mobile.

**Acceptance criteria:**  
- Hero renders correctly in single-column on viewports ≤768px  
- Best-opportunity card appears below the headline on mobile  
- CTA tap target ≥44px height  
- Resort grid collapses to 1-column on mobile (or 2-column if preferred)  
- No horizontal scrolling at 375px  

---

### B13 — Fix Summer nav link
**Agent:** Builder  
**File(s):** `clubmed/index.html`  

**Brief:**  
The nav contains: `<a href="/summer">Summer</a>`. The `/summer` URL is now a redirect to `/clubmed`. Since ski and summer are both on the `/clubmed` page via a Ski/Summer toggle, this nav link should trigger the Summer toggle, not navigate away.

**Option A (preferred):** Change the nav link to an in-page action. Replace `<a href="/summer">Summer</a>` with a button or link that, on click, calls `switchSeason('summer')` (or whatever the season-toggle JS function is named) and scrolls to `#signals`.

**Option B (simpler fallback):** Change the href to `#signals` and add an `onclick` that calls the summer toggle function.

Check the existing season toggle JS to identify the correct function name before implementing.

**Acceptance criteria:**  
- Clicking "Summer" in the nav switches to the summer resort grid and scrolls to the signals section  
- No navigation to `/summer` or any redirect  
- The link still reads "Summer" in the nav  

---

## B-GROUP 3B: BUG FIXES

### B15 — Fix Kit form submission and consent checkbox
**Agent:** Builder  
**File(s):** `clubmed/index.html` (JS section — both alert form and search modal form)  
**Blocked by:** Nothing — fix immediately.

**Issue 1 — Wrong content type on Kit form fetch:**  
Both Kit form submissions use `Content-Type: application/json` with `JSON.stringify({email_address, fields})`. Kit's public form endpoint (`https://app.kit.com/forms/{id}/subscriptions`) expects `application/x-www-form-urlencoded`. Fix both fetch calls to use `URLSearchParams` and the correct content type:

```javascript
const params = new URLSearchParams();
params.append('email_address', email);
params.append('fields[resort_interest]', resortName);

fetch('https://app.kit.com/forms/7f784a323c/subscriptions', {
  method: 'POST',
  headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  body: params.toString()
})
```

Apply the same fix to the search modal form (form ID `f197f8f414`).

**Issue 2 — Consent checkbox may not be visually responding to clicks:**  
Investigate whether the checkbox `#alert-consent` and `#search-kit-consent` register clicks correctly. Check for any overlapping CSS elements or pointer-events issues. If the checkbox appears visually stuck, add `pointer-events: auto` to `.consent-label input[type="checkbox"]`.

**Acceptance criteria:**  
- Both forms submit via URL-encoded POST (correct for Kit public endpoints)  
- Checkbox visually toggles when clicked  
- A test submission with a real email reaches Kit subscribers  
- Commit message: "Fix: Kit form submission encoding and checkbox pointer events"

---

## B-GROUP 4: AFFILIATE READINESS

### B14 — Integrate affiliate links (POST-APPROVAL — do not action until Awin confirms)
**Agent:** Builder  
**File(s):** `clubmed/index.html` (all `bookingUrl` values in `RESORT_DATA`), all `_posts/` articles that contain "Book on Club Med" links  
**Blocked by:** A3 (Awin approval — this task must not be started until the approval email is received)  

**Brief:**  
Once Awin approval is confirmed, replace all Club Med booking links with affiliate tracking URLs.

**Steps:**
1. Log in to Awin publisher dashboard → get the Club Med deep-link builder URL format  
2. For each of the 11 ski resorts, generate a deep-link affiliate URL pointing to the specific resort booking page (e.g. `https://www.clubmed.co.uk/r/val-disere/y`)  
3. Update each `bookingUrl` in `RESORT_DATA` inside `clubmed/index.html` with the correct affiliate URL  
4. Update the summer resort `bookingUrl` values similarly for any summer resorts in `RESORT_DATA_SUMMER`  
5. In any blog articles that contain a direct link to `clubmed.co.uk`, wrap with the affiliate link or replace with the tracker `/clubmed` URL (do not add raw affiliate links mid-article — route through the tracker instead)  
6. Uncomment the affiliate disclosure footer link added in B4  
7. Add a one-line disclosure at the top of any article that contains direct affiliate links: *"This article contains affiliate links. If you book through them, we may earn a commission at no extra cost to you."*

**Acceptance criteria:**  
- All 11 ski resort `bookingUrl` values use Awin affiliate URLs  
- Affiliate disclosure footer link is active  
- Disclosure line appears at top of any article with direct affiliate links  
- Test a single link manually to confirm tracking fires (Awin provides a test tool)  

---

---

## KNOWN ISSUES / TO FIX

Issues identified during ops review. Fix before the next scheduled agent run or content cycle.

---

### KI-1 — CONTENT_QUEUE.md missing (Priority: fix before next content run)
The scheduled Content Writer task references `CONTENT_QUEUE.md` but the file does not exist. Without it the agent guesses the next topic each run, producing unpredictable results.

**Fix:** Create `CONTENT_QUEUE.md` at repo root with a prioritised article queue (resort name, target keyword, status: queued/in-progress/published). The Content Writer agent should read this file at the start of each run, pick the next queued item, and mark it in-progress.

---

### KI-2 — Scheduled task cannot push to GitHub (Priority: fix before next scheduled run)
The Content Writer scheduled task runs in a sandbox without `GITHUB_TOKEN` in the environment. Commits are made locally but the push fails with 403.

**Fix options:**
- Provision `GITHUB_TOKEN` in the scheduled task environment, or
- Add a host-side push step that runs after the task completes

**Until fixed:** after every scheduled content run, someone must manually run `git push origin main` from `~/booking-window`.

---

### KI-3 — La Plagne 2100 placeholder pricing
`_data/prices_clubmed.csv` shows uniform £2,874 across all La Plagne 2100 (`LP2C_WINTER`) weeks for 2-adult party. This looks like placeholder/fallback data rather than genuine daily variation.

**Investigation needed:** verify that `clubmed_checker.py` is querying `LP2C_WINTER` correctly. May need resort code verification against the GraphQL API. Cross-reference with `--verify` flag output.

---

### KI-4 — Homepage + UX changes (from user review)
Four UX improvements identified during review:

1. **Email signup form — move to floating button:** Replace the bottom-of-page signup form with a fixed-position "live chat style" button at bottom-right. Expands into the form on click. Form should remain fully functional.
2. **Remove £1,600 stat from homepage:** The founding story stat lives on the About page — it doesn't need to be repeated on the homepage too. Remove the reference from `clubmed/index.html`.
3. **Move "How WhenToBook works" explainer:** Relocate the "How It Works" section from the homepage to the About page. The homepage should focus on the product (resort grid + signals); the About page is where the method explanation belongs.

---

## TIMELINE — PHASED PLAN

The Awin application is the goal of this entire plan, but it sits at the end of Phase 3 — not the beginning. There is meaningful site work to complete first. Applying too early risks rejection from a site that still reads as a work in progress.

---

### Phase 1 — Immediate (this week)
*Goal: make all decisions, fix the things with no dependencies, check the Eurostar deadline.*

Owner actions this week — these are quick and unblock everything else:

| Action | Task | Time required |
|---|---|---|
| Set up hello@whentobook.co.uk | A2 | 30 minutes |
| Write founding story draft | A3 | 20 minutes |
| Decide: dark teal or light nav header | A4 | 5 minutes |
| Check Kit subscriber count | A5 | 5 minutes |
| Verify Eurostar Snow sale date | A6 | 10 minutes |

Agent tasks this week — no owner input needed, start immediately:

| Task | Agent | Description |
|---|---|---|
| B2 | Builder | Reorder tracker page sections |
| B7 | Builder | Hero + signal copy rewrites |
| B8 | Builder | JS modal narrative copy fixes |
| B10 | Builder | Verify Val d'Isère departure count |
| B12 | Builder | Mobile audit and fix (hero card) |
| B13 | Builder | Fix Summer nav link |
| B4 | Builder | Build affiliate disclosure page |

---

### Phase 2 — Next 1–2 weeks
*Goal: build the structural pages that make the site look like a complete, credible platform.*  
*Requires Phase 1 owner actions (A2, A3, A4) to be done first.*

| Task | Agent | Blocked by | Description |
|---|---|---|---|
| B3 | Builder | A2, A3 done | Build About page with founding story |
| B5 | Builder | A2, B3 done | Expand footer across all pages |
| B1 | Builder | A4 done | Unify header across tracker and blog |
| B6 | Builder | A3 done | Add founding story pull quote to hero |
| B9 | Content Writer | Nothing | Fix article closing lines + CTA box standardisation across all 11 articles |

---

### Phase 3 — Weeks 3–4
*Goal: complete the content set and do a final pre-application review.*

| Task | Agent | Blocked by | Description |
|---|---|---|---|
| B11 | Content Writer | B9 done | Write resort articles 11–13 (Peisey-Vallandry, Grand Massif, Serre-Chevalier) |

Once B11 is done, do a manual review pass of the full site. Check:
- All 14 resort guides are live
- Header is consistent on tracker, blog, and articles
- Footer has About, contact email, Privacy on every page
- About page is live and tells the founding story
- Hero subtitle and signal copy use partner-appropriate language
- Mobile renders correctly on the tracker

---

### Phase 4 — Apply to Awin (end of week 3 / start of week 4)
*Only when Phase 2 and Phase 3 are complete.*

| Action | Task | Notes |
|---|---|---|
| Submit Awin application | A7 | Full instructions in A7 above |

Awin typically takes 2–4 weeks to review and approve. The Club Med programme may take longer if it requires brand-side approval in addition to network approval. Apply and wait — do not chase within the first 2 weeks.

---

### Phase 5 — Post-approval (approximately 4–6 weeks from now)
*Only when Awin sends a confirmation email.*

| Task | Agent | Description |
|---|---|---|
| B14 | Builder | Integrate affiliate links across tracker and articles, activate disclosure footer link |

Also at this point: note your cumulative income for the tax year (A1 — HMRC £1,000 threshold to monitor).

---

## WHAT DOES "READY TO APPLY" LOOK LIKE?

This is the checklist to run through before submitting the Awin application at the end of Phase 3:

- [ ] About page live at `/about` with real founding story
- [ ] Contact email `hello@whentobook.co.uk` visible in footer
- [ ] Affiliate disclosure page built at `/affiliate-disclosure` (footer link still commented out)
- [ ] Consistent header design across tracker, blog, and all article pages
- [ ] Footer expanded with About · Blog · Privacy · contact email on all pages
- [ ] Hero subtitle rewritten (partner framing, not bargain framing)
- [ ] Signal descriptions (Hold/Favourable) rewritten
- [ ] How It Works Step 2 rewritten (remove "Club Med's own site cannot give you")
- [ ] JS modal copy fixed (no "lowest-priced", no "price drop")
- [ ] Mobile hero verified and fixed
- [ ] All 14 resort guides published (11 existing + 3 remaining)
- [ ] All articles end with consistent teal CTA box
- [ ] Summer nav link fixed (triggers toggle, not redirect)

The site does not need photography, an active signal system, or significant traffic to apply successfully. It needs to look like a serious, professionally maintained, editorially independent platform. The above checklist achieves that.
