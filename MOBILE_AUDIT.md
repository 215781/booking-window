# Mobile UX Audit — whentobook.co.uk
**Date:** 2026-05-19  
**Scope:** `index.html` (root landing) + `clubmed/index.html` (tracker)  
**Viewport target:** 375px–430px, touch interface, Google organic arrival

---

## 1. Layout & Readability on Mobile

### index.html (root landing page)

**What a user sees first (375px):**
The header (teal bar, ~60px) + hero headline ("Book at the right moment. Every time.") + one line of body copy. The headline uses `clamp(36px, 5vw, 56px)` — at 375px, 5vw = 18.75px, so the clamp floor of 36px applies. That's workable for Playfair Display but it's still a large, heavy serif that pushes content down. The subline is 18px with no mobile reduction, which is actually fine. The operator cards begin near the fold.

**Operator grid:**
`repeat(auto-fit, minmax(260px, 1fr))` at 375px with 20px side padding gives ~335px of content width, so one column fires. Cards stack correctly. However, operator card padding is `32px 28px` — no mobile reduction is defined, which means cards have significant internal whitespace that wastes space on a small viewport. The "coming soon" cards are dead — they add scroll weight for zero value on mobile.

**Nav at mobile:**
No hamburger, no mobile collapse. On `index.html` the two nav links ("Club Med tracker", "Blog") are 13px with no touch-size protection. They'll render on a single line at most widths, but the tap targets are extremely small — estimated ~30px tall including header padding. An accidental tap is very likely.

**Missing mobile breakpoint on index.html:**
`index.html` only reduces padding at 600px. There is no reduction of font sizes, no adjustment to hero spacing, and no treatment of the nav link touch sizes. It's a simple page, but the omission is notable.

---

### clubmed/index.html

**What a user sees first (375px, portrait):**
At 375px the hero stacks correctly (900px breakpoint fires). A user sees: the teal header with "Set Alert" button → section label → `h1` at 30px → `hero-sub` paragraph → the £1,600 blockquote → *then* the search form below it. That is a very text-heavy scroll before reaching any interactive content. The search form (hero-form-wrap) is buried below four text blocks.

**Font sizes:**
- Hero headline: 30px on mobile — acceptable, but Playfair Display at 30px on 375px is tight with the line-height of 1.15.
- Hero sub: 16px — fine.
- Section labels: 11px, letter-spacing 0.2em — dangerously small at mobile; readable but marginal.
- Card name: 18px — good.
- Card price / muted data: 11–14px — acceptable for secondary info.
- The `.modal-title` is reduced to 20px on mobile ✓.
- The dept-table inside the modal uses 13px — this table has no responsive treatment. On a 375px modal it will overflow horizontally (see section 4 below).

**Critical CSS bug — inline style overrides breakpoint padding:**
Three sections use `style="padding:80px 0;"` as inline attributes:
```html
<section id="signals" class="section" style="padding:80px 0;">
<section id="how-it-works" class="section" style="padding:80px 0;">
<section id="alerts" class="section" style="padding:80px 0;">
```
The media query `@media (max-width: 600px) { .section { padding: 48px 0; } }` is **completely overridden** by these inline styles. On mobile, all three sections have 80px top/bottom padding instead of 48px. This is a real bug — it adds roughly 190px of unnecessary whitespace to the page on mobile.

---

## 2. The Email Signup Form — Floating Widget Proposal

### Assessment

The current alert form sits at the bottom of a long page. On mobile, a user who arrived from Google has to scroll past: hero → search results → 11 resort cards (single column) → "How It Works" (3 steps) → the full form section. That's approximately 3,500–4,000px of scroll on a 375px viewport. The form is functionally invisible.

**The floating chat-style widget idea is good UX for this use case.** Specifically:
- The action is low-commitment ("just leave your email") and benefits from ambient availability — the user shouldn't have to seek it out.
- It mirrors patterns users already understand from Intercom/Drift/Crisp without the overhead of those tools.
- The form itself is only 4 fields + a checkbox + a submit, which is achievable in an expanded widget panel.
- On mobile it should NOT auto-expand or draw attention on page load — that's intrusive. It should sit quietly and be available when the user decides they're interested.

**Risk:** A floating widget that's badly sized or positioned will obscure resort card content. Must be implemented carefully (see spec below).

### Implementation Spec

