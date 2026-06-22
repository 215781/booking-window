#!/usr/bin/env python3
"""
markwarner_summer_checker.py — When To Book: Mark Warner summer beach price checker (async)
Uses aiohttp + asyncio, Semaphore(8) concurrency.

4 beach resorts × 1 airport × 2 durations × 3 party sizes = 24 concurrent API calls.
Appends to _data/prices_markwarner_summer.csv. One git commit+push per resort.

Usage:
    python markwarner_summer_checker.py           # Normal run
    python markwarner_summer_checker.py --test    # Fetch and print, no file writes
    python markwarner_summer_checker.py --verify  # One API call per resort to confirm connectivity
"""

import asyncio
import aiohttp
import csv
import os
import random
import subprocess
import time
import argparse
from datetime import datetime, date, timedelta
from pathlib import Path

# ─────────────────────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────────────────────

# resort_id: embedded in resort page HTML as :resort-id="N"
# Verified 2026-06-22 by fetching /sun-holidays/*/resort-slug/ and grepping :resort-id
RESORTS = [
    {
        "name":      "Aeolian Village Beach Resort",
        "slug":      "aeolian-village",
        "resort_id": 26928,
        "airports":  ["LGW"],
        "country":   "Greece",
        "url_path":  "sun-holidays/greece/aeolian-village",
    },
    {
        "name":      "Lemnos Beach Resort",
        "slug":      "lemnos-beach-resort",
        "resort_id": 8,
        "airports":  ["LGW"],
        "country":   "Greece",
        "url_path":  "sun-holidays/greece/lemnos-beach-resort",
    },
    {
        "name":      "Paleros Beach Resort",
        "slug":      "paleros-beach-resort",
        "resort_id": 19300,
        "airports":  ["LGW", "MAN", "EDI", "BRS"],
        "country":   "Greece",
        "url_path":  "sun-holidays/greece/paleros-beach-resort",
    },
    {
        "name":      "Phokaia Beach Resort",
        "slug":      "phokaia-beach-resort",
        "resort_id": 16797,
        "airports":  ["BHX", "LGW", "MAN", "STN", "LTN"],
        "country":   "Turkey",
        "url_path":  "sun-holidays/turkey/phokaia-beach-resort",
    },
]

DURATIONS = [7, 14]

PARTY_SIZES = [
    {"label": "2A",   "adults": 2, "children": 0, "child_ages": []},
    {"label": "2A1C", "adults": 2, "children": 1, "child_ages": [7]},
    {"label": "2A2C", "adults": 2, "children": 2, "child_ages": [7, 10]},
]

API_URL  = "https://www.markwarner.co.uk/resort/getresortsearchcriteria"
CSV_FILE = "_data/prices_markwarner_summer.csv"

CSV_HEADERS = [
    "timestamp", "resort_id", "resort_code", "airport", "party_size",
    "start_date", "end_date", "duration_nights", "price", "signal",
    "days_before_departure", "day_of_week_sampled",
    "price_first_seen", "price_min_seen", "price_max_seen", "is_cheapest_ever",
]

_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Mobile/15E148 Safari/604.1",
]

# ─────────────────────────────────────────────────────────────
# API
# ─────────────────────────────────────────────────────────────

def _get_headers(resort):
    return {
        "User-Agent":       random.choice(_USER_AGENTS),
        "Accept":           "application/json, text/plain, */*",
        "Accept-Language":  "en-GB,en;q=0.9",
        "Content-Type":     "application/json",
        "Referer":          f"https://www.markwarner.co.uk/{resort['url_path']}",
        "Origin":           "https://www.markwarner.co.uk",
        "X-Requested-With": "XMLHttpRequest",
    }


