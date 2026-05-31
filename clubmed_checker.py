#!/usr/bin/env python3
"""
clubmed_checker.py — When To Book price checker (async)

Uses aiohttp + asyncio for concurrent API calls (semaphore-controlled, max 8 simultaneous).
After each resort completes, rows are appended to CSV and a git commit+push is made,
so the site updates incrementally throughout the run.

Usage:
    python clubmed_checker.py           # Normal run (~20 min, all resorts async)
    python clubmed_checker.py --test    # Fetch prices, print results, no file writes
    python clubmed_checker.py --verify  # Test one API call and exit
    python clubmed_checker.py --inject-only  # Rebuild RESORT_DATA from CSV, no API calls
"""

import asyncio
import aiohttp
import json
import csv
import os
import re
import sys
import time
import random
import smtplib
import argparse
import subprocess
from datetime import datetime, date, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path

# ─────────────────────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────────────────────

HTML_FILE = "clubmed/index.html"
CSV_FILE  = "_data/prices_clubmed.csv"

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

# Season: Dec 2026 – Apr 2027 ski season
SKI_MONTHS = [(2026, 12)] + [(2027, m) for m in range(1, 5)]

def make_windows(departure_day, durations=(6, 7)):
    """
    Generate departure windows for the full ski season across all durations.
    departure_day: int 0-6 (Mon-Sun) for a verified resort, or None to query
                   both Saturday (5) and Sunday (6) until the day is confirmed.
    """
    weekdays = [departure_day] if departure_day is not None else [5, 6]
    windows = []
    for duration_nights in durations:
        for yr, mo in SKI_MONTHS:
            for wd in weekdays:
                for s in weekday_dates_in_month(yr, mo, wd):
                    windows.append({
                        "startDate": s,
                        "endDate": (datetime.strptime(s, "%Y-%m-%d") + timedelta(days=duration_nights)).strftime("%Y-%m-%d"),
                        "duration": duration_nights,
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

# departure_day: 0=Mon … 6=Sun; None = unverified (queries both Sat=5 and Sun=6)
RESORTS = [
    {
        "id":             "tignes-val-claret",
        "name":           "Tignes",
        "resortCode":     "TIGC_WINTER",    # verified 21 Apr 2026
        "bookingUrl":     "https://www.clubmed.co.uk/r/tignes/w",
        "departure_day":  6,                # Sunday — confirmed 26 Apr 2026 via API probe (Sun hits all months, Sat only Easter)
        "combos":         _COMBOS,
    },
    {
        "id":             "les-arcs",
        "name":           "Les Arcs Panorama",
        "resortCode":     "ARPC_WINTER",    # verified 21 Apr 2026
        "bookingUrl":     "https://www.clubmed.co.uk/r/les-arcs/w",
        "departure_day":  6,                # Sunday — confirmed 26 Apr 2026 via API probe
        "combos":         _COMBOS,
    },
    {
        "id":             "peisey-vallandry",
        "name":           "Peisey-Vallandry",
        "resortCode":     "PVAC_WINTER",    # verified 21 Apr 2026
        "bookingUrl":     "https://www.clubmed.co.uk/r/peisey-vallandry/w",
        "departure_day":  6,                # Sunday — confirmed 26 Apr 2026 via API probe
        "combos":         _COMBOS,
    },
    {
        "id":             "valmorel",
        "name":           "Valmorel",
        "resortCode":     "VMOC_WINTER",    # verified 21 Apr 2026
        "bookingUrl":     "https://www.clubmed.co.uk/r/valmorel/w",
        "departure_day":  6,                # Sunday — confirmed 26 Apr 2026 via API probe (Sat prices anomalously ~2x higher, likely wrong product)
        "combos":         _COMBOS,
    },
    {
        "id":             "alpe-dhuez",
        "name":           "Alpe d'Huez",
        "resortCode":     "ALHC_WINTER",    # verified 21 Apr 2026
        "bookingUrl":     "https://www.clubmed.co.uk/r/alpe-dhuez/w",
        "departure_day":  6,                # Sunday — confirmed 26 Apr 2026 via API probe
        "combos":         _COMBOS,
    },
    {
        "id":             "la-rosiere",
        "name":           "La Rosière",
        "resortCode":     "LROC_WINTER",    # verified 21 Apr 2026
        "bookingUrl":     "https://www.clubmed.co.uk/r/la-rosiere/w",
        "departure_day":  6,                # Sunday — confirmed 26 Apr 2026 via API probe
        "combos":         _COMBOS,
    },
    {
        "id":             "la-plagne-2100",
        "name":           "La Plagne 2100",
        "resortCode":     "PLAC",           # year-round resort (no _WINTER suffix) — confirmed 20 May 2026; LP2C_WINTER silently resolves to ARPC_WINTER (Les Arcs fallback) and is wrong
        "bookingUrl":     "https://www.clubmed.co.uk/r/la-plagne-2100/y",
        "departure_day":  6,                # Sunday only — confirmed 20 May 2026 via API probe (all other days return not_for_sale)
        "durations":      (7,),             # 7-night only; 6-night returns not_for_sale for this product
        "combos":         _COMBOS,
    },
    {
        "id":             "val-disere",
        "name":           "Val d'Isère",
        "resortCode":     "VDIC_WINTER",    # confirmed 26 Apr 2026 via API probe (Sun returns prices, Sat closed/not-for-sale)
        "bookingUrl":     "https://www.clubmed.co.uk/r/val-disere/w",
        "departure_day":  6,                # Sunday — confirmed 26 Apr 2026 via API probe
        "combos":         _COMBOS,
    },
    {
        "id":             "grand-massif",
        "name":           "Grand Massif Samoëns Morillon",
        "resortCode":     "GMAC_WINTER",    # confirmed 27 Apr 2026 via GraphQL products query; Sat+Sun both return prices
        "bookingUrl":     "https://www.clubmed.co.uk/r/grand-massif/w",
        "departure_day":  None,             # both Sat and Sun return prices — confirm departure day via accumulation
        "combos":         _COMBOS,
    },
    {
        "id":             "val-thorens",
        "name":           "Val Thorens Sensations",
        "resortCode":     "VTHC",           # confirmed 27 Apr 2026 — year-round resort, no _WINTER suffix; Sunday only
        "bookingUrl":     "https://www.clubmed.co.uk/r/val-thorens-sensations/w",
        "departure_day":  6,                # Sunday — Sat returns "not for sale", Sun returns £5,468 for Jan 2027
        "combos":         _COMBOS,
    },
    {
        "id":             "serre-chevalier",
        "name":           "Serre-Chevalier",
        "resortCode":     "SECC_WINTER",    # confirmed 27 Apr 2026 via GraphQL products query; Sat+Sun both return prices
        "bookingUrl":     "https://www.clubmed.co.uk/r/serre-chevalier/w",
        "departure_day":  None,             # both Sat and Sun return prices — confirm departure day via accumulation
        "combos":         _COMBOS,
    },
]

# Pre-compute windows per resort based on departure_day (and optional per-resort durations)
for _r in RESORTS:
    _r["windows"] = make_windows(_r["departure_day"], _r.get("durations", (6, 7)))

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
        "Content-Type":   "application/json",
        "Accept":         "application/graphql-response+json,application/json;q=0.9",
        "Accept-Language":"en-GB",
        "Origin":         "https://www.clubmed.co.uk",
        "Referer":        "https://www.clubmed.co.uk/",
        "User-Agent":     random.choice(_USER_AGENTS),
    }

HEADERS = _get_headers()

QUERY = """mutation SearchPrice($id: ID!, $options: SearchPriceOptions) {
    searchPrice(id: $id, options: $options) {
        productId
        price { bestPrice }
        noPrice { reason }
    }
}"""

NOT_FOR_SALE_REASONS = {"not for sale for the period", "the product is closed during this period"}

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


def fetch_price_sync(resort_code, adults, children, birthdates, start_date, end_date, retries=3):
    """Synchronous fetch — only used for --verify mode."""
    import requests
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
    time.sleep(random.uniform(1, 3))
    for attempt in range(1, retries + 1):
        try:
            r = requests.post(GRAPHQL_URL, json=payload, headers=_get_headers(), timeout=20)
            r.raise_for_status()
            data = r.json()
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
                return None, "no_price"
            return None, "no_price"
        except Exception as e:
            if attempt == retries:
                return None, "error"
            time.sleep(2 ** attempt)
    return None, "error"

# ─────────────────────────────────────────────────────────────
# SIGNAL LOGIC
# ─────────────────────────────────────────────────────────────

def calculate_signal(price_history):
    """Takes a list of {date, price} dicts (oldest first). Returns signal string."""
    if not price_history or len(price_history) < 2:
        return "hold"

    prices = [p["price"] for p in price_history]
    current = prices[-1]

    lookback_14 = prices[-14] if len(prices) >= 14 else prices[0]
    move_14 = current - lookback_14

    avg = sum(prices) / len(prices)

    if move_14 <= -50 and current < avg:
        return "favourable"
    elif move_14 >= 50:
        return "watch"
    elif current < avg and len(prices) >= 7:
        return "watch"
    else:
        return "hold"

def calculate_availability(price, price_history):
    if not price_history or len(price_history) < 7:
        return "good", "stable"
    prices = [p["price"] for p in price_history]
    recent_avg = sum(prices[-7:]) / 7
    older_avg  = sum(prices[:-7]) / max(len(prices) - 7, 1)
    if recent_avg > older_avg * 1.03:
        return "limited", "tightening"
    elif recent_avg < older_avg * 0.97:
        return "good", "easing"
    else:
        return "moderate", "stable"

# ─────────────────────────────────────────────────────────────
# CSV LOGGING
# ─────────────────────────────────────────────────────────────

CSV_HEADERS = [
    "timestamp", "resort_id", "resort_code", "party_size",
    "start_date", "end_date", "duration_nights", "price", "signal",
    "days_before_departure", "day_of_week_sampled",
    "price_first_seen", "price_min_seen", "price_max_seen", "is_cheapest_ever",
]

def log_to_csv(rows, test_mode=False):
    if test_mode:
        print(f"  [test mode] Would have written {len(rows)} rows to {CSV_FILE}")
        return
    file_exists = Path(CSV_FILE).exists()
    with open(CSV_FILE, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
        if not file_exists:
            writer.writeheader()
        writer.writerows(rows)

def load_price_history_from_csv(resort_id, party_size, start_date, duration_nights=7, resort_code=None):
    """Load all historical price points for a given resort/party/date/duration combo from CSV.

    resort_code: if supplied, only rows with that exact resort_code are included. This prevents
    stale rows from a wrong resort code (e.g. LP2C_WINTER data) from contaminating histories
    after a code correction.
    """
    if not Path(CSV_FILE).exists():
        return []
    history = []
    with open(CSV_FILE, newline="") as f:
        for row in csv.DictReader(f):
            row_dur = int(row["duration_nights"]) if row.get("duration_nights") else 7
            if (row["resort_id"] == resort_id and
                (resort_code is None or row.get("resort_code") == resort_code) and
                row["party_size"] == party_size and
                row["start_date"] == start_date and
                row_dur == duration_nights and
                row["price"]):
                history.append({
                    "date":  row["timestamp"][:10],
                    "price": int(row["price"])
                })
    seen = {}
    for entry in history:
        seen[entry["date"]] = entry["price"]
    return [{"date": d, "price": p} for d, p in sorted(seen.items())]

def load_all_price_stats():
    """
    Read prices_clubmed.csv once and return per-combo stats for enriching new rows.
    Key includes resort_code to prevent contamination from corrected codes (e.g. LP2C_WINTER→PLAC).
    Returns: {(resort_id, resort_code, party_size, start_date, duration_nights): {min, max, first, count}}
    """
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
            key = (row["resort_id"], row.get("resort_code", ""), row["party_size"], row["start_date"], dur)
            if key not in stats:
                stats[key] = {"min": price, "max": price, "first": price, "count": 1}
            else:
                s = stats[key]
                s["min"] = min(s["min"], price)
                s["max"] = max(s["max"], price)
                s["count"] += 1
    return stats

def load_price_history_for_resort(resort_id, resort_code):
    """Load all price history for a resort in one CSV pass (keyed by party/date/dur)."""
    if not Path(CSV_FILE).exists():
        return {}
    raw = {}
    with open(CSV_FILE, newline="") as f:
        for row in csv.DictReader(f):
            if row.get("resort_id") != resort_id:
                continue
            if row.get("resort_code") and row["resort_code"] != resort_code:
                continue
            if not row.get("price"):
                continue
            try:
                price = int(row["price"])
            except (ValueError, TypeError):
                continue
            dur = int(row["duration_nights"]) if row.get("duration_nights") else 7
            key = (row["party_size"], row["start_date"], dur)
            if key not in raw:
                raw[key] = {}
            raw[key][row["timestamp"][:10]] = price
    return {
        k: [{"date": d, "price": p} for d, p in sorted(v.items())]
        for k, v in raw.items()
    }

# ─────────────────────────────────────────────────────────────
# HTML INJECTION
# ─────────────────────────────────────────────────────────────

def build_resort_data_js(all_results):
    """
    all_results: dict keyed by (resort_id, party_size, start_date, duration_nights) -> price
    Returns a JS string for the full RESORT_DATA array.
    """
    now_iso = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    lines = ["const RESORT_DATA = ["]

    for resort in RESORTS:
        rid   = resort["id"]
        rname = resort["name"]
        rcode = resort["resortCode"]

        meta = RESORT_META.get(rid, {"region": "French Alps", "altitude": "—"})

        lines.append("  {")
        booking_url = resort.get("bookingUrl", "https://www.clubmed.co.uk/r/ski/w")
        lines.append(f'    id: "{rid}",')
        lines.append(f'    name: "{rname}",')
        lines.append(f'    region: "{meta["region"]}",')
        lines.append(f'    altitude: "{meta["altitude"]}",')
        lines.append(f'    resortCode: "{rcode}",')
        lines.append(f'    bookingUrl: "{booking_url}",')
        lines.append("    combinations: [")

        for combo in resort["combos"]:
            ps        = combo["partySize"]
            adults    = combo["adults"]
            children  = combo["children"]
            bds_json  = json.dumps(combo["birthdates"])

            lines.append("      {")
            lines.append(f'        partySize: "{ps}", adults: {adults}, children: {children}, birthdates: {bds_json},')
            lines.append("        departures: [")

            for window in resort["windows"]:
                sd = window["startDate"]
                ed = window["endDate"]
                dur = window["duration"]
                key = (rid, ps, sd, dur)
                price = all_results.get(key)
                if price is None:
                    continue

                history = load_price_history_from_csv(rid, ps, sd, dur, resort_code=rcode)
                if not history:
                    history = [{"date": sd, "price": price}]

                today_str = date.today().isoformat()
                if not any(h["date"] == today_str for h in history):
                    history.append({"date": today_str, "price": price})
                history.sort(key=lambda x: x["date"])

                history_30 = history[-30:]

                current_price  = history_30[-1]["price"]
                previous_price = history_30[-14]["price"] if len(history_30) >= 14 else history_30[0]["price"]

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
    if not Path(HTML_FILE).exists():
        print(f"WARNING: {HTML_FILE} not found — skipping HTML injection.")
        return
    with open(HTML_FILE, "r", encoding="utf-8") as f:
        html = f.read()
    pattern = r"const RESORT_DATA = \[.*?\n\];"
    new_html, count = re.subn(pattern, js_string, html, count=1, flags=re.DOTALL)
    if count == 0:
        print("WARNING: Could not find RESORT_DATA in HTML — no injection performed.")
        return
    if test_mode:
        print(f"  [test mode] Would have updated RESORT_DATA in {HTML_FILE}")
        return
    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write(new_html)
    print(f"  Updated {HTML_FILE}")

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

def git_commit_resort(resort_code, run_date, retries=3):
    date_str   = run_date.isoformat()
    commit_msg = f"data: {resort_code} prices {date_str}"

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
# RESORT METADATA
# ─────────────────────────────────────────────────────────────

RESORT_META = {
    "tignes-val-claret":  {"region": "French Alps",                     "altitude": "2100m"},
    "les-arcs":           {"region": "French Alps",                     "altitude": "1950m"},
    "peisey-vallandry":   {"region": "Paradiski, French Alps",          "altitude": "1600m"},
    "valmorel":           {"region": "French Alps",                     "altitude": "1460m"},
    "alpe-dhuez":         {"region": "French Alps",                     "altitude": "1860m"},
    "la-rosiere":         {"region": "French Alps",                     "altitude": "1850m"},
    "la-plagne-2100":     {"region": "Paradiski, French Alps",          "altitude": "2100m"},
    "val-disere":         {"region": "French Alps, Espace Killy",       "altitude": "1850m"},
    "grand-massif":       {"region": "French Alps, Grand Massif",       "altitude": "720m"},
    "val-thorens":        {"region": "French Alps, Three Valleys",      "altitude": "2300m"},
    "serre-chevalier":    {"region": "French Alps",                     "altitude": "1400m"},
}

# Resort code reference:
# TIGC_WINTER — Tignes (verified 21 Apr 2026)
# ARPC_WINTER — Les Arcs Panorama (verified 21 Apr 2026)
# PVAC_WINTER — Peisey-Vallandry (verified 21 Apr 2026)
# VMOC_WINTER — Valmorel (verified 21 Apr 2026)
# ALHC_WINTER — Alpe d'Huez (verified 21 Apr 2026)
# LROC_WINTER — La Rosière (verified 21 Apr 2026)
# (LROV_WINTER = La Rosière Espace Exclusive Collection — premium, separate product)
# PLAC        — La Plagne 2100 (confirmed 20 May 2026; year-round, no _WINTER; LP2C_WINTER was wrong — silently resolved to ARPC_WINTER)
# VDIC_WINTER — Val d'Isère (confirmed 26 Apr 2026)
# GMAC_WINTER — Grand Massif Samoëns Morillon (confirmed 27 Apr 2026)
# VTHC       — Val Thorens Sensations (confirmed 27 Apr 2026; year-round resort, no _WINTER suffix)
# SECC_WINTER — Serre-Chevalier (confirmed 27 Apr 2026)

# ─────────────────────────────────────────────────────────────
# ASYNC RESORT PROCESSING
# ─────────────────────────────────────────────────────────────

async def process_resort(session, semaphore, resort, historical_stats, timestamp, run_date,
                          test_mode=False):
    """Fire all API queries for one resort concurrently, then commit results to CSV."""
    rid   = resort["id"]
    rcode = resort["resortCode"]
    rname = resort["name"]
    total_queries = len(resort["combos"]) * len(resort["windows"])

    print(f"\n[{rname} / {rcode}] Starting {total_queries} queries (semaphore=8)...")

    task_meta = []
    tasks = []
    for combo in resort["combos"]:
        for window in resort["windows"]:
            task_meta.append((combo, window))
            tasks.append(fetch_price_async(
                session, semaphore, rcode,
                combo["adults"], combo["children"], combo["birthdates"],
                window["startDate"], window["endDate"],
            ))

    api_results = await asyncio.gather(*tasks)

    resort_history = load_price_history_for_resort(rid, rcode)

    csv_rows       = []
    prices_ok      = 0
    error_count    = 0
    no_price_count = 0

    for (combo, window), (price, fetch_status) in zip(task_meta, api_results):
        sd         = window["startDate"]
        ed         = window["endDate"]
        ps         = combo["partySize"]
        duration_n = window["duration"]

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

        key  = (rid, rcode, ps, sd, duration_n)
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
            "timestamp":             timestamp,
            "resort_id":             rid,
            "resort_code":           rcode,
            "party_size":            ps,
            "start_date":            sd,
            "end_date":              ed,
            "duration_nights":       duration_n,
            "price":                 price if price else "",
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

    return error_count, no_price_count, total, {
        (combo["partySize"], window["startDate"], window["duration"]): price
        for (combo, window), (price, _) in zip(task_meta, api_results)
        if price is not None
    }

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

    # all_results collects prices for HTML injection
    all_results = {}

    semaphore = asyncio.Semaphore(8)
    connector = aiohttp.TCPConnector(limit=20, ttl_dns_cache=300)

    async with aiohttp.ClientSession(connector=connector) as session:
        for resort in resorts_this_run:
            errors, no_price, row_count, resort_prices = await process_resort(
                session, semaphore, resort, historical_stats, timestamp, run_date, args.test
            )
            total_errors   += errors
            total_no_price += no_price
            total_rows     += row_count

            rid = resort["id"]
            for (ps, sd, dur), price in resort_prices.items():
                all_results[(rid, ps, sd, dur)] = price

    print(f"\nAll resorts complete.")

    prices_fetched = total_rows - total_no_price
    if total_errors > 0 and total_rows > 0 and total_errors / total_rows > 0.3:
        send_alert(
            "When To Book health alert — winter checker API errors",
            f"{total_errors}/{total_rows} fetches failed with network/API errors. "
            f"Check the GitHub Actions logs.\n\nRun timestamp: {timestamp}"
        )

    print(f"\nDone. {prices_fetched}/{total_rows} prices fetched successfully.")
    if total_no_price:
        print(f"  {total_no_price} no-price responses "
              f"({total_errors} errors, rest are pre-season/closed).")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--test",        action="store_true", help="Fetch prices but don't write any files")
    parser.add_argument("--verify",      action="store_true", help="Test one API call and exit")
    parser.add_argument("--inject-only", action="store_true", help="Skip API fetch; rebuild RESORT_DATA from CSV and inject into HTML")
    args = parser.parse_args()

    now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    print(f"\n{'='*60}")
    print(f"Booking Window price checker — {now_str}")
    if args.test:
        print("  MODE: test (no files will be written)")
    if args.inject_only:
        print("  MODE: inject-only (no API calls; rebuilding RESORT_DATA from CSV)")
    print(f"{'='*60}\n")

    if args.verify:
        print("Verifying API with Tignes (TIGC_WINTER) 2A, 17 Apr 2027...")
        price, status = fetch_price_sync("TIGC_WINTER", 2, 0, [], "2027-04-17", "2027-04-24")
        if price:
            print(f"  SUCCESS — price returned: £{price:,}")
        else:
            print(f"  No price returned (status: {status}) — API is {'reachable' if status != 'error' else 'unreachable'}")
        return

    if args.inject_only:
        print("Building all_results from CSV (latest price per combo)...")
        all_results = {}
        if Path(CSV_FILE).exists():
            with open(CSV_FILE, newline="") as f:
                for row in csv.DictReader(f):
                    if not row.get("price"):
                        continue
                    try:
                        price_val = int(row["price"])
                    except (ValueError, TypeError):
                        continue
                    # Skip contaminated LP2C_WINTER rows — only use rows matching each resort's current code
                    resort_obj = next((r for r in RESORTS if r["id"] == row["resort_id"]), None)
                    if resort_obj and row.get("resort_code") and row["resort_code"] != resort_obj["resortCode"]:
                        continue
                    dur = int(row["duration_nights"]) if row.get("duration_nights") else 7
                    key = (row["resort_id"], row["party_size"], row["start_date"], dur)
                    all_results[key] = price_val
        print(f"  Loaded {len(all_results)} price entries from CSV.")
        print("Building updated RESORT_DATA...")
        js_string = build_resort_data_js(all_results)
        inject_into_html(js_string)
        print("Done.")
        return

    asyncio.run(main_async(args))


if __name__ == "__main__":
    main()
