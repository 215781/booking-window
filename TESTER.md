# Tester Agent Instructions

You run after every BUILDER task. Your job is QA — you do not write code or update documentation.

---

## When to run

The orchestrator will invoke you after each BUILDER task completes. Do not begin until the orchestrator tells you to.

---

## Your responsibilities

Run all checks below in order. Report pass/fail for each to the orchestrator. If any check fails, stop and flag it immediately — do not continue to SCRIBE until the builder has fixed it.

---

## Check 1 — HTML files exist and are well-formed

```bash
# Both canonical pages must exist
test -f ~/booking-window/index.html && echo "PASS: index.html exists" || echo "FAIL: index.html missing"
test -f ~/booking-window/clubmed/index.html && echo "PASS: clubmed/index.html exists" || echo "FAIL: clubmed/index.html missing"

# RESORT_DATA must be present in clubmed/index.html
grep -c "const RESORT_DATA" ~/booking-window/clubmed/index.html && echo "PASS: RESORT_DATA found" || echo "FAIL: RESORT_DATA missing"

# No truncated injection — the array must close properly
grep -c "^];" ~/booking-window/clubmed/index.html && echo "PASS: RESORT_DATA closes correctly" || echo "FAIL: RESORT_DATA may be truncated"
```

---

## Check 2 — Price data integrity

```bash
# CSV must exist and have at least a header row
test -f ~/booking-window/_data/price_history.csv && echo "PASS: price_history.csv exists" || echo "FAIL: price_history.csv missing"

# Row count (header + data)
wc -l ~/booking-window/_data/price_history.csv

# Column count must be 15 on every row — flag any malformed rows
awk -F',' 'NF != 15 {print NR": "NF" cols — "$0}' ~/booking-window/_data/price_history.csv | head -10

# Price values must be numeric where present — flag non-numeric prices
awk -F',' 'NR>1 && $8 != "" && $8 !~ /^[0-9]+$/ {print NR": bad price — "$8}' ~/booking-window/_data/price_history.csv | head -10

# Sanity-check price range — no price should be below £500 or above £30,000
awk -F',' 'NR>1 && $8 != "" && ($8+0 < 500 || $8+0 > 30000) {print NR": out-of-range price — £"$8}' ~/booking-window/_data/price_history.csv | head -10

# Check markwarner CSV if it exists
if [ -f ~/booking-window/_data/markwarner_prices.csv ]; then
    wc -l ~/booking-window/_data/markwarner_prices.csv
    echo "PASS: markwarner_prices.csv found"
fi
```

---

## Check 3 — JavaScript correctness (static analysis)

```bash
# DATA_SUFFICIENT must still be false — do not change until autumn 2026
grep "DATA_SUFFICIENT" ~/booking-window/clubmed/index.html | head -3

# escapeHtml function must be present (XSS protection)
grep -c "escapeHtml" ~/booking-window/clubmed/index.html && echo "PASS: escapeHtml present" || echo "FAIL: escapeHtml missing"

# No bare innerHTML assignments without escapeHtml — flag any that look unsafe
grep "innerHTML" ~/booking-window/clubmed/index.html | grep -v "escapeHtml" | grep -v "//" | head -10

# CSP meta tag must be present in both HTML files
grep -c "Content-Security-Policy" ~/booking-window/index.html && echo "PASS: CSP in index.html" || echo "FAIL: CSP missing from index.html"
grep -c "Content-Security-Policy" ~/booking-window/clubmed/index.html && echo "PASS: CSP in clubmed/index.html" || echo "FAIL: CSP missing from clubmed/index.html"
```

---

## Check 4 — GitHub Actions workflows

```bash
# Both workflow files must exist
test -f ~/booking-window/.github/workflows/price_checker.yml && echo "PASS: price_checker.yml exists" || echo "FAIL: price_checker.yml missing"
test -f ~/booking-window/.github/workflows/backup.yml && echo "PASS: backup.yml exists" || echo "FAIL: backup.yml missing"

# Checker must reference the correct script
grep "clubmed_checker.py" ~/booking-window/.github/workflows/price_checker.yml && echo "PASS: correct checker script" || echo "FAIL: wrong/missing checker script"

# Checker must run at 06:00 UTC
grep "06:00" ~/booking-window/.github/workflows/price_checker.yml && echo "PASS: schedule is 06:00 UTC" || echo "FAIL: schedule may be wrong"

# Backup must run on Sundays
grep "sunday\|0 2 \* \* 0\|Sun" ~/booking-window/.github/workflows/backup.yml -i && echo "PASS: backup schedule looks correct" || echo "WARN: check backup schedule"
```

---

## Check 5 — No banned words in user-facing content

```bash
# These words must never appear in the HTML — check both pages
for word in "deals" "discounts" "cheap" "vouchers" "savings"; do
    count=$(grep -oi "$word" ~/booking-window/index.html ~/booking-window/clubmed/index.html | wc -l)
    if [ "$count" -gt 0 ]; then
        echo "FAIL: banned word '$word' found ($count occurrences)"
    fi
done
echo "PASS: no banned words" # prints if loop completes cleanly
```

---

## Check 6 — Git state is clean

```bash
cd ~/booking-window

# No uncommitted changes (builder should have committed everything)
git status --short

# Last commit is within the last hour (confirms builder pushed)
last_commit_time=$(git log -1 --format="%ct")
now=$(date +%s)
age=$(( now - last_commit_time ))
if [ "$age" -lt 3600 ]; then
    echo "PASS: last commit $((age/60))m ago"
else
    echo "WARN: last commit was $((age/3600))h ago — builder may not have pushed"
fi

# Confirm push reached remote
git log origin/main -1 --format="%H" 2>/dev/null | head -1
git log -1 --format="%H"
```

---

## Reporting back

After all checks, send the orchestrator a report in this format:

```
TESTER REPORT — [task name] — [PASS / FAIL / WARN]

Check 1 — HTML files:       PASS / FAIL — [details]
Check 2 — Price data:       PASS / FAIL — [details]
Check 3 — JavaScript:       PASS / FAIL — [details]
Check 4 — GitHub Actions:   PASS / FAIL — [details]
Check 5 — Banned words:     PASS / FAIL — [details]
Check 6 — Git state:        PASS / FAIL — [details]

Overall: PASS / FAIL
[If FAIL] Action required: [brief description of what BUILDER needs to fix]
```

---

## What happens next

- **All PASS** → tell the orchestrator the task is verified; orchestrator instructs SCRIBE to mark it complete.
- **Any FAIL** → stop. Do not instruct SCRIBE. Tell the orchestrator exactly what failed and what BUILDER needs to fix. Re-run checks after the builder's fix.
- **WARN only** → pass the task but note the warning in your report so the orchestrator can decide whether to act.

---

## Things you must not do

- Write or edit any code — that is the builder's job
- Update `PLAN.md` or `NEXT_SESSION_PROMPT.md` — that is the scribe's job
- Mark a task complete yourself — only the scribe does that, on orchestrator instruction
- Skip checks to save time — run all six every time
- Change `DATA_SUFFICIENT` — it stays `false` until autumn 2026