async def fetch_combo_async(session, semaphore, resort, airport, duration, party, retries=4):
    """
    One API call for (resort × airport × duration × party_size).
    Returns (valid_dates, status).
    """
    today = datetime.utcnow().strftime("%Y-%m-%d")
    payload = {
        "resortId":    resort["resort_id"],
        "adults":      party["adults"],
        "children":    party["children"],
        "infants":     0,
        "childAges":   party["child_ages"],
        "infantAges":  [],
        "airport":     airport,
        "duration":    duration,
        "checkIn":     today,
        "adultNames":  [],
        "childNames":  [],
        "infantNames": [],
    }
    label = f"{resort['slug']}/{airport}/{duration}n/{party['label']}"

    async with semaphore:
        await asyncio.sleep(random.uniform(0.3, 1.5))
        last_error = None
        for attempt in range(1, retries + 1):
            try:
                timeout = aiohttp.ClientTimeout(total=25)
                async with session.post(
                    API_URL,
                    json=payload,
                    headers=_get_headers(resort),
                    timeout=timeout,
                ) as r:
                    if r.status == 429:
                        wait = (2 ** attempt) + random.uniform(0, 2)
                        print(f"  429 {label} — retry {attempt}/{retries} in {wait:.1f}s")
                        await asyncio.sleep(wait)
                        continue
                    if r.status in (403, 503):
                        print(f"  HTTP {r.status} {label} — blocking response")
                        return [], "blocking"
                    if r.status != 200:
                        print(f"  HTTP {r.status} {label} — skipping")
                        return [], "error"
                    data = await r.json()
                    if not data.get("success"):
                        print(f"  API success=false for {label}")
                        return [], "empty"
                    valid_dates = data.get("model", {}).get("validDates", [])
                    return valid_dates, "ok"
            except asyncio.TimeoutError:
                last_error = f"Timeout (attempt {attempt}/{retries})"
            except Exception as e:
                last_error = str(e)
            if attempt < retries:
                wait = (2 ** attempt) + random.uniform(0, 1)
                await asyncio.sleep(wait)

        print(f"  {label} failed after {retries} attempts: {last_error}")
        return [], "error"

# ─────────────────────────────────────────────────────────────
# SIGNAL LOGIC
# ─────────────────────────────────────────────────────────────

def calculate_signal(price_history):
    if not price_history or len(price_history) < 2:
        return "hold"
    prices      = [p["price"] for p in price_history]
    current     = prices[-1]
    lookback_14 = prices[-14] if len(prices) >= 14 else prices[0]
    move_14     = current - lookback_14
    avg         = sum(prices) / len(prices)
    if move_14 <= -50 and current < avg:
        return "favourable"
    elif move_14 >= 50:
        return "watch"
    elif current < avg and len(prices) >= 7:
        return "watch"
    else:
        return "hold"

# ─────────────────────────────────────────────────────────────
# CSV
# ─────────────────────────────────────────────────────────────

def load_all_price_stats():
    """Single-pass read: historical min/max/first per (resort_id, airport, party_size, start_date, duration)."""
    stats = {}
    if not Path(CSV_FILE).exists():
        return stats
    with open(CSV_FILE, newline="") as f:
        for row in csv.DictReader(f):
            raw = row.get("price", "")
            if not raw:
                continue
            try:
                price = int(raw)
            except (ValueError, TypeError):
                continue
            dur = int(row["duration_nights"]) if row.get("duration_nights") else 7
            key = (row["resort_id"], row.get("airport", ""), row["party_size"], row["start_date"], dur)
            if key not in stats:
                stats[key] = {"min": price, "max": price, "first": price}
            else:
                s = stats[key]
                s["min"] = min(s["min"], price)
                s["max"] = max(s["max"], price)
    return stats


def load_price_history_bulk():
    """Single-pass read: {(resort_id, airport, party_size, start_date, duration): [{date, price}...]}."""
    if not Path(CSV_FILE).exists():
        return {}
    raw = {}
    with open(CSV_FILE, newline="") as f:
        for row in csv.DictReader(f):
            if not row.get("price"):
                continue
            try:
                price = int(row["price"])
            except (ValueError, TypeError):
                continue
            dur = int(row["duration_nights"]) if row.get("duration_nights") else 7
            key = (row["resort_id"], row.get("airport", ""), row["party_size"], row["start_date"], dur)
            if key not in raw:
                raw[key] = {}
            raw[key][row["timestamp"][:10]] = price
    return {
        k: [{"date": d, "price": p} for d, p in sorted(v.items())]
        for k, v in raw.items()
    }


def log_to_csv(rows, test_mode=False):
    if test_mode:
        print(f"  [test] Would write {len(rows)} rows to {CSV_FILE}")
        return
    file_exists = Path(CSV_FILE).exists()
    with open(CSV_FILE, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADERS, lineterminator='\n')
        if not file_exists:
            writer.writeheader()
        writer.writerows(rows)

# ─────────────────────────────────────────────────────────────
# GIT OPERATIONS
# ─────────────────────────────────────────────────────────────

_SSH_KEY = os.path.expanduser("~/.ssh/booking_window_deploy")


def _run_git(cmd):
    env = os.environ.copy()
    if os.path.exists(_SSH_KEY):
        env["GIT_SSH_COMMAND"] = f"ssh -i {_SSH_KEY} -o StrictHostKeyChecking=no"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, env=env)
    return result.returncode, result.stdout.strip(), result.stderr.strip()


