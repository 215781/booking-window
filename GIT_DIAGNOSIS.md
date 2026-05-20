# Git Regression Forensics — When To Book

**Date of analysis:** 2026-05-20  
**Analyst:** Claude Sonnet 4.6 (forensic mode)

---

## TL;DR

The root cause is **stale worktree commits being cherry-picked onto an advanced codebase**. A commit authored **May 4** was cherry-picked onto `main` on **May 19**, 15 days later. In those 15 days, `main` had gained resort photos, the hero best-card, and signal-first CSS. The cherry-pick applied a diff computed against the May 4 codebase, and the conflict resolution replaced the entire `clubmed/index.html` with the old version, wiping out all 15 days of UI work. Two "restore" commits fixed the damage the following morning.

This has happened multiple times. The pattern is structural, not a one-off mistake.

---

## Step 1: Reflog Analysis

```
f0bbeb3  commit (cherry-pick): Fix 5 items [main, 2026-05-19 20:17:40]
6c22850  pull --rebase (finish): returned to main [2026-05-19 20:05:46]
```

- No force-push entries in the reflog.
- No `reset --hard` moving HEAD backwards.
- The regression was introduced by **cherry-pick**, not a force-push or reset.
- The cherry-pick applied a 15-day-old diff onto a much-newer codebase.

---

## Step 2: Commit History — Diverged Branches

```
* aa1be20  fix: restore hero best-card, signal-first CSS, card-price hierarchy
* 90ec002  fix: restore resort photo images on club med resort cards
* bedd2df  Log: BUILDER mobile FAB task complete
...
* f0bbeb3  Fix 5 items: CSV header, bookingUrl, cheapest copy, mobile touch, sort bar  ← THE CULPRIT
* 6384794  cherry-pick: Fix mobile touch
* c024eb4  cherry-pick: Purge LP2C placeholders
...
* 6c22850  Add auto-merge workflow
```

Branches with commits NOT on `main` (live orphans):

| Branch | Commit | Date | Status |
|--------|--------|------|--------|
| `claude/elated-benz-92eda0` | Orchestrator session wrap-up 2026-05-19 | May 19 20:39 | **Never merged** |
| `claude/naughty-noyce-f4276b` | copy: signal-first reframe — lead with £saved/% down | May 10 21:30 | **Never merged** |
| `claude/peaceful-lumiere-056f8d` | fix: replace remaining Saturday with Sunday | May 7 17:13 | Cherry-picked but original orphaned |
| `claude/quirky-edison-3384f6` | plan: add Known Issues section to PLAN_V2 | May 19 19:13 | **Never merged to main** |

---

## Step 3: The Specific Regression Event

### Offending commit: `f0bbeb3`

```
Author: Booking Window Bot <bot@whentobook.co.uk>
AuthorDate:    2026-05-04 20:14:30 +0100    ← AUTHORED 15 DAYS EARLIER
CommitterDate: 2026-05-19 20:17:40 +0100    ← cherry-picked to main May 19
Parent: 6c22850                              ← current main at time of cherry-pick

clubmed/index.html: 2,265 insertions / 10,359 deletions
```

The author/committer date split is the smoking gun. **`f0bbeb3` was created in a worktree on May 4 and sat there for 15 days before being cherry-picked to main.**

### What `6c22850` (main before cherry-pick) contained:
- ✅ Resort photo images (`RESORT_IMAGES` dict) — added May 19 at 17:41
- ✅ Serre-Chevalier photo — added May 19 at 17:45
- ✅ Signal-first CSS hierarchy — restored May 19 at 18:59
- ✅ Hero best-card (`renderHeroBestCard()`) — added earlier

### What `f0bbeb3` contained after cherry-pick:
- ❌ Resort photos deleted (RESORT_IMAGES wiped)
- ❌ Signal-first CSS reverted
- ❌ Hero best-card replaced with a search form

### How it happened:

1. On May 4, a worktree session was created from that day's `main` (which had none of those features).
2. The session made legitimate fixes: bookingUrl, CSV header, sort bar, etc.
3. It ran `clubmed_checker.py --inject-only`, which regenerated `clubmed/index.html` from the **May 4 template** (without resort images, without hero best-card).
4. This generated a 10k-line replacement of the file, committed as `f0bbeb3`.
5. On May 19 at 20:17, an Orchestrator session cherry-picked this commit onto `6c22850`.
6. The cherry-pick diff (+2,265 / -10,359) applied the May 4 state of `clubmed/index.html` onto the May 19 state — deleting everything added in those 15 days.
7. Because `clubmed/index.html` had changed so dramatically, the cherry-pick had massive conflicts. The conflict resolution accepted the **incoming (May 4) version**, discarding all May 19 improvements.

---

## Step 4: Worktree Analysis

