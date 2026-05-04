#!/usr/bin/env python3
"""
clubmed_checker.py — When To Book price checker
Runs 6x daily via GitHub Actions. Fetches live prices from the Club Med
GraphQL API and writes them directly into clubmed/index.html + price_history.csv

Usage:
    python clubmed_checker.py           # Normal run
    python clubmed_checker.py --test    # Fetch prices, print results, no file writes
    python clubmed_checker.py --verify  # Test one resort code and exit
"""

import requests
import json
import csv
import os
import re
import sys
import time
import random
import smtplib
import argparse
from datetime import datetime, date, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path

# ─────────────────────────────────────────────────────────────
# CONFIGURATION — edit these before first run
# ─────────────────────────────────────────────────────────────

# File paths (relative to this script — keep everything in the same repo folder)
HTML_FILE = "clubmed/index.html"
CSV_FILE  = "_data/price_history.csv"

# Email alerts (set these as GitHub Actions secrets, or hardcode for local testing)
GMAIL_ADDRESS  = os.environ.get("GMAIL_ADDRESS", "")   # your gmail address
GMAIL_APP_PASS = os.environ.get("GMAIL_APP_PASS", "")  # 16-char app password
ALERT_TO       = os.environ.get("ALERT_TO", "")        # where to send alerts

# Price drop threshold to trigger an alert email (£)
ALERT_THRESHOLD = 50

# How many consecutive no-price responses before sending a health-check alert
HEALTH_CHECK_LIMIT = 3

# ─────────────────────────────────────────────────────────────
# RESORT CONFIG
# Each entry defines one resort and all the party/date combos to track.
# Add Saturday departure dates for the full season you want to cover.
# departureCity: "NO" = accommodation only (no flights) — intentional.
# ─────────────────────────────────────────────────────────────

# Helper: generate all dates matching a given weekday (0=Mon … 6=Sun) in a month
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
    {"partySize": "2A",   "adults": 2, "children": 0, "birthdates": []},
    {"partySize": "2A1C", "adults": 2, "children": 1, "birthdates": ["2021-04-28"]},
    {"partySize": "2A2C", "adults": 2, "children": 2, "birthdates": ["2021-04-28", "2019-06-15"]},
]

