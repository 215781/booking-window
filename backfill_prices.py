#!/usr/bin/env python3
"""
backfill_prices.py — Fill gaps in price_history.csv

For each (resort, party_size, start_date, duration) combo, carries the last
known price forward into any missing calendar dates between the first
observation and yesterday.

Backfilled rows are stamped with timestamp YYYY-MM-DDT00:00:00Z — exactly
midnight UTC. Live checker rows always have a non-zero time component
(e.g. T06:15:43Z). Any analysis that needs to exclude interpolated data can
filter by timestamp NOT LIKE '%T00:00:00Z'.

After running, regenerate RESORT_DATA with:
    python clubmed_checker.py --inject-only

Usage:
    python backfill_prices.py            # Fill all gaps up to yesterday
    python backfill_prices.py --dry-run  # Preview without writing
"""

import csv
import sys
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

CSV_FILE = "_data/price_history.csv"


def main():
    dry_run = "--dry-run" in sys.argv

    if not Path(CSV_FILE).exists():
        print(f"ERROR: {CSV_FILE} not found")
        sys.exit(1)

    rows = list(csv.DictReader(open(CSV_FILE, newline="")))
    fieldnames = list(rows[0].keys()) if rows else []
    print(f"Loaded {len(rows):,} rows from {CSV_FILE}")

    yesterday = (date.today() - timedelta(days=1)).isoformat()

    # Group by (resort_id, resort_code, party_size, start_date, end_date, duration_nights)
    by_combo = defaultdict(list)
    for r in rows:
        key = (
            r["resort_id"], r["resort_code"], r["party_size"],
            r["start_date"], r.get("end_date", ""),
            r.get("duration_nights", "7"),
        )
        by_combo[key].append(r)

    backfill_rows = []

    for key, combo_rows in by_combo.items():
        resort_id, resort_code, party_size, start_date, end_date, duration_nights = key

        # Dates already represented in the CSV for this combo
        existing_dates = set(r["timestamp"][:10] for r in combo_rows)

        # Only rows that have an actual price (ignore no-price rows for carry-forward)
        priced = sorted(
            ((r["timestamp"][:10], r) for r in combo_rows if r.get("price")),
            key=lambda x: x[0],
        )
        if not priced:
            continue  # nothing to carry forward

        # Build date→row lookup for the days we have real prices
        price_by_date = {d: r for d, r in priced}
        first_date = date.fromisoformat(priced[0][0])
        end_date_limit = date.fromisoformat(yesterday)

        current = first_date
        last_known_row = None

        while current <= end_date_limit:
            d_str = current.isoformat()
            if d_str in price_by_date:
                last_known_row = price_by_date[d_str]
            elif last_known_row is not None and d_str not in existing_dates:
                dep_date = date.fromisoformat(start_date)
                backfill_rows.append({
                    "timestamp":             f"{d_str}T00:00:00Z",
                    "resort_id":             resort_id,
                    "resort_code":           resort_code,
                    "party_size":            party_size,
                    "start_date":            start_date,
                    "end_date":              end_date,
                    "duration_nights":       duration_nights,
                    "price":                 last_known_row.get("price", ""),
                    "signal":                last_known_row.get("signal", ""),
                    "days_before_departure": (dep_date - current).days,
                    "day_of_week_sampled":   current.weekday(),
                    "price_first_seen":      "",
                    "price_min_seen":        "",
                    "price_max_seen":        "",
                    "is_cheapest_ever":      "",
                })
            current += timedelta(days=1)

    print(f"Found {len(backfill_rows):,} rows to backfill")

    if not backfill_rows:
        print("No gaps to fill — CSV is complete.")
        return

    # Preview
    from collections import Counter
    by_date = Counter(r["timestamp"][:10] for r in backfill_rows)
    print("Backfill coverage:")
    for d, count in sorted(by_date.items()):
        print(f"  {d}: {count:4d} rows")

    if dry_run:
        print("\n[dry-run] No changes written.")
        return

    with open(CSV_FILE, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writerows(backfill_rows)

    print(f"\nAppended {len(backfill_rows):,} backfill rows to {CSV_FILE}")
    print("Backfilled rows: timestamp ends T00:00:00Z (distinguishable from live data)")
    print("\nNext step: regenerate RESORT_DATA with:")
    print("  python clubmed_checker.py --inject-only")


if __name__ == "__main__":
    main()
