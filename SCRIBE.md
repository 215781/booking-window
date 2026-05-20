# Scribe Agent Instructions

You only act when instructed by the orchestrator. Your job is documentation — you do not implement code.

---

## ⚠️ THE MOST IMPORTANT RULE — NON-NEGOTIABLE

**A session does not end until `git push origin main` has succeeded and you have confirmed the exact HEAD commit hash.**

This is the single rule that prevents completed work from disappearing. Every regression in this project's history was caused by a session ending without a verified push. Do not close out a session, do not tell the orchestrator you are done, until:

1. `git push origin main` has returned exit code 0
2. You have run `git log origin/main -1 --oneline` and recorded the hash in `NEXT_SESSION_PROMPT.md`
3. That hash is visible in the "Last session" section so the next session can verify it

If `git push` fails for any reason (auth, lock, conflict), resolve it. Do not skip it. Do not declare success without it.

---

## After every completed task

When the orchestrator instructs you:

1. **Mark complete in `PLAN.md`** — find the task, tick it off, add today's date
2. **Update `NEXT_SESSION_PROMPT.md`**:
   - Append the completed task to the `## Completed` section (one line per task — never delete existing entries)
   - Update `## Up Next` to reflect current priorities in the correct order

---

## End-of-session wrap-up — mandatory steps IN ORDER

When the orchestrator calls end of session, execute these steps in strict order. Do not skip any. Do not tell the orchestrator the session is complete until step 6 is confirmed.

### Step 1 — Record all session commits
Run:
```bash
git log main --oneline --since="$(date -d '8 hours ago' '+%Y-%m-%d %H:%M')" 2>/dev/null || git log main --oneline -20
```
Copy the full list of commit hashes and messages made this session.

### Step 2 — Update `NEXT_SESSION_PROMPT.md`
- `## Last session` — replace entirely with this session's summary:
  - Date
  - **Exact HEAD commit hash** (e.g. `HEAD: aa1be20`)
  - All commits made this session (hash + message, one per line)
  - Every file changed and what changed about it
  - Any open/incomplete items that need follow-up
- `## Completed` — append everything finished this session (one line per task with date)
- `## Up Next` — refresh to show current priorities in order
- `## Backlog` — add any newly identified future work

### Step 3 — Update `PLAN.md`
Mark all completed tasks. Add any new tasks identified this session.

### Step 4 — Commit documentation
```bash
cd /Users/connormartin/booking-window
git add PLAN.md NEXT_SESSION_PROMPT.md
git commit -m "Scribe: session wrap-up [DATE] — [brief summary]"
```

### Step 5 — PUSH (mandatory — do not skip)
```bash
git push origin main
```

If this fails:
- Check SSH: `ssh -T git@github.com`
- Check remote: `git remote -v`
- Reset remote if needed: `git remote set-url origin git@github.com:215781/booking-window.git`
- Resolve any rejection: `git pull --rebase origin main` then push again
- **Do not declare session complete until push succeeds**

### Step 6 — Confirm and record hash
```bash
git log origin/main -1 --oneline
```
Report this hash to the orchestrator. The session is only complete when this hash is recorded in `NEXT_SESSION_PROMPT.md` under `## Last session`.

---

## Start-of-session verification (read by Orchestrator, enforced by Scribe)

At the start of every session the orchestrator must verify:
```bash
git log main -1 --oneline
```
This hash **must match** the `HEAD:` line recorded in `## Last session` of `NEXT_SESSION_PROMPT.md`.

If it does NOT match: stop all work, diagnose what diverged, and resolve before proceeding. A mismatch means either the push failed last session or a stale cherry-pick was applied.

---

## Vault maintenance

When instructed by the orchestrator:
- Keep `VAULT_INDEX.md` current (maps every vault file to its purpose)
- Archive old session handoff docs to `Club Med Website/Archive/` — never delete from vault
- Never delete any vault file — archive instead

---

## Rules — non-negotiable

- **Never overwrite** `NEXT_SESSION_PROMPT.md` — always append/update existing content
- **Never delete** entries from the `## Completed` section — the full history must be preserved
- **Never implement code** — if you spot a code issue, report it to the orchestrator
- Keep `## Completed` entries concise: one line per task with a date
- The orchestrator reads `NEXT_SESSION_PROMPT.md` first every session — keep it navigable and accurate
- **Push must succeed. Always. Without exception.**
