#!/usr/bin/env python3
"""
clubmed_ski_international_checker.py — When To Book international ski resort price checker

Covers Italian Alps, Swiss Alps, Japan, and China Club Med ski resorts.
Uses aiohttp + asyncio, same architecture as clubmed_summer_checker.py.

Resort codes verified via Club Med GraphQL API productId probe — May 2026.

Usage:
    python clubmed_ski_international_checker.py              # Normal run
    python clubmed_ski_international_checker.py --test       # No file writes
    python clubmed_ski_international_checker.py --verify     # One API call, exit
    python clubmed_ski_international_checker.py --inject-only # Rebuild HTML block from CSV
"""

import asyncio
import aiohttp
import json
import csv
import os
import random
import smtplib
import argparse
import subprocess
import time
from datetime import datetime, date, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path

# ─────────────────────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────────────────────

CSV_FILE  = "_data/prices_clubmed_ski_international.csv"
HTML_FILE = "clubmed/index.html"

GMAIL_ADDRESS  = os.environ.get("GMAIL_ADDRESS", "")
GMAIL_APP_PASS = os.environ.get("GMAIL_APP_PASS", "")
ALERT_TO       = os.environ.get("ALERT_TO", "")

# ─────────────────────────────────────────────────────────────
# RESORT CONFIG
# ─────────────────────────────────────────────────────────────

def weekday_dates_in_month(year, month, weekday):
    dates = []
    d = date(year, month, 1)
    while d.weekday() != weekday:
        d += timedelta(days=1)
    while d.month == month:
        dates.append(d.strftime("%Y-%m-%d"))
        d += timedelta(days=7)
    return dates

# Winter 2026/27 season: December 2026 – April 2027
WINTER_MONTHS = [(2026, 12), (2027, 1), (2027, 2), (2027, 3), (2027, 4)]

def make_windows(departure_day, durations=(7,)):
    """
    Generate departure windows for the full winter season.
    departure_day: int 0-6 (Mon-Sun), or None to use Sunday(6).
    """
    weekdays = [departure_day] if departure_day is not None else [6]
    windows = []
    for duration_nights in durations:
        for yr, mo in WINTER_MONTHS:
            for wd in weekdays:
                for s in weekday_dates_in_month(yr, mo, wd):
                    windows.append({
                        "startDate": s,
                        "endDate":   (datetime.strptime(s, "%Y-%m-%d") + timedelta(days=duration_nights)).strftime("%Y-%m-%d"),
                        "duration":  duration_nights,
                    })
    return windows

_COMBOS = [
    {"partySize": "2A",     "adults": 2, "children": 0, "birthdates": []},
    {"partySize": "2A1I",   "adults": 2, "children": 1, "birthdates": ["2024-03-15"]},                      # infant 0-3
    {"partySize": "2A1C",   "adults": 2, "children": 1, "birthdates": ["2018-09-01"]},                      # child 4-11
    {"partySize": "2A1J",   "adults": 2, "children": 1, "birthdates": ["2013-06-01"]},                      # junior 12+
    {"partySize": "2A1C1J", "adults": 2, "children": 2, "birthdates": ["2018-09-01", "2013-06-01"]},        # child + junior
    {"partySize": "2A2C",   "adults": 2, "children": 2, "birthdates": ["2018-09-01", "2016-06-01"]},        # 2 children 4-11 band
    {"partySize": "3A",     "adults": 3, "children": 0, "birthdates": []},
    {"partySize": "3A1C",   "adults": 3, "children": 1, "birthdates": ["2018-09-01"]},                      # 3 adults + child 4-11
]

