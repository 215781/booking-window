#!/usr/bin/env python3
"""
clubmed_summer_checker.py — Club Med summer resort price checker
Tracks 7 European summer resorts (June–September), accommodation-only, 2 adults, 7 nights.
Appends one row per resort per departure date to _data/prices_clubmed_summer.csv.

Usage:
    python clubmed_summer_checker.py          # Normal run
    python clubmed_summer_checker.py --test   # Fetch prices, no file writes
    python clubmed_summer_checker.py --verify # Test one API call and exit
"""

import asyncio
import aiohttp
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

CSV_FILE = "_data/prices_clubmed_summer.csv"
CSV_HEADERS = ["collected_at", "resort_code", "resort_name", "departure_date", "price_pp", "currency"]

GMAIL_ADDRESS  = os.environ.get("GMAIL_ADDRESS", "")
GMAIL_APP_PASS = os.environ.get("GMAIL_APP_PASS", "")
ALERT_TO       = os.environ.get("ALERT_TO", "")

# ─────────────────────────────────────────────────────────────
# RESORT CONFIG
# All codes verified via Club Med GraphQL API, 2026-05-12.
# departureCity: "NO" = accommodation only (no flights) — intentional.
# Summer resorts depart on Saturdays.
# ─────────────────────────────────────────────────────────────

RESORTS = [
    {
        "id":         "magna-marbella",
        "name":       "Magna Marbella",
        "resortCode": "MMAC",         # verified 2026-05-12 — seasonal (closed Jan)
        "bookingUrl": "https://www.clubmed.co.uk/r/magna-marbella",
    },
    {
        "id":         "cefalu",
        "name":       "Cefalù",
        "resortCode": "CFAC",         # verified 2026-05-12 — seasonal (closed Jan)
        "bookingUrl": "https://www.clubmed.co.uk/r/cefalu",
    },
    {
        "id":         "gregolimano",
        "name":       "Gregolimano",
        "resortCode": "GREC",         # verified 2026-05-12 — seasonal (closed Jan)
        "bookingUrl": "https://www.clubmed.co.uk/r/gregolimano",
    },
    {
        "id":         "palmiye",
        "name":       "Palmiye",
        "resortCode": "PALC",         # verified 2026-05-12 — seasonal (closed Jan)
        "bookingUrl": "https://www.clubmed.co.uk/r/palmiye",
    },
    {
        "id":         "da-balaia",
        "name":       "Da Balaia",
        "resortCode": "DBAC",         # verified 2026-05-12 — seasonal (closed Jan)
        "bookingUrl": "https://www.clubmed.co.uk/r/da-balaia",
    },
    {
        "id":         "la-palmyre",
        "name":       "La Palmyre Atlantique",
        "resortCode": "LPAC",         # verified 2026-05-12 — seasonal (closed Jan)
        "bookingUrl": "https://www.clubmed.co.uk/r/la-palmyre-atlantique",
    },
    {
        "id":         "marrakech-palmeraie",
        "name":       "Marrakech La Palmeraie",
        "resortCode": "MPAC",         # verified 2026-05-12 — year-round (open Jan)
        "bookingUrl": "https://www.clubmed.co.uk/r/marrakech-la-palmeraie",
    },
]

# Summer season: June–September 2026
SUMMER_MONTHS = [(2026, m) for m in range(6, 10)]


def saturdays_in_month(year, month):
    dates = []
    d = date(year, month, 1)
    while d.weekday() != 5:
        d += timedelta(days=1)
    while d.month == month:
        dates.append(d.strftime("%Y-%m-%d"))
        d += timedelta(days=7)
    return dates


def make_summer_windows(duration_nights=7):
    windows = []
    for yr, mo in SUMMER_MONTHS:
        for s in saturdays_in_month(yr, mo):
            end = (datetime.strptime(s, "%Y-%m-%d") + timedelta(days=duration_nights)).strftime("%Y-%m-%d")
            windows.append({"startDate": s, "endDate": end})
    return windows


WINDOWS = make_summer_windows()

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