def git_setup():
    _run_git("git config user.name 'Booking Window Bot'")
    _run_git("git config user.email 'bot@bookingwindow.co.uk'")


def git_push_with_retry(label, max_attempts=3):
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            capture_output=True, text=True
        )
        remote_url = result.stdout.strip()
        if remote_url.startswith("git@github.com:"):
            repo_path = remote_url.replace("git@github.com:", "")
            remote_url = f"https://x-access-token:{token}@github.com/{repo_path}"
        elif "github.com" in remote_url and not remote_url.startswith("https://x-access-token"):
            remote_url = remote_url.replace("https://", f"https://x-access-token:{token}@")
        push_target = remote_url
        push_env = os.environ.copy()
    else:
        push_target = "origin"
        push_env = os.environ.copy()
        if os.path.exists(_SSH_KEY):
            push_env["GIT_SSH_COMMAND"] = f"ssh -i {_SSH_KEY} -o StrictHostKeyChecking=no"

    for attempt in range(1, max_attempts + 1):
        subprocess.run(
            ["git", "pull", "--rebase", push_target, "main"],
            capture_output=True, env=push_env
        )
        result = subprocess.run(
            ["git", "push", push_target, "main"],
            capture_output=True, text=True, env=push_env
        )
        if result.returncode == 0:
            return True
        err = result.stderr.strip()
        print(f"  [{label}] Push attempt {attempt}/{max_attempts} failed: {err[:120]}")
        if attempt < max_attempts:
            time.sleep(2 ** attempt + random.uniform(0, 1))
    return False


def git_commit_resort(resort_slug, run_date, retries=3):
    date_str   = run_date.isoformat()
    commit_msg = f"data: {resort_slug} summer prices {date_str}"

    rc, _, err = _run_git(f"git add {CSV_FILE}")
    if rc != 0:
        print(f"  [{resort_slug}] git add failed: {err}")
        return

    rc, out, err = _run_git(f'git commit -m "{commit_msg}"')
    if rc != 0:
        combined = out + err
        if "nothing to commit" in combined or "nothing added" in combined:
            print(f"  [{resort_slug}] Nothing to commit — skipping push")
        else:
            print(f"  [{resort_slug}] git commit failed: {err}")
        return

    if git_push_with_retry(resort_slug, retries):
        print(f"  [{resort_slug}] Pushed: {commit_msg}")
    else:
        print(f"  [{resort_slug}] All push retries exhausted — data saved locally, run continues")

# ─────────────────────────────────────────────────────────────
# PROCESS RESULTS
# ─────────────────────────────────────────────────────────────

def process_resort_results(resort, combo_results, historical_stats, history_bulk, timestamp, run_date):
    """
    Convert raw API results into CSV rows for one resort.
    combo_results: list of ((airport, duration, party), (valid_dates, status))
    """
    all_rows   = []
    any_block  = False
    today_str  = run_date.isoformat()

    for (airport, duration, party), (valid_dates, status) in combo_results:
        if status == "blocking":
            any_block = True
            continue
        if not valid_dates:
            continue

        label = f"{airport}/{duration}n/{party['label']}"
        sample_printed = 0

        for entry in valid_dates:
            dep_str = entry.get("d", "")
            if not dep_str:
                continue
            dep_date = dep_str[:10]
            price_raw = entry.get("pr")
            if price_raw is None:
                continue
            try:
                price = int(price_raw)
            except (ValueError, TypeError):
                continue

            end_date = (
                datetime.strptime(dep_date, "%Y-%m-%d") + timedelta(days=duration)
            ).strftime("%Y-%m-%d")

            key = (resort["slug"], airport, party["label"], dep_date, duration)
            stat = historical_stats.get(key)
            if stat:
                min_seen    = min(stat["min"], price)
                max_seen    = max(stat["max"], price)
                first_seen  = stat["first"]
                is_cheapest = 1 if price <= stat["min"] else 0
            else:
                min_seen    = price
                max_seen    = price
                first_seen  = price
                is_cheapest = 1

            hist_key = (resort["slug"], airport, party["label"], dep_date, duration)
            history  = list(history_bulk.get(hist_key, []))
            if not any(h["date"] == today_str for h in history):
                history.append({"date": today_str, "price": price})
            history.sort(key=lambda x: x["date"])
            signal = calculate_signal(history[-30:])

            dep_dt      = datetime.strptime(dep_date, "%Y-%m-%d").date()
            days_before = (dep_dt - run_date).days
            dow_sampled = run_date.weekday()

            all_rows.append({
                "timestamp":             timestamp,
                "resort_id":             resort["slug"],
                "resort_code":           str(resort["resort_id"]),
                "airport":               airport,
                "party_size":            party["label"],
                "start_date":            dep_date,
                "end_date":              end_date,
                "duration_nights":       duration,
                "price":                 price,
                "signal":                signal,
                "days_before_departure": days_before,
                "day_of_week_sampled":   dow_sampled,
                "price_first_seen":      first_seen,
                "price_min_seen":        min_seen,
                "price_max_seen":        max_seen,
                "is_cheapest_ever":      is_cheapest,
            })

            if sample_printed < 2:
                print(f"    [{label}] {dep_date}  £{price:,}  (signal: {signal})")
                sample_printed += 1

        count = len([r for r in all_rows if r["airport"] == airport and r["duration_nights"] == duration and r["party_size"] == party["label"] and r["resort_id"] == resort["slug"]])
        if count > 2:
            print(f"    [{label}] ... and {count - 2} more rows")

    if any_block:
        print(f"  WARNING: Mark Warner may be blocking this IP for {resort['slug']}.")

    return all_rows