RESORTS = [
    {
        "id":            "pragelato-sestriere",
        "name":          "Pragelato Sestriere",
        "resortCode":    "PRAC_WINTER",       # confirmed May 2026 — Italian Alps
        "bookingUrl":    "https://www.clubmed.co.uk/r/pragelato-sestriere/w",
        "departure_day": 6,                   # Sunday
    },
    {
        "id":            "st-moritz-roi-soleil",
        "name":          "St. Moritz Roi Soleil",
        "resortCode":    "SMRC",              # confirmed May 2026 — Swiss Alps (no _WINTER suffix)
        "bookingUrl":    "https://www.clubmed.co.uk/r/st-moritz-roi-soleil/w",
        "departure_day": 6,                   # Sunday
    },
    {
        "id":            "tomamu-hokkaido",
        "name":          "Tomamu Hokkaido",
        "resortCode":    "TOMC_WINTER",       # confirmed May 2026 — Japan
        "bookingUrl":    "https://www.clubmed.co.uk/r/tomamu-hokkaido/w",
        "departure_day": 6,                   # Sunday
    },
    {
        "id":            "kiroro-peak",
        "name":          "Kiroro Peak",
        "resortCode":    "KIPC_WINTER",       # confirmed May 2026 — Japan
        "bookingUrl":    "https://www.clubmed.co.uk/r/kiroro-peak/w",
        "departure_day": 6,                   # Sunday
    },
    {
        "id":            "kiroro-grand",
        "name":          "Kiroro Grand",
        "resortCode":    "KIGC_WINTER",       # confirmed May 2026 — Japan
        "bookingUrl":    "https://www.clubmed.co.uk/r/kiroro-grand/w",
        "departure_day": 6,                   # Sunday
    },
    {
        "id":            "sahoro-hokkaido",
        "name":          "Sahoro Hokkaido",
        "resortCode":    "SAOC_WINTER",       # confirmed May 2026 — Japan
        "bookingUrl":    "https://www.clubmed.co.uk/r/sahoro-hokkaido/w",
        "departure_day": 6,                   # Sunday
    },
    {
        "id":            "beidahu",
        "name":          "Beidahu",
        "resortCode":    "BEIC_WINTER",       # confirmed May 2026 — China
        "bookingUrl":    "https://www.clubmed.co.uk/r/beidahu/w",
        "departure_day": 6,                   # Sunday
    },
    {
        "id":            "changbaishan",
        "name":          "Changbaishan",
        "resortCode":    "CBAC_WINTER",       # confirmed May 2026 — China (Jan+ pricing; Dec window may not be open yet)
        "bookingUrl":    "https://www.clubmed.co.uk/r/changbaishan/w",
        "departure_day": 6,                   # Sunday
    },
]

# Pre-compute windows per resort
for _r in RESORTS:
    _r["windows"] = make_windows(_r["departure_day"])

# ─────────────────────────────────────────────────────────────
# GRAPHQL API
# ─────────────────────────────────────────────────────────────

GRAPHQL_URL = "https://graphql.dcx.clubmed/"

_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Mobile/15E148 Safari/604.1",
]

def _get_headers():
    return {
        "Content-Type":    "application/json",
        "Accept":          "application/graphql-response+json,application/json;q=0.9",
        "Accept-Language": "en-GB",
        "Origin":          "https://www.clubmed.co.uk",
        "Referer":         "https://www.clubmed.co.uk/",
        "User-Agent":      random.choice(_USER_AGENTS),
    }

QUERY = """mutation SearchPrice($id: ID!, $options: SearchPriceOptions) {
    searchPrice(id: $id, options: $options) {
        productId
        price { bestPrice }
        noPrice { reason }
    }
}"""

