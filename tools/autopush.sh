#!/bin/bash
# Pushes local commits on main and rebuild to GitHub every few minutes (run by launchd, see
# tools/install_autopush.sh). Lets Cowork sessions commit locally and have the work land on GitHub.
# Safe by design: never force-pushes, never rebases; stops and logs if a merge would conflict.
set -u
REPO="$HOME/booking-window"
LOG="$HOME/Library/Logs/whentobook-autopush.log"
export GIT_SSH_COMMAND="ssh -i $HOME/.ssh/booking_window_deploy -o BatchMode=yes -o ConnectTimeout=15"
log() { echo "$(date '+%Y-%m-%d %H:%M:%S') $*" | tee -a "$REPO/.autopush.log" >> "$LOG"; }
log "run start"
cd "$REPO" || exit 1
[ -e .git/MERGE_HEAD ] || [ -d .git/rebase-merge ] || [ -d .git/rebase-apply ] && { log "skip: merge/rebase in progress"; exit 0; }
git fetch -q origin main rebuild 2>>"$REPO/.autopush.log" || { log "fetch failed (offline?)"; exit 0; }
current=$(git symbolic-ref --short -q HEAD || echo "")
for b in main rebuild; do
  git rev-parse -q --verify "refs/heads/$b" >/dev/null || continue
  ahead=$(git rev-list --count "origin/$b..$b")
  [ "$ahead" -gt 0 ] || continue
  behind=$(git rev-list --count "$b..origin/$b")
  if [ "$behind" -gt 0 ]; then
    if [ "$b" = "$current" ]; then
      git merge -q --no-edit "origin/$b" >>"$LOG" 2>&1 || { git merge --abort 2>/dev/null; log "$b: merge with origin conflicts - left for a human"; continue; }
    else
      # Branch not checked out: merge in a temporary worktree so the user's working copy is untouched.
      tmp=$(mktemp -d)
      if git worktree add -q "$tmp" "$b" 2>>"$LOG" && git -C "$tmp" merge -q --no-edit "origin/$b" >>"$LOG" 2>&1; then :; else
        git -C "$tmp" merge --abort 2>/dev/null; log "$b: merge with origin conflicts - left for a human"
        git worktree remove --force "$tmp"; continue
      fi
      git worktree remove --force "$tmp"
    fi
  fi
  if git push -q origin "$b" 2>>"$REPO/.autopush.log"; then log "$b: pushed $ahead commit(s)"; else log "$b: push failed"; fi
done
