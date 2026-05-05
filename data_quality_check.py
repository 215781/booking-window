#!/usr/bin/env python3
"""
Data quality check for price_history.csv.
Appends a summary line to AGENT_LOG.md.
Exits with code 1 if any CRITICAL issue is found.
"""

import csv
import sys
from collections import defaultdict
from datetime import datetime, timezone, timedelta
from pathlib import Path

CSV_PATH = Path("_data/price_history.csv")
LOG_PATH = Path("AGENT_LOG.md")

PLACEHOLDER_THRESHOLD = 10   # same price >N times in one resort+run = placeholder signal
SWING_THRESHOLD = 0.20       # >20% overnight change = suspicious
MIN_HISTORY_DAYS = 7         # fewer than this = thin history
STALE_HOURS = 26             # newest row older than this = stale


def fmt_price(v):
    return f"£{v:,}"


def run_checks():
    if not CSV_PATH.exists():
        print(f"ERROR: {CSV_PATH} not found")
        sys.exit(1)

    rows = []
    with open(CSV_PATH, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    if not rows:
        print("ERROR: CSV is empty")
        sys.exit(1)

    issues = []   # list of (severity, message)
    score = 100

    # ── 1. Data freshness ──────────────────────────────────────────────────
    timestamps = [r["timestamp"] for r in rows if r["timestamp"]]
    max_ts_str = max(timestamps)
    max_ts = datetime.fromisoformat(max_ts_str.replace("Z", "+00:00"))
    now_utc = datetime.now(timezone.utc)
    age_hours = (now_utc - max_ts).total_seconds() / 3600

    if age_hours > STALE_HOURS:
        issues.append(("CRITICAL", f"Data is STALE — newest row is {age_hours:.1f}h old (threshold {STALE_HOURS}h)"))
        score -= 25
    freshness = "STALE" if age_hours > STALE_HOURS else "FRESH"

    # Group rows by (run_date, resort_code) and (resort_code, start_date)
    by_run_resort = defaultdict(list)      # (run_date, resort_code) → [price, ...]
    by_resort_dep = defaultdict(list)      # (resort_code, start_date) → [(run_date, price), ...]
    run_dates_by_resort = defaultdict(set) # resort_code → {run_date, ...}

    for r in rows:
        ts = r["timestamp"]
        if not ts:
            continue
        run_date = ts[:10]  # YYYY-MM-DD
        resort = r["resort_code"]
        start = r["start_date"]
        price_raw = r["price"].strip()
        price = int(price_raw) if price_raw else 0

        if price > 0:  # ignore empty/zero prices — pre-booking-window expected
            by_run_resort[(run_date, resort)].append(price)
            by_resort_dep[(resort, start)].append((run_date, price))
        run_dates_by_resort[resort].add(run_date)

    # ── 2. Placeholder price detection ────────────────────────────────────
    latest_run_date = max(ts[:10] for ts in timestamps if ts)
    for resort in set(r["resort_code"] for r in rows):
        prices = by_run_resort.get((latest_run_date, resort), [])
        if not prices:
            continue
        counts = defaultdict(int)
        for p in prices:
            counts[p] += 1
        for price_val, count in counts.items():
            if count > PLACEHOLDER_THRESHOLD:
                issues.append((
                    "CRITICAL",
                    f"Placeholder signal: {resort} — price {fmt_price(price_val)} "
                    f"repeated {count}x in run {latest_run_date}"
                ))
                score -= 30

    # ── 3. Overnight price swing ──────────────────────────────────────────
    for (resort, start), entries in by_resort_dep.items():
        if len(entries) < 2:
            continue
        entries_sorted = sorted(entries, key=lambda x: x[0])
        prev_date, prev_price = entries_sorted[-2]
        curr_date, curr_price = entries_sorted[-1]
        if prev_price == 0 or curr_price == 0:
            continue
        swing = abs(curr_price - prev_price) / prev_price
        if swing > SWING_THRESHOLD:
            direction = "↑" if curr_price > prev_price else "↓"
            issues.append((
                "WARNING",
                f"Overnight swing {swing:.0%} {direction} on {resort} dep {start} "
                f"({fmt_price(prev_price)} → {fmt_price(curr_price)}) "
                f"between {prev_date} and {curr_date}"
            ))
            score -= 10

    # ── 4. Thin history ──────────────────────────────────────────────────
    for resort, dates in run_dates_by_resort.items():
        if len(dates) < MIN_HISTORY_DAYS:
            issues.append((
                "INFO",
                f"Thin history: {resort} has only {len(dates)} day(s) of data "
                f"(min {MIN_HISTORY_DAYS})"
            ))
            score -= 3

    score = max(0, score)

    # ── Print report ──────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print(f"  WhenToBook — Data Quality Report")
    print(f"  Run: {now_utc.strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"{'='*60}")
    print(f"  DATA_QUALITY_SCORE: {score}/100")
    print(f"  FRESHNESS_STATUS:   {freshness} (newest row: {max_ts_str}, {age_hours:.1f}h ago)")
    print()

    if issues:
        print("  ISSUES_FOUND:")
        for sev, msg in issues:
            print(f"    [{sev}] {msg}")
    else:
        print("  ISSUES_FOUND: none")

    print()
    if issues:
        criticals = [m for s, m in issues if s == "CRITICAL"]
        warnings  = [m for s, m in issues if s == "WARNING"]
        infos     = [m for s, m in issues if s == "INFO"]
        parts = []
        if criticals: parts.append(f"{len(criticals)} CRITICAL")
        if warnings:  parts.append(f"{len(warnings)} WARNING")
        if infos:     parts.append(f"{len(infos)} INFO")
        print(f"  RECOMMENDED_ACTIONS:")
        if criticals:
            print("    - Investigate CRITICAL issues → route to Builder via Orchestrator")
        if warnings:
            print("    - Review WARNING swings — may be API noise; monitor next run")
        if infos:
            print("    - INFO items are advisory; no immediate action required")
    else:
        print("  RECOMMENDED_ACTIONS: none — data looks healthy")

    print(f"{'='*60}\n")

    # ── Append to AGENT_LOG.md ────────────────────────────────────────────
    today = now_utc.strftime("%Y-%m-%d")
    if not issues:
        severity = "INFO"
        summary = f"Clean run — score {score}/100, freshness {freshness}, no issues detected"
    else:
        highest = "INFO"
        for s, _ in issues:
            if s == "CRITICAL":
                highest = "CRITICAL"
                break
            if s == "WARNING":
                highest = "WARNING"
        severity = highest
        issue_summary = "; ".join(f"{s}: {m}" for s, m in issues[:3])
        if len(issues) > 3:
            issue_summary += f" (+ {len(issues)-3} more)"
        summary = f"Score {score}/100, {freshness} — {issue_summary}"

    log_entry = (
        f"\n{today} [DATA_ANALYST] → [ORCHESTRATOR]: {severity} {summary} "
        f"— STATUS: {'OPEN' if severity in ('CRITICAL','WARNING') else 'RESOLVED'}"
    )

    with open(LOG_PATH, "a") as f:
        f.write(log_entry + "\n")

    print(f"Appended to {LOG_PATH}")

    # ── Exit code ─────────────────────────────────────────────────────────
    has_critical = any(s == "CRITICAL" for s, _ in issues)
    if has_critical:
        sys.exit(1)


if __name__ == "__main__":
    run_checks()