**HTML Structure:**
```html
<!-- Floating Alert Widget -->
<div id="alert-widget" aria-label="Set a booking alert" role="complementary">
  <button id="alert-widget-trigger" aria-expanded="false" aria-controls="alert-widget-panel">
    <svg><!-- bell icon, 20×20 --></svg>
    <span class="widget-trigger-label">Get Alerts</span>
  </button>
  <div id="alert-widget-panel" role="dialog" aria-modal="false" aria-label="Set booking alert">
    <div class="widget-header">
      <span class="widget-header-title">Set a Booking Alert</span>
      <button class="widget-close" aria-label="Close">&times;</button>
    </div>
    <div class="widget-body">
      <!-- Same form fields as current #alert-form, deduped into this widget -->
      <!-- On submit, posts to Kit; shows inline confirmation -->
    </div>
  </div>
</div>
```

**CSS Positioning:**
```css
#alert-widget {
  position: fixed;
  bottom: 24px;
  right: 20px;
  z-index: 900;  /* below modals at z-index 1000 */
}

/* The trigger button */
#alert-widget-trigger {
  display: flex;
  align-items: center;
  gap: 8px;
  background: var(--amber);
  color: #fff;
  border: none;
  border-radius: 28px;           /* pill shape */
  padding: 14px 20px;
  font-family: 'Inter', sans-serif;
  font-size: 13px;
  font-weight: 600;
  letter-spacing: 0.04em;
  box-shadow: 0 4px 16px rgba(138, 106, 42, 0.4);
  cursor: pointer;
  min-height: 52px;              /* well above 44px touch minimum */
  min-width: 52px;
  transition: transform 0.15s, box-shadow 0.15s;
}

#alert-widget-trigger:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(138, 106, 42, 0.5);
}

/* On very small screens, collapse to icon-only */
@media (max-width: 400px) {
  .widget-trigger-label { display: none; }
  #alert-widget-trigger { padding: 14px; border-radius: 50%; }
}

/* The expanded panel */
#alert-widget-panel {
  position: absolute;
  bottom: calc(100% + 12px);
  right: 0;
  width: 320px;
  background: var(--card-bg);
  border: 1px solid var(--border);
  box-shadow: 0 8px 40px rgba(0, 0, 0, 0.18);
  border-radius: 4px;
  
  /* Hidden state */
  opacity: 0;
  pointer-events: none;
  transform: translateY(12px) scale(0.97);
  transform-origin: bottom right;
  transition: opacity 0.2s ease, transform 0.2s ease;
  max-height: calc(100vh - 120px);
  overflow-y: auto;
}

/* Open state — toggled by JS adding .open to #alert-widget */
#alert-widget.open #alert-widget-panel {
  opacity: 1;
  pointer-events: auto;
  transform: translateY(0) scale(1);
}

#alert-widget.open #alert-widget-trigger {
  background: var(--teal);      /* colour shift signals "active" */
}

/* On narrow phones, panel goes full-width from bottom */
@media (max-width: 400px) {
  #alert-widget-panel {
    position: fixed;
    bottom: 80px;
    right: 8px;
    left: 8px;
    width: auto;
  }
}

.widget-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px 12px;
  border-bottom: 1px solid var(--border);
}

.widget-header-title {
  font-family: 'Inter', sans-serif;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--text-muted);
}

.widget-close {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: var(--text-muted);
  min-width: 32px;
  min-height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.widget-body {
  padding: 16px 20px 20px;
}
```

**JS Behaviour:**
```javascript
const widget = document.getElementById('alert-widget');
const trigger = document.getElementById('alert-widget-trigger');
const closeBtn = widget.querySelector('.widget-close');

trigger.addEventListener('click', () => {
  const isOpen = widget.classList.toggle('open');
  trigger.setAttribute('aria-expanded', isOpen);
  if (isOpen) {
    // Focus first form field after animation completes
    setTimeout(() => widget.querySelector('select,input')?.focus(), 220);
  }
});

closeBtn.addEventListener('click', () => {
  widget.classList.remove('open');
  trigger.setAttribute('aria-expanded', 'false');
  trigger.focus();
});

// Close on outside click
document.addEventListener('click', (e) => {
  if (widget.classList.contains('open') && !widget.contains(e.target)) {
    widget.classList.remove('open');
    trigger.setAttribute('aria-expanded', 'false');
  }
});

// Close on Escape
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape' && widget.classList.contains('open')) {
    widget.classList.remove('open');
    trigger.focus();
  }
});
```

**What happens on tap:** Tap the amber pill → panel scales/fades in from bottom-right origin over 200ms → focus moves to first field. Tap X or outside → reverse animation. On confirmation, show inline success message, then auto-close after 3 seconds. The existing `#alerts` section at the bottom of the page can be kept as a secondary fallback (or removed as part of the content restructure below), but the widget replaces it as the primary capture mechanism.

