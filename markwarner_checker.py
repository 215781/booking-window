#!/usr/bin/env python3
"""
markwarner_checker.py — When To Book: Mark Warner price checker (async)
Uses aiohttp + asyncio for concurrent party-size requests (Semaphore(8)).
After all party sizes complete, rows are appended to CSV and a git commit+push is made.

API: POST https://www.markwarner.co.uk/resort/getresortsearchcriteria
     One call per party size → validDates[] with pr (promo total) for the full season.

Usage:
    python markwarner_checker.py           # Normal run
    python markwarner_checker.py --test    # Fetch and print, no file writes
    python markwarner_checker.py --verify  # One API call to confirm connectivity
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

RESORT_SLUG = "chalet-hotel-lecrin"   # resort_id in CSV (slug, stable)
RESORT_CODE = "957"                    # resort_code in CSV (Mark Warner numeric ID)
RESORT_NAME = "Chalet Hotel L'Écrin"
RESORT_ID   = 957                      # integer for API payload
AIRPORT     = "LGW"
DURATION    = 7

API_URL  = "https://www.markwarner.co.uk/resort/getresortsearchcriteria"
CSV_FILE = "_data/prices_markwarner.csv"

CSV_HEADERS = [
    "timestamp", "resort_id", "resort_code", "party_size",
    "start_date", "end_date", "duration_nights", "price", "signal",
    "days_before_departure", "day_of_week_sampled",
    "price_first_seen", "price_min_seen", "price_max_seen", "is_cheapest_ever",
]

PARTY_SIZES = [
    {"label": "2A",   "adults": 2, "children": 0, "child_ages": []},
    {"label": "2A1C", "adults": 2, "children": 1, "child_ages": [7]},
    {"label": "2A2C", "adults": 2, "children": 2, "child_ages": [7, 10]},
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

def _get_headers():
    return {
        "User-Agent":       random.choice(_USER_AGENTS),
        "Accept":           "application/json, text/plain, */*",
        "Accept-Language":  "en-GB,en;q=0.9",
        "Content-Type":     "application/json",
        "Referer":          "https://www.markwarner.co.uk/ski-holidays/france/chalet-hotel-lecrin",
        "Origin":           "https://www.markwarner.co.uk",
        "X-Requested-With": "XMLHttpRequest",
    }


async def fetch_party_async(session, semaphore, party, retries=4):
    """
    POST for one party size. Returns (valid_dates, status).
    valid_dates: list of {d, pr, prpp, wp, wppp, u, pc} dicts from the API.
    status: "ok" | "blocking" | "empty" | "error"
    """
    today = datetime.utcnow().strftime("%Y-%m-%d")
    payload = {
        "resortId":    RESORT_ID,
        "adults":      party["adults"],
        "children":    party["children"],
        "infants":     0,
        "childAges":   party["child_ages"],
        "infantAges":  [],
        "airport":     AIRPORT,
        "duration":    DURATION,
        "checkIn":     today,
        "adultNames":  [],
        "childNames":  [],
        "infantNames": [],
    }

    async with semaphore:
        await asyncio.sleep(random.uniform(0.5, 2.0))
        last_error = None
        for attempt in range(1, retries + 1):
            try:
                timeout = aiohttp.ClientTimeout(total=25)
                async with session.post(
                    API_URL, json=payload, headers=_get_headers(), timeout=timeout
                ) as r:
                    if r.status == 429:
                        wait = (2 ** attempt) + random.uniform(0, 2)
                        print(f"  429 {party['label']} — retry {attempt}/{retries} in {wait:.1f}s")
                        await asyncio.sleep(wait)
                        continue
                    if r.status in (403, 503):
                        print(f"  HTTP {r.status} {party['label']} — blocking response")
                        return [], "blocking"
                    if r.status != 200:
                        print(f"  HTTP {r.status} {party['label']} — skipping")
                        return [], "error"
                    data = await r.json()
                    if not data.get("success"):
                        print(f"  API success=false for {party['label']}")
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

        print(f"  {party['label']} failed after {retries} attempts: {last_error}")
        return [], "error"

# ─────────────────────────────────────────────────────────────
# SIGNAL LOGIC (mirrors clubmed_checker.py)
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
    """Single-pass read to get historical min/max/first per (resort_id, party_size, start_date, duration)."""
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
            key = (row["resort_id"], row["party_size"], row["start_date"], dur)
            if key not in stats:
                stats[key] = {"min": price, "max": price, "first": price}
            else:
                s = stats[key]
                s["min"] = min(s["min"], price)
                s["max"] = max(s["max"], price)
    return stats


def load_price_history_bulk():
    """Single-pass read returning {(party_size, start_date): [{date, price}, ...]}."""
    if not Path(CSV_FILE).exists():
        return {}
    raw = {}
    with open(CSV_FILE, newline="") as f:
        for row in csv.DictReader(f):
            if row.get("resort_id") != RESORT_SLUG or not row.get("price"):
                continue
            try:
                price = int(row["price"])
            except (ValueError, TypeError):
                continue
            key = (row["party_size"], row["start_date"])
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
# GIT OPERATIONS (same pattern as clubmed_checker.py)
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


def git_commit_resort(resort_label, run_date, retries=3):
    """Commit and push CSV rows for this resort. Retries on push failure."""
    date_str   = run_date.isoformat()
    commit_msg = f"data: {resort_label} prices {date_str}"

    rc, _, err = _run_git(f"git add {CSV_FILE}")
    if rc != 0:
        print(f"  [{resort_label}] git add failed: {err}")
        return

    rc, out, err = _run_git(f'git commit -m "{commit_msg}"')
    if rc != 0:
        combined = out + err
        if "nothing to commit" in combined or "nothing added" in combined:
            print(f"  [{resort_label}] Nothing to commit — skipping push")
        else:
            print(f"  [{resort_label}] git commit failed: {err}")
        return

    for attempt in range(1, retries + 1):
        _run_git("git pull --rebase origin main")
        rc, _, err = _run_git("git push origin main")
        if rc == 0:
            print(f"  [{resort_label}] Pushed: {commit_msg}")
            return
        print(f"  [{resort_label}] Push failed (attempt {attempt}/{retries}): {err[:120]}")
        if attempt < retries:
            wait = (2 ** attempt) + random.uniform(0, 1)
            time.sleep(wait)

    print(f"  [{resort_label}] All push retries exhausted — data saved locally, run continues")

# ─────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────

async def main_async(args):
    timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    run_date  = date.today()

    if args.verify:
        sem = asyncio.Semaphore(1)
        connector = aiohttp.TCPConnector(limit=1)
        async with aiohttp.ClientSession(connector=connector) as session:
            valid_dates, status = await fetch_party_async(session, sem, PARTY_SIZES[0])
        if valid_dates:
            first = valid_dates[0]
            price = first.get("pr", "?")
            print(f"  {first.get('d')}  £{price:,} total")
            print("OK — connectivity confirmed")
        else:
            print(f"  No dates returned (status: {status}) — API may be unreachable")
        return

    if not args.test:
        git_setup()

    historical_stats = load_all_price_stats()
    history_bulk     = load_price_history_bulk()

    party_sizes_this_run = list(PARTY_SIZES)
    random.shuffle(party_sizes_this_run)

    print(f"\n[{RESORT_NAME}, {AIRPORT}] Fetching {len(PARTY_SIZES)} party sizes concurrently (semaphore=8)...")

    semaphore = asyncio.Semaphore(8)
    connector = aiohttp.TCPConnector(limit=10, ttl_dns_cache=300)

    async with aiohttp.ClientSession(connector=connector) as session:
        tasks   = [fetch_party_async(session, semaphore, p) for p in party_sizes_this_run]
        results = await asyncio.gather(*tasks)

    all_rows  = []
    any_block = False

    for party, (valid_dates, status) in zip(party_sizes_this_run, results):
        if status == "blocking":
            any_block = True
            print(f"  {party['label']}: blocking response — skipping")
            continue
        if not valid_dates:
            print(f"  {party['label']}: no dates returned")
            continue

        print(f"  {party['label']}: {len(valid_dates)} departure dates")
        sample_printed = 0

        for entry in valid_dates:
            dep_date = entry.get("d")
            if not dep_date:
                continue
            price_raw = entry.get("pr")
            if price_raw is None:
                continue
            try:
                price = int(price_raw)
            except (ValueError, TypeError):
                continue

            end_date = (
                datetime.strptime(dep_date, "%Y-%m-%d") + timedelta(days=DURATION)
            ).strftime("%Y-%m-%d")

            key = (RESORT_SLUG, party["label"], dep_date, DURATION)
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

            hist_key = (party["label"], dep_date)
            history  = list(history_bulk.get(hist_key, []))
            today_str = run_date.isoformat()
            if not any(h["date"] == today_str for h in history):
                history.append({"date": today_str, "price": price})
            history.sort(key=lambda x: x["date"])
            signal = calculate_signal(history[-30:])

            dep_dt      = datetime.strptime(dep_date, "%Y-%m-%d").date()
            days_before = (dep_dt - run_date).days
            dow_sampled = run_date.weekday()

            all_rows.append({
                "timestamp":             timestamp,
                "resort_id":             RESORT_SLUG,
                "resort_code":           RESORT_CODE,
                "party_size":            party["label"],
                "start_date":            dep_date,
                "end_date":              end_date,
                "duration_nights":       DURATION,
                "price":                 price,
                "signal":                signal,
                "days_before_departure": days_before,
                "day_of_week_sampled":   dow_sampled,
                "price_first_seen":      first_seen,
                "price_min_seen":        min_seen,
                "price_max_seen":        max_seen,
                "is_cheapest_ever":      is_cheapest,
            })

            if sample_printed < 3:
                print(f"    {dep_date}  £{price:,}  (signal: {signal})")
                sample_printed += 1

        if len(valid_dates) > 3:
            print(f"    ... and {len(valid_dates) - 3} more")

    if any_block:
        print("\nWARNING: Mark Warner may be blocking this IP.")

    if not all_rows:
        print("\nWARNING: No price rows collected.")
        return

    print(f"\nTotal: {len(all_rows)} rows across {len(PARTY_SIZES)} party sizes")

    if args.test:
        print("[--test] No files written.")
        return

    log_to_csv(all_rows)
    git_commit_resort("markwarner", run_date)
    print(f"\nDone. {len(all_rows)} rows appended to {CSV_FILE}")


def main():
    parser = argparse.ArgumentParser(description="Mark Warner price checker (async)")
    parser.add_argument("--test",   action="store_true", help="Fetch and print, no file writes")
    parser.add_argument("--verify", action="store_true", help="One API call to confirm connectivity")
    args = parser.parse_args()

    now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    print(f"\n{'='*60}")
    print(f"Mark Warner price checker (async) — {now_str}")
    if args.test:
        print("  MODE: test (no files will be written)")
    print(f"{'='*60}\n")

    asyncio.run(main_async(args))


if __name__ == "__main__":
    main()