# departure_day: 0=Mon … 6=Sun; None = unverified (queries both Sat=5 and Sun=6)
RESORTS = [
    {
        "id":             "tignes-val-claret",
        "name":           "Tignes",
        "resortCode":     "TIGC_WINTER",    # verified 21 Apr 2026
        "departure_day":  6,                # Sunday — confirmed 26 Apr 2026 via API probe (Sun hits all months, Sat only Easter)
        "combos":         _COMBOS,
    },
    {
        "id":             "les-arcs",
        "name":           "Les Arcs Panorama",
        "resortCode":     "ARPC_WINTER",    # verified 21 Apr 2026
        "departure_day":  6,                # Sunday — confirmed 26 Apr 2026 via API probe
        "combos":         _COMBOS,
    },
    {
        "id":             "peisey-vallandry",
        "name":           "Peisey-Vallandry",
        "resortCode":     "PVAC_WINTER",    # verified 21 Apr 2026
        "departure_day":  6,                # Sunday — confirmed 26 Apr 2026 via API probe
        "combos":         _COMBOS,
    },
    {
        "id":             "valmorel",
        "name":           "Valmorel",
        "resortCode":     "VMOC_WINTER",    # verified 21 Apr 2026
        "departure_day":  6,                # Sunday — confirmed 26 Apr 2026 via API probe (Sat prices anomalously ~2x higher, likely wrong product)
        "combos":         _COMBOS,
    },
    {
        "id":             "alpe-dhuez",
        "name":           "Alpe d'Huez",
        "resortCode":     "ALHC_WINTER",    # verified 21 Apr 2026
        "departure_day":  6,                # Sunday — confirmed 26 Apr 2026 via API probe
        "combos":         _COMBOS,
    },
    {
        "id":             "la-rosiere",
        "name":           "La Rosière",
        "resortCode":     "LROC_WINTER",    # verified 21 Apr 2026
        "departure_day":  6,                # Sunday — confirmed 26 Apr 2026 via API probe
        "combos":         _COMBOS,
    },
    {
        "id":             "la-plagne-2100",
        "name":           "La Plagne 2100",
        "resortCode":     "LP2C_WINTER",    # verified 26 Apr 2026
        "departure_day":  6,                # Sunday — confirmed 26 Apr 2026
        "combos":         _COMBOS,
    },
    {
        "id":             "val-disere",
        "name":           "Val d'Isère",
        "resortCode":     "VDIC_WINTER",    # confirmed 26 Apr 2026 via API probe (Sun returns prices, Sat closed/not-for-sale)
        "departure_day":  6,                # Sunday — confirmed 26 Apr 2026 via API probe
        "combos":         _COMBOS,
    },
    {
        "id":             "grand-massif",
        "name":           "Grand Massif Samoëns Morillon",
        "resortCode":     "GMAC_WINTER",    # confirmed 27 Apr 2026 via GraphQL products query; Sat+Sun both return prices
        "departure_day":  None,             # both Sat and Sun return prices — confirm departure day via accumulation
        "combos":         _COMBOS,
    },
    {
        "id":             "val-thorens",
        "name":           "Val Thorens Sensations",
        "resortCode":     "VTHC",           # confirmed 27 Apr 2026 — year-round resort, no _WINTER suffix; Sunday only
        "departure_day":  6,                # Sunday — Sat returns "not for sale", Sun returns £5,468 for Jan 2027
        "combos":         _COMBOS,
    },
    {
        "id":             "serre-chevalier",
        "name":           "Serre-Chevalier",
        "resortCode":     "SECC_WINTER",    # confirmed 27 Apr 2026 via GraphQL products query; Sat+Sun both return prices
        "departure_day":  None,             # both Sat and Sun return prices — confirm departure day via accumulation
        "combos":         _COMBOS,
    },
]

# Pre-compute windows per resort based on departure_day
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

# Keep a module-level HEADERS alias for any code that references it directly
HEADERS = _get_headers()

QUERY = """mutation SearchPrice($id: ID!, $options: SearchPriceOptions) {
    searchPrice(id: $id, options: $options) {
        productId
        price { bestPrice }
        noPrice { reason }
    }
}"""

NOT_FOR_SALE_REASONS = {"not for sale for the period", "the product is closed during this period"}

