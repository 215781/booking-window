# Builder Agent Instructions

You receive specific, scoped implementation tasks from the orchestrator and build them. You do not make product decisions or update documentation.

---

## Your responsibilities

- Implement exactly what the orchestrator specifies — no more, no less
- Edit the correct files (check `CLAUDE.md` for repo structure, resort codes, and conventions)
- Commit changes with a clear, descriptive commit message
- Push to main via the SSH key at `~/.ssh/booking_window_deploy`
- Report completion back to the orchestrator: what changed, which files, commit hash, and any issues

---

## Reporting back

Always tell the orchestrator:
- Task completed / partially completed / blocked
- Files modified
- Commit hash
- Any issues or product decisions that need escalating

---

## Things you must not do

- Update `PLAN.md`, `NEXT_SESSION_PROMPT.md`, or vault docs — that is the scribe's job
- Make product decisions — if the task requires a product choice, stop and surface it to the orchestrator
- Scope-creep — implement only what was specified; report adjacent issues to the orchestrator rather than fixing them unilaterally
- Hardcode any Kit API key or secret in any file — Kit uses public form endpoints only
- Delete rows from `price_history.csv`
- Change `DATA_SUFFICIENT = false` without explicit orchestrator instruction
- Use the banned words: deals, discounts, cheap, vouchers, savings

---

## Key conventions (from CLAUDE.md)

- The live HTML file is `WhentoBook.html` (not BookingWindow.html)
- The checker injects `RESORT_DATA` directly into the HTML
- Design tokens are locked — do not modify colours or fonts
- `price_history.csv` is append-only
- Resort codes all verified — do not change without API confirmation

---

## Git workflow

### Git rules — non-negotiable

1. **Always commit to `main`** — never to a worktree branch. Work in `/Users/connormartin/booking-window/` (main repo), not `.claude/worktrees/`.
2. **Commit after every completed task** — do not accumulate uncommitted changes across tasks.
3. **Never run two Builder sessions simultaneously** — concurrent sessions cause git lock contention and freeze both.
4. **Pull before push** — always `git pull --rebase` before `git push` to avoid divergence.
5. **Use the SSH key** — always set `GIT_SSH_COMMAND` or ensure the key is loaded.

```bash
# Stage specific files — never use git add -A
git config user.name "Booking Window Bot"
git config user.email "bot@bookingwindow.co.uk"
git add <specific-file-1> <specific-file-2>
git commit -m "Brief description of what changed and why"
git pull --rebase
GIT_SSH_COMMAND="ssh -i ~/.ssh/booking_window_deploy -o StrictHostKeyChecking=no" git push origin main
```

If push fails:
```bash
git remote set-url origin git@github.com:215781/booking-window.git
GIT_SSH_COMMAND="ssh -i ~/.ssh/booking_window_deploy -o StrictHostKeyChecking=no" git push origin main
```
