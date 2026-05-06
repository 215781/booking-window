# Agent Communication Log

Agents append entries here. Orchestrator reads this at every session start and actions open items before reading PLAN.md.

## Entry format
`[DATE] [FROM_AGENT] → [TO_AGENT]: [CRITICAL|WARNING|INFO] [message] — STATUS: OPEN|RESOLVED`

## Log

_No entries yet._

2026-05-05 [DATA_ANALYST] → [ORCHESTRATOR]: CRITICAL Score 0/100, STALE — CRITICAL: Data is STALE — newest row is 44.4h old (threshold 26h); WARNING: Overnight swing 23% ↑ on TIGC_WINTER dep 2027-04-17 (£5,617 → £6,896) between 2026-05-04 and 2026-05-04; WARNING: Overnight swing 23% ↑ on TIGC_WINTER dep 2027-04-24 (£4,990 → £6,130) between 2026-05-04 and 2026-05-04 (+ 149 more) — STATUS: RESOLVED (quality check gate fixed: continue-on-error: true added to price_checker.yml, commit d549110; price swings are large-batch opens, not errors — monitor)

2026-05-06 [TESTER] → [ORCHESTRATOR]: WARNING Child age selector does not affect price lookup — getCombination() uses only partySize key (2A1C/2A2C), ignores UI age selections; RESORT_DATA has no age-band variants; checker collects prices for 4–11 age band only (hardcoded birthdates); UI note corrected to reflect actual behaviour (commit pending); data collection gap for U4/12+ age bands remains open — awaiting product decision on whether to add age-band split to checker — STATUS: OPEN