```
$ git worktree list | wc -l
127
```

**127 active worktrees.** Claude Code creates one per session and never removes them. Each worktree branches from `main` at its creation moment and may accumulate commits that never make it to `main`. Over time, worktrees fork from increasingly old states.

The danger: a worktree created 2 weeks ago that runs `--inject-only` will generate an HTML template from a 2-week-old baseline, then if that commit is cherry-picked to current `main`, it overwrites 2 weeks of work.

Worktrees accumulate unboundedly. At 127 and growing, the probability of a stale one being mistakenly used for cherry-pick increases each session.

---

## Step 5: Push Pattern

Local `main` and `origin/main` are **in sync**: both at `aa1be20`. No divergence. The problem is not a missing push — it is content being overwritten by a stale cherry-pick before reaching origin.

---

## Step 6: Root Cause Report

### What specifically caused the revert?

A **cherry-pick of a 15-day-old commit** (`f0bbeb3`, authored May 4) onto current `main` (May 19). The commit had regenerated `clubmed/index.html` wholesale using an old template. When applied to a much-newer `main`, the conflict resolution replaced the current file with the old content, deleting resort images, hero best-card, and signal-first CSS.

This is **not** the first time. Earlier regressions:
- `012ca2f` "fix: restore signal-first visual hierarchy" (May 19 18:59)
- `6b5319c` "fix: restore native checkbox rendering" (May 19 19:13)
- `1bd606a` "Revert clubmed/index.html to working state" (May 5)

All of these are repair commits following the same pattern: stale cherry-pick deletes newer work.

### Is this a Scribe/Orchestrator problem, or a deeper git workflow problem?

**Both, but the git workflow problem is structural.** The Scribe/Orchestrator design assumes that worktree commits can be safely cherry-picked to `main` at any time. That assumption is wrong when:

1. The commit is more than minutes old (any new work on `main` in the interim is at risk).
2. The commit modifies a file that is also regenerated wholesale (`clubmed/index.html`).
3. Conflict resolution is automated or non-conservative.

The Scribe/Orchestrator layer makes it worse by providing a false sense that session wrap-ups and cherry-picks are handled correctly — but nothing is checking whether the cherry-picked content is actually safe to apply to the current state of `main`.

### What is the fix?

**Immediate (prevent the next regression):**

1. **Author-date check before cherry-pick**: If a commit's author date is more than 2 hours older than current `HEAD`, do not cherry-pick it. Instead, check out the worktree branch, rebase it onto current `main` (`git rebase main`), resolve conflicts explicitly, then apply.

2. **Sanity grep before any push touching `clubmed/index.html`**:
   ```bash
   grep -c "RESORT_IMAGES" clubmed/index.html   # must be > 0
   grep -c "renderHeroBestCard" clubmed/index.html  # must be > 0
   grep -c "price-movement" clubmed/index.html   # must be > 0
   ```
   If any are 0, abort and investigate.

3. **`--inject-only` must run against current main's `clubmed_checker.py`**, not a worktree's stale copy. The workflow should always `git pull` before running `--inject-only`.

**Structural (prevent accumulation):**

4. **Worktree prune**: Run `git worktree prune` to remove worktrees whose branches have been deleted or merged. This won't help the live ones, but stops the list growing further.

5. **Merge instead of cherry-pick for HTML work**: For any commit that modifies `clubmed/index.html` by more than 100 lines, use `git merge --no-ff <branch>` instead of cherry-pick. This forces explicit conflict resolution.

6. **One authoritative session at a time for HTML work**: Never run two sessions in parallel that both write `clubmed/index.html`. The Orchestrator/Builder pattern should treat `clubmed/index.html` as a mutex resource.

---

## Appendix: Historical Regression Timeline

| Date | Repair commit | What it fixed | Cause |
|------|--------------|---------------|-------|
| 2026-05-05 | `1bd606a` Revert to working state (d651c28) | Unknown breakage | Likely same pattern |
| 2026-05-19 18:59 | `012ca2f` Restore signal-first CSS | CSS hierarchy reverted | Stale overwrite |
| 2026-05-19 19:13 | `6b5319c` Restore native checkbox | Checkbox styling broken | Stale overwrite |
| 2026-05-20 08:02 | `90ec002` Restore resort photos | RESORT_IMAGES deleted | `f0bbeb3` cherry-pick |
| 2026-05-20 08:10 | `aa1be20` Restore hero best-card + CSS | Multiple regressions | `f0bbeb3` cherry-pick |

The two repair commits on May 19 (18:59, 19:13) were themselves overwritten by the `f0bbeb3` cherry-pick at 20:17, requiring two more repair commits on May 20.

---

*Analysis based on: `git reflog --all`, `git log --graph --all`, `git worktree list`, `git cat-file`, cherry-pick reflog entries.*