# ─────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────

async def main_async(args):
    timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    run_date  = date.today()

    if args.verify:
        print("Running connectivity check — one call per resort...")
        semaphore = asyncio.Semaphore(4)
        connector = aiohttp.TCPConnector(limit=8)
        async with aiohttp.ClientSession(connector=connector) as session:
            for resort in RESORTS:
                party   = PARTY_SIZES[0]
                airport = resort["airports"][0]
                dates, status = await fetch_combo_async(
                    session, semaphore, resort, airport, 7, party, retries=2
                )
                if dates:
                    sample = dates[0]
                    print(f"  {resort['name']}: {sample.get('d','')[:10]}  £{sample.get('pr','?'):,} total — OK")
                else:
                    print(f"  {resort['name']}: no dates (status: {status})")
        return

    if not args.test:
        git_setup()

    historical_stats = load_all_price_stats()
    history_bulk     = load_price_history_bulk()

    # Build the full task list: (resort, airport, duration, party)
    # Group tasks by resort so we can commit per-resort
    semaphore = asyncio.Semaphore(8)
    connector = aiohttp.TCPConnector(limit=10, ttl_dns_cache=300)

    total_rows = 0

    async with aiohttp.ClientSession(connector=connector) as session:

        for resort in RESORTS:
            combos = [
                (airport, duration, party)
                for airport in resort["airports"]
                for duration in DURATIONS
                for party in PARTY_SIZES
            ]

            print(f"\n[{resort['name']} — {resort['country']}]")
            print(f"  {len(combos)} combinations: {len(resort['airports'])} airport(s) × {len(DURATIONS)} durations × {len(PARTY_SIZES)} party sizes")

            tasks   = [
                fetch_combo_async(session, semaphore, resort, ap, dur, p)
                for (ap, dur, p) in combos
            ]
            results = await asyncio.gather(*tasks)

            combo_results = list(zip(combos, results))
            rows = process_resort_results(
                resort, combo_results, historical_stats, history_bulk, timestamp, run_date
            )

            print(f"  {len(rows)} rows collected for {resort['name']}")

            if not rows:
                print(f"  WARNING: No rows for {resort['name']} — skipping commit")
                continue

            if args.test:
                print(f"  [--test] Would write {len(rows)} rows to {CSV_FILE}")
            else:
                log_to_csv(rows)
                git_commit_resort(resort["slug"], run_date)

            total_rows += len(rows)

    print(f"\nTotal: {total_rows} rows across {len(RESORTS)} resorts")
    if args.test:
        print("[--test] No files written.")
    else:
        print(f"Done. {total_rows} rows appended to {CSV_FILE}")


def main():
    parser = argparse.ArgumentParser(description="Mark Warner summer beach price checker (async)")
    parser.add_argument("--test",   action="store_true", help="Fetch and print, no file writes")
    parser.add_argument("--verify", action="store_true", help="One API call per resort to confirm connectivity")
    args = parser.parse_args()

    now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    print(f"\n{'='*60}")
    print(f"Mark Warner Summer price checker (async) — {now_str}")
    if args.test:
        print("  MODE: test (no files will be written)")
    print(f"{'='*60}\n")

    asyncio.run(main_async(args))


if __name__ == "__main__":
    main()