async def fetch_price_async(session, semaphore, resort_code, adults, children, birthdates,
                             start_date, end_date, retries=4):
    """Async price fetch with semaphore control, 429 backoff, and retry on error.

    Returns (price_or_None, status) where status is:
      "ok"           — price returned successfully
      "not_for_sale" — API says period not on sale yet
      "closed"       — resort closed for this period
      "no_price"     — API returned noPrice for another reason
      "error"        — network/HTTP failure after all retries
    """
    payload = {
        "operationName": "SearchPrice",
        "variables": {
            "id": resort_code,
            "options": {
                "adults":               adults,
                "children":             children,
                "startDate":            start_date,
                "endDate":              end_date,
                "flexible":             None,
                "birthdates":           birthdates,
                "departureCity":        "NO",
                "isExclusiveSpacePage": False,
                "shouldGetRealPrice":   True,
            },
        },
        "query": QUERY,
    }

    async with semaphore:
        await asyncio.sleep(random.uniform(0.3, 1.2))

        last_error = None
        for attempt in range(1, retries + 1):
            try:
                timeout = aiohttp.ClientTimeout(total=25)
                async with session.post(
                    GRAPHQL_URL, json=payload, headers=_get_headers(), timeout=timeout
                ) as r:
                    if r.status == 429:
                        wait = (2 ** attempt) + random.uniform(0, 2)
                        print(f"  429 {resort_code} {start_date} — retry {attempt}/{retries} in {wait:.1f}s")
                        await asyncio.sleep(wait)
                        continue
                    if r.status != 200:
                        print(f"  HTTP {r.status} for {resort_code} {start_date} — skipping")
                        return None, "error"
                    data = await r.json()
                    result = data.get("data", {}).get("searchPrice", {})
                    price_obj = result.get("price")
                    if price_obj and price_obj.get("bestPrice"):
                        return int(price_obj["bestPrice"]), "ok"
                    no_price = result.get("noPrice")
                    if no_price:
                        reason = no_price.get("reason", "unknown").lower()
                        if "not for sale" in reason:
                            return None, "not_for_sale"
                        elif "closed" in reason:
                            return None, "closed"
                        else:
                            return None, "no_price"
                    return None, "no_price"
            except asyncio.TimeoutError:
                last_error = f"Timeout (attempt {attempt}/{retries})"
            except Exception as e:
                last_error = str(e)
            if attempt < retries:
                wait = (2 ** attempt) + random.uniform(0, 1)
                await asyncio.sleep(wait)

        print(f"  Error {resort_code} {start_date}: {last_error}")
        return None, "error"

# ─────────────────────────────────────────────────────────────
# SIGNAL LOGIC
# ─────────────────────────────────────────────────────────────

def calculate_signal(price_history):
    """Takes a list of {date, price} dicts (oldest first). Returns signal string."""
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
# CSV LOGGING
# ─────────────────────────────────────────────────────────────

CSV_HEADERS = [
    "collected_at", "resort_id", "resort_code", "resort_name", "party_size",
    "departure_date", "end_date", "duration_nights", "price_pp", "currency", "signal",
    "days_before_departure", "day_of_week_sampled",
    "price_first_seen", "price_min_seen", "price_max_seen", "is_cheapest_ever",
]

def log_to_csv(rows, test_mode=False):
    if test_mode:
        print(f"  [test mode] Would have written {len(rows)} rows to {CSV_FILE}")
        return
    file_exists = Path(CSV_FILE).exists()
    with open(CSV_FILE, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADERS, lineterminator='\n')
        if not file_exists:
            writer.writeheader()
        writer.writerows(rows)

def load_price_history_from_csv(resort_id, party_size, departure_date, duration_nights=7):
    if not Path(CSV_FILE).exists():
        return []
    history = []
    with open(CSV_FILE, newline="") as f:
        for row in csv.DictReader(f):
            row_dur = int(row["duration_nights"]) if row.get("duration_nights") else 7
            if (row["resort_id"] == resort_id and
                    row["party_size"] == party_size and
                    row["departure_date"] == departure_date and
                    row_dur == duration_nights and
                    row["price_pp"]):
                history.append({
                    "date":  row["collected_at"][:10],
                    "price": int(row["price_pp"]),
                })
    seen = {}
    for entry in history:
        seen[entry["date"]] = entry["price"]
    return [{"date": d, "price": p} for d, p in sorted(seen.items())]

def load_price_history_for_resort(resort_id):
    """Load all price history for a resort in one CSV pass."""
    if not Path(CSV_FILE).exists():
        return {}
    raw = {}
    with open(CSV_FILE, newline="") as f:
        for row in csv.DictReader(f):
            if row.get("resort_id") != resort_id or not row.get("price_pp"):
                continue
            try:
                price = int(row["price_pp"])
            except (ValueError, TypeError):
                continue
            dur = int(row["duration_nights"]) if row.get("duration_nights") else 7
            key = (row["party_size"], row["departure_date"], dur)
            if key not in raw:
                raw[key] = {}
            raw[key][row["collected_at"][:10]] = price
    return {
        k: [{"date": d, "price": p} for d, p in sorted(v.items())]
        for k, v in raw.items()
    }

