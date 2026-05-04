#!/usr/bin/env python3
"""
backfill_csv.py — Enrich existing price_history.csv rows with new columns.

Adds to rows that are missing them:
  duration_nights, days_before_departure, day_of_week_sampled,
  price_first_seen, price_min_seen, price_max_seen, is_cheapest_ever

Safe to run multiple times — detects already-enriched files and skips.
Usage: python3 backfill_csv.py
"""

import csv
import sys
from datetime import datetime, date
from pathlib import Path

CSV_FILE = "_data/price_history.csv"

NEW_HEADERS = [
    "timestamp", "resort_id", "resort_code", "party_size",
    "start_date", "end_date", "duration_nights", "price", "signal",
    "days_before_departure", "day_of_week_sampled",
    "price_first_seen", "price_min_seen", "price_max_seen", "is_cheapest_ever",
]

def main():
    p = Path(CSV_FILE)
    if not p.exists():
        print(f"{CSV_FILE} not found.")
        sys.exit(1)

    with open(p, newline="") as f:
        reader = csv.DictReader(f)
        existing_headers = reader.fieldnames or []
        rows = list(reader)

    if "days_before_departure" in existing_headers and "is_cheapest_ever" in existing_headers:
        print("File already fully enriched — nothing to do.")
        sys.exit(0)

    print(f"Read {len(rows)} rows. Backfilling new columns...")

    # First pass: compute per-combo stats from rows that have prices
    # Process in order (CSV is chronological) so "first" = first encountered
    combo_stats = {}  # (resort_id, party_size, start_date) -> {min, max, first}
    for row in rows:
        raw = row.get("price", "")
        if not raw:
            continue
        try:
            price = int(raw)
        except (ValueError, TypeError):
            continue
        key = (row["resort_id"], row["party_size"], row["start_date"])
        if key not in combo_stats:
            combo_stats[key] = {"min": price, "max": price, "first": price}
        else:
            s = combo_stats[key]
            s["min"] = min(s["min"], price)
            s["max"] = max(s["max"], price)

    # Second pass: build enriched rows
    # Track running min per combo so is_cheapest_ever reflects "cheapest at time of this row"
    running_min = {}
    enriched = []
    for row in rows:
        # duration_nights
        try:
            sd = row.get("start_date", "")
            ed = row.get("end_date", "")
            if sd and ed:
                duration_n = (datetime.strptime(ed, "%Y-%m-%d") -
                              datetime.strptime(sd, "%Y-%m-%d")).days
            else:
                duration_n = ""
        except Exception:
            duration_n = ""

        # days_before_departure + day_of_week_sampled
        try:
            ts = row.get("timestamp", "")
            run_dt = datetime.strptime(ts[:10], "%Y-%m-%d").date()
            dep_dt = datetime.strptime(sd, "%Y-%m-%d").date()
            days_before = (dep_dt - run_dt).days
            dow = run_dt.weekday()
        except Exception:
            days_before = ""
            dow = ""

        # price stats
        raw = row.get("price", "")
        key = (row.get("resort_id", ""), row.get("party_size", ""), sd)
        stats = combo_stats.get(key)

        if raw and stats:
            try:
                price = int(raw)
            except (ValueError, TypeError):
                price = None
        else:
            price = None

        if stats:
            first_seen = stats["first"]
            min_seen   = stats["min"]
            max_seen   = stats["max"]
        else:
            first_seen = raw if raw else ""
            min_seen   = raw if raw else ""
            max_seen   = raw if raw else ""

        # is_cheapest_ever: was this price the running minimum at time of recording?
        if price is not None:
            prev_min = running_min.get(key)
            is_cheapest = 1 if (prev_min is None or price <= prev_min) else 0
            running_min[key] = min(prev_min, price) if prev_min is not None else price
        else:
            is_cheapest = ""

        enriched.append({
            "timestamp":             row.get("timestamp", ""),
            "resort_id":             row.get("resort_id", ""),
            "resort_code":           row.get("resort_code", ""),
            "party_size":            row.get("party_size", ""),
            "start_date":            sd,
            "end_date":              ed,
            "duration_nights":       duration_n,
            "price":                 raw,
            "signal":                row.get("signal", ""),
            "days_before_departure": days_before,
            "day_of_week_sampled":   dow,
            "price_first_seen":      first_seen,
            "price_min_seen":        min_seen,
            "price_max_seen":        max_seen,
            "is_cheapest_ever":      is_cheapest,
        })

    # Write back
    backup = Path(CSV_FILE + ".bak")
    p.rename(backup)
    print(f"Backed up original to {backup}")

    with open(p, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=NEW_HEADERS)
        writer.writeheader()
        writer.writerows(enriched)

    print(f"Written {len(enriched)} enriched rows to {CSV_FILE}")
    print(f"New columns added: duration_nights, days_before_departure, day_of_week_sampled,")
    print(f"                   price_first_seen, price_min_seen, price_max_seen, is_cheapest_ever")

if __name__ == "__main__":
    main()