def fetch_price(resort_code, adults, children, birthdates, start_date, end_date, retries=3):
    """Fetch a single price from the Club Med GraphQL API.

    Returns (price_or_None, status) where status is one of:
      "ok"           — price returned successfully
      "not_for_sale" — API says period not on sale yet (expected pre-season)
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
    # Random delay between requests to avoid burst traffic pattern
    time.sleep(random.uniform(2, 8))

    last_error = None
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
                reason = no_price.get("reason", "unknown")
                reason_lower = reason.lower()
                if "not for sale" in reason_lower:
                    return None, "not_for_sale"
                elif "closed" in reason_lower:
                    return None, "closed"
                else:
                    print(f"  No price — reason: {reason}")
                    return None, "no_price"
            return None, "no_price"
        except requests.exceptions.Timeout:
            last_error = f"Timeout (attempt {attempt}/{retries})"
        except Exception as e:
            last_error = str(e)
        if attempt < retries:
            time.sleep(2 ** attempt)
    print(f"  Error fetching {resort_code} {start_date}: {last_error}")
    return None, "error"

# ─────────────────────────────────────────────────────────────
# SIGNAL LOGIC
# Determines Book Now / Watch / Hold based on price history.
# Rules (adjust these as you accumulate more data):
#   Book Now  — price has dropped £50+ in last 14 days AND is below 30-day average
#   Watch     — price has risen £50+ in last 14 days, OR price is below 30-day avg but no clear drop
#   Hold      — everything else (stable, insufficient data)
# ─────────────────────────────────────────────────────────────

def calculate_signal(price_history):
    """Takes a list of {date, price} dicts (oldest first). Returns signal string."""
    if not price_history or len(price_history) < 2:
        return "hold"

    prices = [p["price"] for p in price_history]
    current = prices[-1]

    # 14-day movement
    lookback_14 = prices[-14] if len(prices) >= 14 else prices[0]
    move_14 = current - lookback_14  # negative = dropped, positive = risen

    # 30-day average (or whatever we have)
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
    """
    Placeholder availability logic — replace with real availability data
    when we find it in the API response. For now, inferred from price movement.
    """
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
# Every single check is written here — this is the historical record.
# ─────────────────────────────────────────────────────────────

CSV_HEADERS = [
    "timestamp", "resort_id", "resort_code", "party_size",
    "start_date", "end_date", "duration_nights", "price", "signal",
    "days_before_departure", "day_of_week_sampled",
    "price_first_seen", "price_min_seen", "price_max_seen", "is_cheapest_ever",
]

def log_to_csv(rows, test_mode=False):
    """Append a list of result dicts to the CSV log."""
    if test_mode:
        print(f"  [test mode] Would have written {len(rows)} rows to {CSV_FILE}")
        return
    file_exists = Path(CSV_FILE).exists()
    with open(CSV_FILE, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
        if not file_exists:
            writer.writeheader()
        writer.writerows(rows)

def load_price_history_from_csv(resort_id, party_size, start_date, duration_nights=7):
    """Load all historical price points for a given resort/party/date/duration combo from CSV."""
    if not Path(CSV_FILE).exists():
        return []
    history = []
    with open(CSV_FILE, newline="") as f:
        for row in csv.DictReader(f):
            row_dur = int(row["duration_nights"]) if row.get("duration_nights") else 7
            if (row["resort_id"] == resort_id and
                row["party_size"] == party_size and
                row["start_date"] == start_date and
                row_dur == duration_nights and
                row["price"]):
                history.append({
                    "date":  row["timestamp"][:10],
                    "price": int(row["price"])
                })
    # deduplicate by date, keep latest
    seen = {}
    for entry in history:
        seen[entry["date"]] = entry["price"]
    return [{"date": d, "price": p} for d, p in sorted(seen.items())]

def load_all_price_stats():
    """
    Read price_history.csv once and return per-combo stats for enriching new rows.
    Returns: {(resort_id, party_size, start_date, duration_nights): {min, max, first, count}}
    CSV is appended chronologically so the first row encountered per key IS the first-ever price.
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
            key = (row["resort_id"], row["party_size"], row["start_date"], dur)
            if key not in stats:
                stats[key] = {"min": price, "max": price, "first": price, "count": 1}
            else:
                s = stats[key]
                s["min"] = min(s["min"], price)
                s["max"] = max(s["max"], price)
                s["count"] += 1
    return stats

# ─────────────────────────────────────────────────────────────
# HTML INJECTION
# Finds the RESORT_DATA array in BookingWindow.html and replaces it
# with fresh data. Everything else in the HTML is untouched.
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

        # Get region/altitude from a simple lookup (matches the HTML)
        meta = RESORT_META.get(rid, {"region": "French Alps", "altitude": "—"})

        lines.append("  {")
        lines.append(f'    id: "{rid}",')
        lines.append(f'    name: "{rname}",')
        lines.append(f'    region: "{meta["region"]}",')
        lines.append(f'    altitude: "{meta["altitude"]}",')
        lines.append(f'    resortCode: "{rcode}",')
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
                    continue  # skip windows with no price — API returned nothing

                # Load full history from CSV
                history = load_price_history_from_csv(rid, ps, sd, dur)
                if not history:
                    history = [{"date": sd, "price": price}]

                # Ensure today's price is in history
                today_str = date.today().isoformat()
                if not any(h["date"] == today_str for h in history):
                    history.append({"date": today_str, "price": price})
                history.sort(key=lambda x: x["date"])

                # Keep last 30 days max for the chart
                history_30 = history[-30:]

                current_price  = history_30[-1]["price"]
                previous_price = history_30[-14]["price"] if len(history_30) >= 14 else history_30[0]["price"]

                signal = calculate_signal(history_30)
                availability, avail_trend = calculate_availability(current_price, history_30)

                # Display date: "w/c {day} {Mon} {year}"
                dep_dt = datetime.strptime(sd, "%Y-%m-%d") + timedelta(days=1)
                display_date = dep_dt.strftime("w/c %-d %b %Y")

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
    """Replace the RESORT_DATA block in BookingWindow.html."""
    if not Path(HTML_FILE).exists():
        print(f"WARNING: {HTML_FILE} not found — skipping HTML injection.")
        return
    with open(HTML_FILE, "r", encoding="utf-8") as f:
        html = f.read()
    # Match from 'const RESORT_DATA = [' to the closing ']; on its own line.
    # Non-greedy + \n before ]; prevents consuming JS functions that follow.
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
    """Send an alert email via Gmail SMTP."""
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