def load_all_price_stats():
    stats = {}
    if not Path(CSV_FILE).exists():
        return stats
    with open(CSV_FILE, newline="") as f:
        for row in csv.DictReader(f):
            raw = row.get("price_pp", "")
            if not raw:
                continue
            try:
                price = int(raw)
            except (ValueError, TypeError):
                continue
            dur = int(row["duration_nights"]) if row.get("duration_nights") else 7
            key = (row["resort_id"], row["party_size"], row["departure_date"], dur)
            if key not in stats:
                stats[key] = {"min": price, "max": price, "first": price, "count": 1}
            else:
                s = stats[key]
                s["min"] = min(s["min"], price)
                s["max"] = max(s["max"], price)
                s["count"] += 1
    return stats

# ─────────────────────────────────────────────────────────────
# EMAIL ALERTS
# ─────────────────────────────────────────────────────────────

def send_alert(subject, body):
    if not GMAIL_ADDRESS or not GMAIL_APP_PASS or not ALERT_TO:
        print(f"  Email not configured — alert not sent: {subject}")
        return
    try:
        msg = MIMEMultipart()
        msg["From"]    = GMAIL_ADDRESS
        msg["To"]      = ALERT_TO
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_ADDRESS, GMAIL_APP_PASS)
            server.send_message(msg)
        print(f"  Alert sent: {subject}")
    except Exception as e:
        print(f"  Failed to send alert: {e}")

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
    """Pull then push. Uses GITHUB_TOKEN (HTTPS) if in Actions, else SSH key."""
    token = os.environ.get('GITHUB_TOKEN')
    if token:
        result = subprocess.run(
            ['git', 'remote', 'get-url', 'origin'],
            capture_output=True, text=True
        )
        remote_url = result.stdout.strip()
        if remote_url.startswith('git@github.com:'):
            repo_path = remote_url.replace('git@github.com:', '')
            remote_url = f'https://x-access-token:{token}@github.com/{repo_path}'
        elif 'github.com' in remote_url and not remote_url.startswith('https://x-access-token'):
            remote_url = remote_url.replace('https://', f'https://x-access-token:{token}@')
        push_target = remote_url
        push_env = os.environ.copy()
    else:
        push_target = 'origin'
        push_env = os.environ.copy()
        if os.path.exists(_SSH_KEY):
            push_env['GIT_SSH_COMMAND'] = f'ssh -i {_SSH_KEY} -o StrictHostKeyChecking=no'

    for attempt in range(1, max_attempts + 1):
        subprocess.run(
            ['git', 'pull', '--rebase', push_target, 'main'],
            capture_output=True, env=push_env
        )
        result = subprocess.run(
            ['git', 'push', push_target, 'main'],
            capture_output=True, text=True, env=push_env
        )
        if result.returncode == 0:
            return True
        err = result.stderr.strip()
        print(f"  [{label}] Push attempt {attempt}/{max_attempts} failed: {err[:120]}")
        if attempt < max_attempts:
            time.sleep(2 ** attempt + random.uniform(0, 1))
    return False

def git_commit_resort(resort_code, run_date, retries=3):
    date_str   = run_date.isoformat()
    commit_msg = f"data: {resort_code} international ski prices {date_str}"

    rc, _, err = _run_git(f"git add {CSV_FILE}")
    if rc != 0:
        print(f"  [{resort_code}] git add failed: {err}")
        return

    rc, out, err = _run_git(f'git commit -m "{commit_msg}"')
    if rc != 0:
        combined = out + err
        if "nothing to commit" in combined or "nothing added" in combined:
            print(f"  [{resort_code}] Nothing to commit — skipping push")
        else:
            print(f"  [{resort_code}] git commit failed: {err}")
        return

    if git_push_with_retry(resort_code, retries):
        print(f"  [{resort_code}] Pushed: {commit_msg}")
    else:
        print(f"  [{resort_code}] All push retries exhausted — data saved locally, run continues")

