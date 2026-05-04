#!/usr/bin/env python3
"""
markwarner_checker.py — When To Book: Mark Warner price checker
Fetches per-week departure prices for Chalet Hotel L'Écrin, Tignes via the
Mark Warner search API. One API call per party size returns all available
departure dates for the season. Appends to _data/markwarner_prices.csv.

API: POST https://www.markwarner.co.uk/resort/getresortsearchcriteria
Response: validDates[] — per-week departure dates with pr/prpp (promo) and
          wp/wppp (was-price, pre-promotion reference price).

Usage:
    python markwarner_checker.py           # Normal run
    python markwarner_checker.py --test    # Fetch and print, no file writes
    python markwarner_checker.py --verify  # One API call to confirm connectivity
"""

import csv
import os
import re
import sys
import time
import random
import argparse
from datetime import datetime, timezone

import requests

# ─────────────────────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────────────────────

RESORT_NAME = "Chalet Hotel L'Écrin"
RESORT_LOCATION = "Tignes, France"
RESORT_ID = 957           # numeric ID found in page HTML
AIRPORT = "LGW"           # London Gatwick — only airport for this resort

API_URL = "https://www.markwarner.co.uk/resort/getresortsearchcriteria"

CSV_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_data", "markwarner_prices.csv")

CSV_FIELDNAMES = [
    "timestamp",
    "resort",
    "location",
    "departure_date",
    "duration_nights",
    "party_size",
    "adults",
    "children",
    "room_type",
    "price_total",        # pr — discounted total price (includes any active promo)
    "price_pp",           # prpp — discounted price per person
    "was_price_total",    # wp — pre-promo reference price
    "was_price_pp",       # wppp — pre-promo price per person
    "promo_code",         # pc — active promo code (e.g. FIRSTTRACKS)
    "currency",
]

# Party sizes to track — 2 adults is the primary signal
PARTY_SIZES = [
    {"label": "2A",   "adults": 2, "children": 0, "child_ages": []},
    {"label": "2A1C", "adults": 2, "children": 1, "child_ages": [7]},
    {"label": "2A2C", "adults": 2, "children": 2, "child_ages": [7, 10]},
]

DURATION_NIGHTS = 7

USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
]


# ─────────────────────────────────────────────────────────────
# API
# ─────────────────────────────────────────────────────────────

def api_headers():
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-GB,en;q=0.9",
        "Content-Type": "application/json",
        "Referer": "https://www.markwarner.co.uk/ski-holidays/france/chalet-hotel-lecrin",
        "Origin": "https://www.markwarner.co.uk",
        "X-Requested-With": "XMLHttpRequest",
    }


def fetch_prices(party: dict, retries: int = 3) -> list[dict]:
    """
    POST to the search criteria endpoint. Returns all validDates for the season.
    One call per party size — the response contains the full set of departure
    dates and their prices regardless of the checkIn parameter.
    Retries with exponential backoff on network/HTTP failures.
    """
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    payload = {
        "resortId": RESORT_ID,
        "adults": party["adults"],
        "children": party["children"],
        "infants": 0,
        "childAges": party["child_ages"],
        "infantAges": [],
        "airport": AIRPORT,
        "duration": DURATION_NIGHTS,
        "checkIn": today,
        "adultNames": [],
        "childNames": [],
        "infantNames": [],
    }

    # Random pre-request delay to mimic a user navigating to the search page
    time.sleep(random.uniform(3, 8) + random.uniform(0, 2))

    last_error = None
    for attempt in range(1, retries + 1):
        try:
            resp = requests.post(API_URL, headers=api_headers(), json=payload, timeout=20)
            resp.raise_for_status()
            data = resp.json()
            if not data.get("success"):
                print(f"  WARNING: API returned success=false for {party['label']}")
                return []
            return data.get("model", {}).get("validDates", [])
        except requests.exceptions.Timeout:
            last_error = f"Timeout (attempt {attempt}/{retries})"
        except requests.HTTPError as e:
            if e.response.status_code in (403, 429):
                raise  # blocking responses — don't retry, let caller handle
            last_error = f"HTTP {e.response.status_code} (attempt {attempt}/{retries})"
        except requests.RequestException as e:
            last_error = str(e)

        if attempt < retries:
            backoff = 2 ** attempt + random.uniform(0, 3)
            print(f"  Retry {attempt}/{retries} in {backoff:.0f}s — {last_error}")
            time.sleep(backoff)

    raise requests.RequestException(f"All {retries} attempts failed: {last_error}")