def check_for_alerts(all_results, previous_signals):
    """Compare new signals against previous run — alert on any new Book Now."""
    for (resort_id, party_size, start_date, duration_n), price in all_results.items():
        if price is None:
            continue
        history = load_price_history_from_csv(resort_id, party_size, start_date, duration_n)
        signal  = calculate_signal(history)
        prev    = previous_signals.get((resort_id, party_size, start_date))
        if signal == "favourable" and prev != "favourable":
            resort_name = next((r["name"] for r in RESORTS if r["id"] == resort_id), resort_id)
            dep_dt      = datetime.strptime(start_date, "%Y-%m-%d") + timedelta(days=1)
            display_date = dep_dt.strftime("%-d %b %Y")
            subject = f"When To Book signal: {resort_name} w/c {display_date} — Favourable"
            body = (
                f"A new Favourable signal has triggered on When To Book.\n\n"
                f"Resort:     {resort_name}\n"
                f"Departure:  w/c {display_date}\n"
                f"Party size: {party_size}\n"
                f"Price:      £{price:,}\n\n"
                f"View: https://whentobook.co.uk\n"
            )
            send_alert(subject, body)

def load_previous_signals():
    """Load the last known signal for each combo from CSV."""
    if not Path(CSV_FILE).exists():
        return {}
    signals = {}
    with open(CSV_FILE, newline="") as f:
        for row in csv.DictReader(f):
            key = (row["resort_id"], row["party_size"], row["start_date"])
            signals[key] = row.get("signal", "hold")
    return signals

# ─────────────────────────────────────────────────────────────
# RESORT METADATA (region, altitude — matches the HTML)
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
# LP2C_WINTER — La Plagne 2100 (verified 26 Apr 2026)
# VDIC_WINTER — Val d'Isère (confirmed 26 Apr 2026)
# GMAC_WINTER — Grand Massif Samoëns Morillon (confirmed 27 Apr 2026)
# VTHC       — Val Thorens Sensations (confirmed 27 Apr 2026; year-round resort, no _WINTER suffix)
# SECC_WINTER — Serre-Chevalier (confirmed 27 Apr 2026)