**One important constraint:** The widget trigger must not overlap the resort cards' "tap to open" affordance. At bottom: 24px, right: 20px on a 375px viewport, the trigger sits over empty page margin at the bottom of a card row, not over card content. Acceptable.

---

## 3. Reducing Text on the Homepage

### What belongs on the homepage (clubmed/index.html)

The homepage should answer one question: *Is now a good time to book my Club Med ski holiday?* Everything else is secondary.

**Remove from homepage:**
- The £1,600 blockquote in the hero. This is great copy but it's explanation, not action. It belongs in the About page's "why we built this" narrative. The user arriving from Google already has intent — they don't need persuading, they need the data.
- The entire "How When To Book Works" section (steps 01/02/03). This is useful for sceptics and return visitors, but it's ~400px of scroll for a user who just wants to see the resort signals. Move it to the About page.

**Keep on homepage:**
- The hero headline and sub-copy: short, clear, purposeful.
- The hero search form (search by resort + travel month): this is the primary action.
- The resort signal grid: this is the product.
- The signal guide (Favourable/Watch/Hold definitions): this is necessary context for interpreting the cards. It's short and earns its place.
- The floating alert widget (replacing the current full-width form section).

**Recommended homepage copy structure:**

```
[Header]

[Hero — left column]
  Headline: "Knowing when to book is as important as knowing where."
  Subline: "We track Club Med availability and pricing daily — so you know 
            when conditions are in your favour."
  [No quote here — remove entirely from this page]

[Hero — right column]
  Search form (resort + month + party size → search)

[Resort signals grid]
  Season toggle (Ski / Summer)
  11 resort cards

[Signal guide]
  Favourable / Watch / Hold explanations (3 panels — keep, they're brief)

[Floating alert widget]
  [Persistent, bottom-right corner]

[Footer]
```

**About page — what to add there:**
- The £1,600 story (verbatim quote works well in long-form context)
- "How When To Book Works" (steps 01/02/03) in its current form
- Background on Drop Media Ltd, data methodology, frequency of checks

This structure reduces the clubmed page by roughly one full section (how-it-works) and trims the hero. On mobile, the user reaches the resort grid in ~2 scrolls rather than 4–5.

---

## 4. Touch Targets & Tap Interactions

### Issues found