# ─────────────────────────────────────────────────────────────
# PARSING
# ─────────────────────────────────────────────────────────────

def parse_dates(valid_dates: list, party: dict, timestamp: str) -> list[dict]:
    rows = []
    for entry in valid_dates:
        dep_date = entry.get("d")
        if not dep_date:
            continue
        rows.append({
            "timestamp":       timestamp,
            "resort":          RESORT_NAME,
            "location":        RESORT_LOCATION,
            "departure_date":  dep_date,
            "duration_nights": DURATION_NIGHTS,
            "party_size":      party["label"],
            "adults":          party["adults"],
            "children":        party["children"],
            "room_type":       entry.get("u", ""),   # e.g. "Double room (ensuite bath)"
            "price_total":     entry.get("pr"),       # discounted total
            "price_pp":        entry.get("prpp"),     # discounted per person
            "was_price_total": entry.get("wp"),       # pre-promo total
            "was_price_pp":    entry.get("wppp"),     # pre-promo per person
            "promo_code":      entry.get("pc", ""),
            "currency":        "GBP",
        })
    return rows


# ─────────────────────────────────────────────────────────────
# CSV
# ─────────────────────────────────────────────────────────────

def append_csv(rows: list[dict]) -> None:
    os.makedirs(os.path.dirname(CSV_FILE), exist_ok=True)
    file_exists = os.path.isfile(CSV_FILE)
    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDNAMES)
        if not file_exists:
            writer.writeheader()
        writer.writerows(rows)


# ─────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Mark Warner price checker")
    parser.add_argument("--test",   action="store_true", help="Fetch and print, no file writes")
    parser.add_argument("--verify", action="store_true", help="One API call to confirm connectivity")
    args = parser.parse_args()

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    print(f"[{timestamp}] Mark Warner checker starting — {RESORT_NAME}, {RESORT_LOCATION}")

    all_rows = []

    # Randomise party-size order each run so request cadence varies day-to-day
    party_sizes_this_run = list(PARTY_SIZES)
    random.shuffle(party_sizes_this_run)

    for party_idx, party in enumerate(party_sizes_this_run):
        if party_idx > 0:
            # Longer pause between party-size groups — simulates navigating between search results
            inter_group_sleep = random.uniform(10, 30)
            print(f"  Pausing {inter_group_sleep:.0f}s before next party size...")
            time.sleep(inter_group_sleep)

        print(f"\nFetching {party['label']} ({party['adults']}A {party['children']}C)...")
        try:
            valid_dates = fetch_prices(party)
        except requests.HTTPError as e:
            print(f"  ERROR: HTTP {e.response.status_code} — {e}")
            if e.response.status_code in (403, 429):
                print("  Mark Warner may be blocking this IP. Stopping.")
                sys.exit(1)
            continue
        except requests.RequestException as e:
            print(f"  ERROR: {e}")
            continue

        if not valid_dates:
            print(f"  No dates returned for {party['label']}")
            continue

        rows = parse_dates(valid_dates, party, timestamp)
        print(f"  {len(rows)} departure dates found")
        for r in rows[:3]:
            print(f"    {r['departure_date']}  £{r['price_total']:,} total  (£{r['price_pp']:,}pp)")
        if len(rows) > 3:
            print(f"    ... and {len(rows)-3} more")

        all_rows.extend(rows)

        if args.verify:
            print("OK — connectivity confirmed")
            return

    if not all_rows:
        print("\nWARNING: No price rows collected.")
        sys.exit(0)

    print(f"\nTotal: {len(all_rows)} rows across {len(PARTY_SIZES)} party sizes")

    if args.test:
        print("[--test] No files written.")
        return

    append_csv(all_rows)
    print(f"Appended {len(all_rows)} rows to {CSV_FILE}")


if __name__ == "__main__":
    main()