# ─────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────

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

    # Quick API verify mode
    if args.verify:
        print("Verifying API with Tignes (TIGC_WINTER) 2A, 17 Apr 2027...")
        price, status = fetch_price("TIGC_WINTER", 2, 0, [], "2027-04-17", "2027-04-24")
        if price:
            print(f"  SUCCESS — price returned: £{price:,}")
        else:
            print(f"  No price returned (status: {status}) — API is {'reachable' if status != 'error' else 'unreachable'}")
        return

    # Inject-only mode: rebuild RESORT_DATA from CSV without any API calls
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
                    dur = int(row["duration_nights"]) if row.get("duration_nights") else 7
                    key = (row["resort_id"], row["party_size"], row["start_date"], dur)
                    all_results[key] = price_val  # later rows overwrite earlier (CSV is chronological)
        print(f"  Loaded {len(all_results)} price entries from CSV.")
        print("Building updated RESORT_DATA...")
        js_string = build_resort_data_js(all_results)
        inject_into_html(js_string)
        print("Done.")
        return

    # Load previous signals for alert comparison
    previous_signals = load_previous_signals()

    # Load historical price stats once — used to compute enriched CSV fields
    historical_stats = load_all_price_stats()

    all_results = {}  # (resort_id, party_size, start_date) -> price
    csv_rows    = []
    error_count    = 0  # only real API errors (network/HTTP failures)
    no_price_count = 0  # includes not_for_sale / closed — expected pre-season
    timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    run_date  = date.today()

    # Randomise resort order each run so we don't always query the same resort first
    resorts_this_run = list(RESORTS)
    random.shuffle(resorts_this_run)

    for resort_idx, resort in enumerate(resorts_this_run):
        if resort_idx > 0:
            # Longer pause between resorts to simulate a user navigating between pages
            inter_resort_sleep = random.uniform(15, 30)
            print(f"  Pausing {inter_resort_sleep:.0f}s before next resort...")
            time.sleep(inter_resort_sleep)
        print(f"Fetching: {resort['name']} ({resort['resortCode']})")
        for combo in resort["combos"]:
            for window in resort["windows"]:
                sd = window["startDate"]
                ed = window["endDate"]
                ps = combo["partySize"]
                duration_n = window["duration"]

                price, fetch_status = fetch_price(
                    resort["resortCode"],
                    combo["adults"],
                    combo["children"],
                    combo["birthdates"],
                    sd, ed
                )

                key = (resort["id"], ps, sd, duration_n)
                all_results[key] = price

                if price is None:
                    no_price_count += 1
                    if fetch_status == "error":
                        error_count += 1
                        print(f"  {ps} {sd}: API error")
                    elif fetch_status not in ("not_for_sale", "closed"):
                        print(f"  {ps} {sd}: no price ({fetch_status})")
                else:
                    print(f"  {ps} {sd}: £{price:,}")

                # Work out signal from accumulated history
                history = load_price_history_from_csv(resort["id"], ps, sd, duration_n)
                if price:
                    history.append({"date": timestamp[:10], "price": price})
                signal = calculate_signal(history)

                # Enriched fields
                departure_dt   = datetime.strptime(sd, "%Y-%m-%d").date()
                days_before    = (departure_dt - run_date).days
                dow_sampled    = run_date.weekday()  # 0=Mon … 6=Sun

                key = (resort["id"], ps, sd, duration_n)
                hist = historical_stats.get(key)
                if hist:
                    min_seen   = min(hist["min"], price) if price else hist["min"]
                    max_seen   = max(hist["max"], price) if price else hist["max"]
                    first_seen = hist["first"]
                    is_cheapest = 1 if (price and price <= hist["min"]) else 0
                else:
                    # First time we've ever seen this combo
                    min_seen   = price if price else ""
                    max_seen   = price if price else ""
                    first_seen = price if price else ""
                    is_cheapest = 1 if price else ""

                csv_rows.append({
                    "timestamp":             timestamp,
                    "resort_id":             resort["id"],
                    "resort_code":           resort["resortCode"],
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

    # Write CSV
    print(f"\nLogging {len(csv_rows)} rows to {CSV_FILE}...")
    log_to_csv(csv_rows, test_mode=args.test)

    # Inject into HTML
    print(f"Building updated RESORT_DATA...")
    js_string = build_resort_data_js(all_results)
    inject_into_html(js_string, test_mode=args.test)

    # Check alerts
    if not args.test:
        check_for_alerts(all_results, previous_signals)

    # Health check — only alert on actual API errors, not pre-season "not for sale" responses
    total = len(csv_rows)
    prices_fetched = total - no_price_count
    if error_count > 0 and total > 0 and error_count / total > 0.3:
        send_alert(
            "When To Book health alert — API errors detected",
            f"{error_count}/{total} fetches failed with network/API errors (not including expected pre-season no-price responses). "
            f"Check the GitHub Actions logs.\n\nRun timestamp: {timestamp}"
        )

    print(f"\nDone. {prices_fetched}/{total} prices fetched successfully.")
    if no_price_count:
        print(f"  {no_price_count} no-price responses ({error_count} errors, rest are pre-season/closed).")

if __name__ == "__main__":
    main()