**"Set Alert" button in header nav:**
```css
.header-nav .btn-alert {
  padding: 9px 20px;
  font-size: 12px;
}
```
Computed height ≈ 12px × 1.6 line-height + 18px padding = ~37px. **Below the 44px minimum.** This is the primary CTA on mobile (it's the only nav element that survives the `display:none` rule at 600px). It needs `min-height: 44px` and matching padding.

**Season toggle buttons:**
```css
.season-btn { padding: 8px 20px; }
```
No mobile min-height override (the `min-height: 44px` rule only applies to `.filter-btn` and `.btn`). At 8px top/bottom padding + 13px font = ~34px. **Below minimum.** The season toggle is a primary affordance above the resort grid. Add `min-height: 44px` to `.season-btn` inside the mobile breakpoint.

**Modal close button (×):**
```css
.modal-close { padding: 2px 4px; font-size: 24px; }
```
Computed touch area ≈ 28px × 28px. **Below minimum.** Should be `min-width: 44px; min-height: 44px` with `display: flex; align-items: center; justify-content: center`.

**Departure date mode tabs:**
```css
.date-mode-tab { padding: 8px 6px; }
```
~8px + ~11px line-height × 1.6 = ~26px. **Below minimum.** These are key navigation inside the search form — increase to `min-height: 44px`.

**Resort cards:**
Each card is a `div` with `cursor: pointer` and a JS click handler. The entire card surface is tappable — this is good. However there's no `:active` state defined for touch feedback. Mobile users tapping a card get no visual confirmation the tap registered before the modal opens. Add a brief `:active { transform: scale(0.98); }` or background shift.

**Form selects and inputs:**
Correctly given `min-height: 44px` in the mobile breakpoint ✓.

**"Book on Club Med" button (modal CTA):**
`btn-lg` has `padding: 14px 32px` — computed height ~42px. Borderline. Add `min-height: 44px` to `.btn-lg` for safety.

**dept-table in resort modal:**
The price history table (`dept-table`) has no mobile-specific layout. At 375px with 20px modal padding on each side, the content area is 335px. The table has columns: departure date, 7 nights, adults, 1C, 2C, trend, book link. That's 7 columns. On mobile this will overflow and require horizontal scroll — a poor experience. This table needs either a mobile-specific card layout or selective column hiding (hide adult/child variant columns, keep date + best price + signal + book link).

---

## 5. Performance Concerns on Mobile

**JavaScript weight:**
The page is a single-file HTML with all JS inline — the `<script>` block will be large once `RESORT_DATA` is fully populated (11 resorts × multiple departures × price history arrays). For now, with placeholder data, this is not a concern. As the dataset grows, the page weight will grow proportionally. Consider splitting `RESORT_DATA` into a separate `resort-data.js` fetched asynchronously so the HTML parses faster. Not urgent for MVP.

**Google Fonts:**
Two font families are loaded: Playfair Display (7 weights/variants) and Inter (4 weights). That's 11 font files. The `display=swap` parameter is correctly set ✓. The preconnect headers are present ✓. However, the Playfair Display weight list includes `wght@0,400;0,500;0,600;0,700;1,400;1,500;1,600` — 7 variants. On the tracker page, only weights 400, 500, 600, 700 are meaningfully used. Remove unused variants to reduce font payload. Estimated saving: 2–3 requests, ~30–40KB.

**Google Analytics:**
`<script async src="...gtag/js?id=...">` is present with `async` ✓. Not a blocking concern.

**Images:**
No `<img>` tags are present (card images are CSS gradients). No image optimisation work needed currently.

**Card image placeholders:**
`.card-image` uses `height: 160px` with a CSS gradient. Fine for now. When real photography is added, use `<img loading="lazy">` and `srcset` for responsive images.

**The inline `style="padding:80px 0;"` CSS bug:**
Mentioned in section 1 — this isn't a performance issue but it does cause unnecessary scroll on mobile, which degrades perceived performance.

**Sparkline SVGs:**
SVGs are generated inline by JS. Each resort card gets one. At 11 cards, that's 11 SVG elements in the DOM. Lightweight in practice, not a concern.

---

## 6. Overall Verdict

**Current mobile UX score: 5.5 / 10**

The fundamentals are in place — viewport meta tag, breakpoints exist, the resort grid stacks correctly, modals slide up from the bottom. But there are several real friction points that would measurably hurt conversion for a mobile user arriving from Google:

1. The inline style padding bug means far too much scroll between sections.
2. The primary CTA (the alert form) requires 4–5 scrolls to reach — the floating widget is the right fix.
3. Multiple touch targets are undersized, particularly the two most important ones: the "Set Alert" nav button and the season toggle.
4. The hero is too text-heavy on mobile — the £1,600 story and "How It Works" belong on About.
5. The modal's price history table will overflow on mobile once real data is injected.

---

## Prioritised Top 5 Improvements

**Priority 1 — Fix the inline style padding bug (30 minutes)**  
Remove `style="padding:80px 0;"` from the three sections (`#signals`, `#how-it-works`, `#alerts`) and let the CSS breakpoint `padding: 48px 0` apply correctly on mobile. This is a single-line fix per section that reduces unnecessary scroll immediately.

**Priority 2 — Fix undersized touch targets (1 hour)**  
Add `min-height: 44px` to `.header-nav .btn-alert`, `.season-btn`, `.modal-close`, and `.date-mode-tab` inside the `@media (max-width: 600px)` block. These are the controls users will reach for most — they must be reliably tappable.

**Priority 3 — Implement the floating alert widget (2–3 hours)**  
Replace the full-width alert section with the floating pill widget per the spec in section 2. This is the highest-impact conversion change: the current form is practically invisible on mobile. The `#alerts` section can be removed from the page or repurposed as a minimal "Want alerts?" text link that triggers the widget.

**Priority 4 — Trim the hero and move How It Works to About (1 hour)**  
Remove the £1,600 blockquote from the hero. Remove the `#how-it-works` section from clubmed/index.html. Add both to the About page. The homepage becomes: hero → search → resort grid → signal guide. Tighter, faster, more immediate.

**Priority 5 — Make dept-table mobile-safe (2 hours)**  
Add a mobile CSS rule inside `@media (max-width: 600px)` that hides the per-party-size variant columns from the departure table inside the resort modal, and shows only: departure date, lowest price, price signal, book link. This prevents horizontal overflow once real data populates the table. Can also add `-webkit-overflow-scrolling: touch; overflow-x: auto;` as a quick containment fallback.

---

*Audit by Claude / Cowork — 2026-05-19*