async def fetch_price_async(session, semaphore, resort_code, start_date, end_date, retries=4):
    """Fetch 2-adult price for one resort / departure date. Returns (price_or_None, status)."""
    payload = {
        "operationName": "SearchPrice",
        "variables": {
            "id": resort_code,
            "options": {
                "adults":               2,
                "children":             0,
                "startDate":            start_date,
                "endDate":              end_date,
                "flexible":             None,
                "birthdates":           [],
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
# CSV LOGGING
# ─────────────────────────────────────────────────────────────


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
    commit_msg = f"data: {resort_code} summer prices {date_str}"

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
        print(f"  [{resort_code}] All push retries exhausted — data saved locally")

# ─────────────────────────────────────────────────────────────
# ASYNC RESORT PROCESSING
# ─────────────────────────────────────────────────────────────


async def process_resort(session, semaphore, resort, timestamp, run_date, test_mode=False):
    rcode = resort["resortCode"]
    rname = resort["name"]
    total_queries = len(WINDOWS)

    print(f"\n[{rname} / {rcode}] Starting {total_queries} queries...")

    tasks = [
        fetch_price_async(session, semaphore, rcode, w["startDate"], w["endDate"])
        for w in WINDOWS
    ]
    api_results = await asyncio.gather(*tasks)

    csv_rows   = []
    prices_ok  = 0
    error_count = 0
    no_price_count = 0

    for window, (price, status) in zip(WINDOWS, api_results):
        if price is not None:
            prices_ok += 1
            price_pp = price // 2  # 2-adult total → per person
            csv_rows.append({
                "collected_at":   timestamp,
                "resort_code":    rcode,
                "resort_name":    rname,
                "departure_date": window["startDate"],
                "price_pp":       price_pp,
                "currency":       "GBP",
            })
        else:
            no_price_count += 1
            if status == "error":
                error_count += 1

    print(f"  [{rname}] Complete: {prices_ok}/{total_queries} prices OK "
          f"({no_price_count} no-price, {error_count} errors)")

    log_to_csv(csv_rows, test_mode)
    if not test_mode and csv_rows:
        git_commit_resort(rcode, run_date)

    return prices_ok, error_count, no_price_count, len(WINDOWS)

# ─────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────


async def main_async(args):
    timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    run_date  = date.today()

    git_setup()

    resorts_this_run = list(RESORTS)
    random.shuffle(resorts_this_run)

    total_ok       = 0
    total_errors   = 0
    total_no_price = 0
    total_rows     = 0

    semaphore = asyncio.Semaphore(8)
    connector = aiohttp.TCPConnector(limit=20, ttl_dns_cache=300)

    async with aiohttp.ClientSession(connector=connector) as session:
        for resort in resorts_this_run:
            ok, errors, no_price, rows = await process_resort(
                session, semaphore, resort, timestamp, run_date, args.test
            )
            total_ok       += ok
            total_errors   += errors
            total_no_price += no_price
            total_rows     += rows

    print(f"\nAll resorts complete.")
    print(f"Done. {total_ok}/{total_rows} prices fetched successfully.")
    if total_no_price:
        print(f"  {total_no_price} no-price responses "
              f"({total_errors} errors, rest are pre-season/closed).")

    if total_errors > 0 and total_rows > 0 and total_errors / total_rows > 0.3:
        send_alert(
            "When To Book summer checker — API errors detected",
            f"{total_errors}/{total_rows} fetches failed. "
            f"Check GitHub Actions logs.\n\nTimestamp: {timestamp}"
        )


def main():
    parser = argparse.ArgumentParser(description="When To Book — Club Med summer price checker")
    parser.add_argument("--test",   action="store_true", help="Fetch prices but don't write any files")
    parser.add_argument("--verify", action="store_true", help="Test one API call and exit")
    args = parser.parse_args()

    now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    print(f"\n{'='*60}")
    print(f"Club Med summer price checker — {now_str}")
    if args.test:
        print("  MODE: test (no files will be written)")
    print(f"  Tracking {len(RESORTS)} resorts × {len(WINDOWS)} departure dates")
    print(f"{'='*60}\n")

    if args.verify:
        print("Verifying API with Magna Marbella (MMAC), 2026-07-04...")

        async def _verify():
            sem = asyncio.Semaphore(1)
            async with aiohttp.ClientSession() as session:
                return await fetch_price_async(
                    session, sem, "MMAC", "2026-07-04", "2026-07-11"
                )

        price, status = asyncio.run(_verify())
        if price:
            print(f"  SUCCESS — total price returned: £{price:,} (£{price//2:,} pp)")
        else:
            print(f"  No price returned (status: {status}) — API is "
                  f"{'reachable' if status != 'error' else 'unreachable'}")
        return

    asyncio.run(main_async(args))


if __name__ == "__main__":
    main()