# ─────────────────────────────────────────────────────────────
# ASYNC RESORT PROCESSING
# ─────────────────────────────────────────────────────────────

async def process_resort(session, semaphore, resort, historical_stats, timestamp, run_date,
                          test_mode=False):
    """Fire all API queries for one resort concurrently, then commit results to CSV."""
    rid   = resort["id"]
    rcode = resort["resortCode"]
    rname = resort["name"]
    total_queries = len(_COMBOS) * len(resort["windows"])

    print(f"\n[{rname} / {rcode}] Starting {total_queries} queries (semaphore=8)...")

    task_meta = []
    tasks = []
    for combo in _COMBOS:
        for window in resort["windows"]:
            task_meta.append((combo, window))
            tasks.append(fetch_price_async(
                session, semaphore, rcode,
                combo["adults"], combo["children"], combo["birthdates"],
                window["startDate"], window["endDate"],
            ))

    api_results = await asyncio.gather(*tasks)

    resort_history = load_price_history_for_resort(rid)

    csv_rows       = []
    prices_ok      = 0
    error_count    = 0
    no_price_count = 0

    for (combo, window), (price, fetch_status) in zip(task_meta, api_results):
        sd         = window["startDate"]
        ed         = window["endDate"]
        ps         = combo["partySize"]
        duration_n = window["duration"]
        key        = (rid, ps, sd, duration_n)

        if price is not None:
            prices_ok += 1
        else:
            no_price_count += 1
            if fetch_status == "error":
                error_count += 1

        hist_key = (ps, sd, duration_n)
        history  = list(resort_history.get(hist_key, []))
        if price:
            history.append({"date": timestamp[:10], "price": price})
        signal = calculate_signal(history)

        departure_dt = datetime.strptime(sd, "%Y-%m-%d").date()
        days_before  = (departure_dt - run_date).days
        dow_sampled  = run_date.weekday()

        stat = historical_stats.get(key)
        if stat:
            min_seen    = min(stat["min"], price) if price else stat["min"]
            max_seen    = max(stat["max"], price) if price else stat["max"]
            first_seen  = stat["first"]
            is_cheapest = 1 if (price and price <= stat["min"]) else 0
        else:
            min_seen    = price if price else ""
            max_seen    = price if price else ""
            first_seen  = price if price else ""
            is_cheapest = 1 if price else ""

        csv_rows.append({
            "collected_at":          timestamp,
            "resort_id":             rid,
            "resort_code":           rcode,
            "resort_name":           rname,
            "party_size":            ps,
            "departure_date":        sd,
            "end_date":              ed,
            "duration_nights":       duration_n,
            "price_pp":              price if price else "",
            "currency":              "GBP",
            "signal":                signal,
            "days_before_departure": days_before,
            "day_of_week_sampled":   dow_sampled,
            "price_first_seen":      first_seen,
            "price_min_seen":        min_seen,
            "price_max_seen":        max_seen,
            "is_cheapest_ever":      is_cheapest,
        })

    total = len(csv_rows)
    print(f"  [{rname}] Complete: {prices_ok}/{total} prices OK "
          f"({no_price_count} no-price, {error_count} errors)")

    log_to_csv(csv_rows, test_mode)
    if not test_mode:
        git_commit_resort(rcode, run_date)

    return error_count, no_price_count, total

# ─────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────

async def main_async(args):
    timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    run_date  = date.today()

    git_setup()
    historical_stats = load_all_price_stats()

    resorts_this_run = list(RESORTS)
    random.shuffle(resorts_this_run)

    total_errors   = 0
    total_no_price = 0
    total_rows     = 0

    semaphore = asyncio.Semaphore(8)
    connector = aiohttp.TCPConnector(limit=20, ttl_dns_cache=300)

    async with aiohttp.ClientSession(connector=connector) as session:
        for resort in resorts_this_run:
            errors, no_price, row_count = await process_resort(
                session, semaphore, resort, historical_stats, timestamp, run_date, args.test
            )
            total_errors   += errors
            total_no_price += no_price
            total_rows     += row_count

    print(f"\nAll resorts complete. CSV data committed per-resort.")

    prices_fetched = total_rows - total_no_price
    if total_errors > 0 and total_rows > 0 and total_errors / total_rows > 0.3:
        send_alert(
            "When To Book health alert — international ski checker API errors",
            f"{total_errors}/{total_rows} fetches failed with network/API errors. "
            f"Check the GitHub Actions logs.\n\nRun timestamp: {timestamp}"
        )

    print(f"\nDone. {prices_fetched}/{total_rows} prices fetched successfully.")
    if total_no_price:
        print(f"  {total_no_price} no-price responses "
              f"({total_errors} errors, rest are pre-season/closed).")


