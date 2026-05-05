#!/usr/bin/env python3
"""
Data quality check — runs after price_checker.yml collects prices.
Reads _data/price_history.csv and appends a summary to AGENT_LOG.md.
Exits with code 1 if CRITICAL issues found (marks GitHub Actions run as failed).
"""

import csv
import sys
from collections import defaultdict
from datetime import datetime, timezone, timedelta
from pathlib import Path

CSV_PATH = Path("_data/price_history.csv")
AGENT_LOG_PATH = Path("AGENT_LOG.md")

PLACEHOLDER_CRITICAL = 20   # consecutive identical prices → CRITICAL
PLACEHOLDER_WARNING = 10    # consecutive identical prices → WARNING
ANOMALY_THRESHOLD = 0.20    # >20% overnight price change → WARNING
FRESHNESS_CRITICAL_H = 26   # hours since latest row → CRITICAL
FRESHNESS_WARNING_H = 20    # hours since latest row → WARNING
MIN_DAYS_COVERAGE = 5       # fewer than this in last 7 days → WARNING (active resort)
MIN_DAYS_COVERAGE_CRITICAL = 2  # fewer than this → CRITICAL


def parse_csv():
    if not CSV_PATH.exists():
        return []
    rows = []
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


def check_freshness(rows):
    """Return (severity, latest_dt, age_hours)."""
    if not rows:
        return "CRITICAL", None, None

    # Try common timestamp column names
    ts_col = None
    for col in ("timestamp", "date", "run_date", "checked_at", "datetime"):
        if col in (rows[-1] or {}):
            ts_col = col
            break
    if ts_col is None and rows:
        ts_col = list(rows[-1].keys())[0]

    try:
        raw = rows[-1][ts_col]
        # Handle various formats
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
            try:
                latest_dt = datetime.strptime(raw, fmt).replace(tzinfo=timezone.utc)
                break
            except ValueError:
                continue
        else:
            return "WARNING", None, None
    except (KeyError, TypeError):
        return "WARNING", None, None

    now = datetime.now(timezone.utc)
    age_hours = (now - latest_dt).total_seconds() / 3600

    if age_hours > FRESHNESS_CRITICAL_H:
        return "CRITICAL", latest_dt, age_hours
    elif age_hours > FRESHNESS_WARNING_H:
        return "WARNING", latest_dt, age_hours
    return "OK", latest_dt, age_hours


def check_placeholder_prices(rows):
    """
    Detect same price repeated >10 times consecutively for one resort.
    Returns list of (resort, price, count, severity).
    """
    issues = []
    resort_col = _detect_col(rows, ("resort", "resort_code", "resort_id"))
    price_col = _detect_col(rows, ("price", "best_price", "bestprice", "bestpricevalue", "price_gbp"))
    if not resort_col or not price_col:
        return issues

    by_resort = defaultdict(list)
    for row in rows:
        r = row.get(resort_col, "")
        p = row.get(price_col, "")
        if r and p:
            by_resort[r].append(p)

    for resort, prices in by_resort.items():
        max_run = _max_consecutive_run(prices)
        if max_run >= PLACEHOLDER_CRITICAL:
            issues.append((resort, None, max_run, "CRITICAL"))
        elif max_run >= PLACEHOLDER_WARNING:
            issues.append((resort, None, max_run, "WARNING"))

    return issues


def check_anomalies(rows):
    """
    Flag resort/date combos with >20% overnight price change.
    Returns list of (resort, departure_date, old_price, new_price, pct_change).
    """
    issues = []
    resort_col = _detect_col(rows, ("resort", "resort_code", "resort_id"))
    price_col = _detect_col(rows, ("price", "best_price", "bestprice", "bestpricevalue", "price_gbp"))
    date_col = _detect_col(rows, ("departure_date", "departure", "date_departure"))
    ts_col = _detect_col(rows, ("timestamp", "date", "run_date", "checked_at", "datetime"))

    if not all([resort_col, price_col, ts_col]):
        return issues

    # Build dict: (resort, departure_date) → list of (timestamp, price)
    history = defaultdict(list)
    for row in rows:
        resort = row.get(resort_col, "")
        raw_price = row.get(price_col, "")
        ts = row.get(ts_col, "")
        dep = row.get(date_col, "") if date_col else ""
        try:
            price = float(raw_price)
        except (ValueError, TypeError):
            continue
        if price > 0 and resort:
            history[(resort, dep)].append((ts, price))

    for (resort, dep), entries in history.items():
        entries.sort(key=lambda x: x[0])
        for i in range(1, len(entries)):
            old_p = entries[i - 1][1]
            new_p = entries[i][1]
            if old_p > 0:
                pct = abs(new_p - old_p) / old_p
                if pct > ANOMALY_THRESHOLD:
                    issues.append((resort, dep, old_p, new_p, pct))

    return issues


