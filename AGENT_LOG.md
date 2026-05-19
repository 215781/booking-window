# Agent Communication Log

Agents append entries here. Orchestrator reads this at every session start and actions open items before reading PLAN.md.

## Entry format
`[DATE] [FROM_AGENT] → [TO_AGENT]: [CRITICAL|WARNING|INFO] [message] — STATUS: OPEN|RESOLVED`

## Log

_No entries yet._

2026-05-05 [DATA_ANALYST] → [ORCHESTRATOR]: CRITICAL Score 0/100, STALE — CRITICAL: Data is STALE — newest row is 44.4h old (threshold 26h); WARNING: Overnight swing 23% ↑ on TIGC_WINTER dep 2027-04-17 (£5,617 → £6,896) between 2026-05-04 and 2026-05-04; WARNING: Overnight swing 23% ↑ on TIGC_WINTER dep 2027-04-24 (£4,990 → £6,130) between 2026-05-04 and 2026-05-04 (+ 149 more) — STATUS: RESOLVED (quality check gate fixed: continue-on-error: true added to price_checker.yml, commit d549110; price swings are large-batch opens, not errors — monitor)

2026-05-06 [TESTER] → [ORCHESTRATOR]: WARNING Child age selector does not affect price lookup — getCombination() uses only partySize key (2A1C/2A2C), ignores UI age selections; RESORT_DATA has no age-band variants; checker collects prices for 4–11 age band only (hardcoded birthdates); UI note corrected to reflect actual behaviour (commit pending); data collection gap for U4/12+ age bands remains open — awaiting product decision on whether to add age-band split to checker — STATUS: RESOLVED (hero form removed entirely in commit 5d7d42f — age selectors no longer exist in the UI)

[2026-05-19] [TESTER] → [ORCHESTRATOR]: INFO bookingUrl audit — all 11 ski resorts have resort-specific bookingUrl slugs in clubmed_checker.py (line 92–172), emitted by build_resort_data_js() (line 459), and wired into clickable CTAs in clubmed/index.html: modal "Book on Club Med" button href set dynamically via JS (line 13241: `document.getElementById('modal-book-btn').href = resort.bookingUrl || 'https://www.clubmed.co.uk'`), departure table rows each contain a per-departure "Book on Club Med ↗" anchor using `resort.bookingUrl` (line 13175/13191), and search results also use bookingUrl (line 13500) — PLAN.md claim is correct; product owner dispute is unfounded — STATUS: RESOLVED