# ─────────────────────────────────────────────────────────────
# RESORT METADATA (for --inject-only HTML generation)
# ─────────────────────────────────────────────────────────────

RESORT_META = {
    "pragelato-sestriere":   {"region": "Piedmont, Italian Alps"},
    "st-moritz-roi-soleil":  {"region": "Graubünden, Swiss Alps"},
    "tomamu-hokkaido":       {"region": "Hokkaido, Japan"},
    "kiroro-peak":           {"region": "Hokkaido, Japan"},
    "kiroro-grand":          {"region": "Hokkaido, Japan"},
    "sahoro-hokkaido":       {"region": "Hokkaido, Japan"},
    "beidahu":               {"region": "Jilin, China"},
    "changbaishan":          {"region": "Jilin, China"},
}

def calculate_availability(current_price, history):
    """Simple availability heuristic based on price trend."""
    if len(history) < 7:
        return "good", "stable"
    recent = [h["price"] for h in history[-7:]]
    trend  = recent[-1] - recent[0]
    if trend > 200:
        return "limited", "tightening"
    elif trend > 50:
        return "moderate", "tightening"
    elif trend < -200:
        return "good", "easing"
    return "good", "stable"

def build_resort_data_js():
    """Read international ski CSV and build SKI_INTERNATIONAL_DATA JS for injection into clubmed/index.html."""
    import re as _re
    now_iso = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

    resort_history = {}
    if Path(CSV_FILE).exists():
        with open(CSV_FILE, newline="") as f:
            for row in csv.DictReader(f):
                rid  = row.get("resort_id", "")
                ps   = row.get("party_size", "")
                sd   = row.get("departure_date", "")
                dur  = int(row["duration_nights"]) if row.get("duration_nights") else 7
                raw  = row.get("price_pp", "")
                if not (rid and ps and sd and raw):
                    continue
                try:
                    price = int(raw)
                except (ValueError, TypeError):
                    continue
                key = (rid, ps, sd, dur)
                if key not in resort_history:
                    resort_history[key] = {}
                resort_history[key][row.get("collected_at", "")[:10]] = price

    lines = ["const SKI_INTERNATIONAL_DATA = ["]

    for resort in RESORTS:
        rid   = resort["id"]
        rname = resort["name"]
        rcode = resort["resortCode"]
        meta  = RESORT_META.get(rid, {"region": "—"})

        lines.append("  {")
        lines.append(f'    id: "{rid}",')
        lines.append(f'    name: "{rname}",')
        lines.append(f'    region: "{meta["region"]}",')
        lines.append(f'    resortCode: "{rcode}",')
        lines.append(f'    bookingUrl: "{resort["bookingUrl"]}",')
        lines.append("    combinations: [")

        for combo in _COMBOS:
            ps       = combo["partySize"]
            adults   = combo["adults"]
            children = combo["children"]
            bds_json = json.dumps(combo["birthdates"])

            lines.append("      {")
            lines.append(f'        partySize: "{ps}", adults: {adults}, children: {children}, birthdates: {bds_json},')
            lines.append("        departures: [")

            for window in resort["windows"]:
                sd  = window["startDate"]
                ed  = window["endDate"]
                dur = window["duration"]
                key = (rid, ps, sd, dur)
                daily = resort_history.get(key, {})
                if not daily:
                    continue

                history_sorted = [{"date": d, "price": p} for d, p in sorted(daily.items())]
                history_30 = history_sorted[-30:]
                prices = [h["price"] for h in history_30]
                current_price  = prices[-1]
                previous_price = prices[-14] if len(prices) >= 14 else prices[0]
                signal = calculate_signal(history_30)
                availability, avail_trend = calculate_availability(current_price, history_30)

                dep_dt = datetime.strptime(sd, "%Y-%m-%d")
                end_dt = dep_dt + timedelta(days=dur)
                if dep_dt.month == end_dt.month:
                    display_date = f"{dep_dt.day}–{end_dt.day} {dep_dt.strftime('%b %Y')}"
                else:
                    display_date = f"{dep_dt.strftime('%-d %b')}–{end_dt.strftime('%-d %b %Y')}"

                history_js = json.dumps(history_30)
                lines.append("          {")
                lines.append(f'            duration: {dur}, date: "{sd}", displayDate: "{display_date}",')
                lines.append(f'            currentPrice: {current_price}, previousPrice: {previous_price},')
                lines.append(f'            priceHistory: {history_js},')
                lines.append(f'            availability: "{availability}", availabilityTrend: "{avail_trend}",')
                lines.append(f'            signal: "{signal}", lastUpdated: "{now_iso}"')
                lines.append("          },")

            lines.append("        ]")
            lines.append("      },")

        lines.append("    ]")
        lines.append("  },")

    lines.append("];")
    return "\n".join(lines)