def check_coverage(rows):
    """
    For each active resort, check how many distinct days exist in the last 7 days.
    Returns list of (resort, days_found, severity).
    """
    issues = []
    resort_col = _detect_col(rows, ("resort", "resort_code", "resort_id"))
    ts_col = _detect_col(rows, ("timestamp", "date", "run_date", "checked_at", "datetime"))

    if not resort_col or not ts_col:
        return issues

    now = datetime.now(timezone.utc)
    cutoff_7d = now - timedelta(days=7)
    cutoff_30d = now - timedelta(days=30)

    active_resorts = set()
    days_by_resort_7d = defaultdict(set)

    for row in rows:
        resort = row.get(resort_col, "")
        raw_ts = row.get(ts_col, "")
        if not resort or not raw_ts:
            continue
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
            try:
                dt = datetime.strptime(raw_ts[:len(fmt) + 2].rstrip(), fmt).replace(tzinfo=timezone.utc)
                break
            except ValueError:
                continue
        else:
            continue

        if dt >= cutoff_30d:
            active_resorts.add(resort)
        if dt >= cutoff_7d:
            days_by_resort_7d[resort].add(dt.date())

    for resort in active_resorts:
        days = len(days_by_resort_7d.get(resort, set()))
        if days < MIN_DAYS_COVERAGE_CRITICAL:
            issues.append((resort, days, "CRITICAL"))
        elif days < MIN_DAYS_COVERAGE:
            issues.append((resort, days, "WARNING"))

    return issues


def _detect_col(rows, candidates):
    if not rows:
        return None
    cols = list(rows[0].keys())
    cols_lower = [c.lower() for c in cols]
    for c in candidates:
        if c in cols_lower:
            return cols[cols_lower.index(c)]
    return None


def _max_consecutive_run(values):
    if not values:
        return 0
    max_run = 1
    current_run = 1
    for i in range(1, len(values)):
        if values[i] == values[i - 1] and values[i] not in ("", "0", None):
            current_run += 1
            max_run = max(max_run, current_run)
        else:
            current_run = 1
    return max_run


def compute_score(freshness_sev, placeholder_issues, anomaly_issues, coverage_issues):
    score = 100
    for sev in [freshness_sev]:
        if sev == "CRITICAL":
            score -= 20
    for _, _, _, sev in placeholder_issues:
        score -= (20 if sev == "CRITICAL" else 5)
    for _ in anomaly_issues:
        score -= 5
    for _, _, sev in coverage_issues:
        score -= (20 if sev == "CRITICAL" else 5)
    return max(0, score)


def main():
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    rows = parse_csv()

    if not rows:
        log_line = (
            f"[{now_str}] [DATA_ANALYST] → [ORCHESTRATOR]: CRITICAL "
            f"DATA_QUALITY_SCORE=0 — price_history.csv missing or empty"
        )
        append_log(log_line)
        print(log_line)
        sys.exit(1)

    freshness_sev, latest_dt, age_hours = check_freshness(rows)
    placeholder_issues = check_placeholder_prices(rows)
    anomaly_issues = check_anomalies(rows)
    coverage_issues = check_coverage(rows)

    score = compute_score(freshness_sev, placeholder_issues, anomaly_issues, coverage_issues)

    # Determine overall severity
    all_sevs = [freshness_sev]
    all_sevs += [s for _, _, _, s in placeholder_issues]
    all_sevs += ["WARNING"] * len(anomaly_issues)
    all_sevs += [s for _, _, s in coverage_issues]

    if "CRITICAL" in all_sevs:
        overall = "CRITICAL"
    elif "WARNING" in all_sevs:
        overall = "WARNING"
    else:
        overall = "OK"

    # Build summary message
    parts = []
    if freshness_sev != "OK":
        age_str = f"{age_hours:.1f}h" if age_hours is not None else "unknown"
        parts.append(f"data age {age_str} [{freshness_sev}]")
    for resort, _, count, sev in placeholder_issues:
        parts.append(f"{resort}: {count} identical prices [{sev}]")
    for resort, dep, old_p, new_p, pct in anomaly_issues[:3]:  # cap at 3 in log
        parts.append(f"{resort}/{dep}: {old_p:.0f}→{new_p:.0f} ({pct*100:.0f}% change) [WARNING]")
    for resort, days, sev in coverage_issues:
        parts.append(f"{resort}: {days}/7 days coverage [{sev}]")

    summary = "; ".join(parts) if parts else "All checks passed"

    log_line = (
        f"[{now_str}] [DATA_ANALYST] → [ORCHESTRATOR]: {overall} "
        f"DATA_QUALITY_SCORE={score} — {summary}"
    )
    append_log(log_line)

    print(f"\nDATA_QUALITY_REPORT")
    print(f"===================")
    print(f"Generated: {now_str}")
    print(f"DATA_QUALITY_SCORE: {score}")
    print(f"FRESHNESS_STATUS: {freshness_sev}")
    if latest_dt:
        print(f"  Latest row: {latest_dt.strftime('%Y-%m-%d %H:%M UTC')}")
        print(f"  Age: {age_hours:.1f}h")
    print(f"\nISSUES_FOUND:")
    if not placeholder_issues and not anomaly_issues and not coverage_issues and freshness_sev == "OK":
        print("  (none)")
    else:
        for resort, _, count, sev in placeholder_issues:
            print(f"  [{sev}] {resort}: {count} consecutive identical prices (placeholder/stale API response)")
        for resort, dep, old_p, new_p, pct in anomaly_issues:
            print(f"  [WARNING] {resort} {dep}: price changed {old_p:.0f}→{new_p:.0f} ({pct*100:.1f}% overnight)")
        for resort, days, sev in coverage_issues:
            print(f"  [{sev}] {resort}: only {days}/7 days coverage in last week")
        if freshness_sev != "OK":
            print(f"  [{freshness_sev}] Data freshness: latest row is {age_hours:.1f}h old")

    print(f"\nLog entry appended to {AGENT_LOG_PATH}")

    if overall == "CRITICAL":
        sys.exit(1)


def append_log(line):
    if not AGENT_LOG_PATH.exists():
        return
    with open(AGENT_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(line + "\n")


if __name__ == "__main__":
    main()