def inject_into_html(js_string, test_mode=False):
    """Replace the SKI_INTERNATIONAL_DATA block in clubmed/index.html."""
    import re as _re
    if not Path(HTML_FILE).exists():
        print(f"WARNING: {HTML_FILE} not found — skipping HTML injection.")
        return
    with open(HTML_FILE, "r", encoding="utf-8") as f:
        html = f.read()
    pattern = r"const SKI_INTERNATIONAL_DATA = \[.*?\n\];"
    new_html, count = _re.subn(pattern, js_string, html, count=1, flags=_re.DOTALL)
    if count == 0:
        print("INFO: SKI_INTERNATIONAL_DATA block not yet in HTML — skipping injection (will be added during UI restructure).")
        return
    if test_mode:
        print(f"  [test mode] Would have updated SKI_INTERNATIONAL_DATA in {HTML_FILE}")
        return
    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write(new_html)
    print(f"  Updated {HTML_FILE}")


def main():
    parser = argparse.ArgumentParser(description="When To Book — Club Med international ski price checker")
    parser.add_argument("--test",        action="store_true", help="Fetch prices but don't write any files")
    parser.add_argument("--verify",      action="store_true", help="Test one API call and exit")
    parser.add_argument("--inject-only", action="store_true", help="Rebuild SKI_INTERNATIONAL_DATA in clubmed/index.html from CSV, no API calls")
    args = parser.parse_args()

    now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    print(f"\n{'='*60}")
    print(f"Booking Window international ski price checker — {now_str}")
    if args.test:
        print("  MODE: test (no files will be written)")
    if args.inject_only:
        print("  MODE: inject-only (no API calls; rebuilding SKI_INTERNATIONAL_DATA from CSV)")
    print(f"{'='*60}\n")

    if args.inject_only:
        print("Building SKI_INTERNATIONAL_DATA from CSV...")
        js_string = build_resort_data_js()
        inject_into_html(js_string)
        print("Done.")
        return

    if args.verify:
        print("Verifying API with Pragelato Sestriere (PRAC_WINTER) 2A, 7 Dec 2026...")

        async def _verify():
            sem = asyncio.Semaphore(1)
            async with aiohttp.ClientSession() as session:
                return await fetch_price_async(
                    session, sem, "PRAC_WINTER", 2, 0, [], "2026-12-06", "2026-12-13"
                )

        price, status = asyncio.run(_verify())
        if price:
            print(f"  SUCCESS — price returned: £{price:,}")
        else:
            print(f"  No price returned (status: {status}) — API is "
                  f"{'reachable' if status != 'error' else 'unreachable'}")
        return

    asyncio.run(main_async(args))


if __name__ == "__main__":
    main()
