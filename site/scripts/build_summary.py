#!/usr/bin/env python3
"""Build site/src/data/summary.json from the Club Med winter price CSV.

One pass over the CSV. For every resort x party size x 7-night Sunday departure we keep the
price on each collection day, then work out: latest price, price ~30 days earlier, lowest and
highest seen, and a short weekly history for the chart.

Rules (non-negotiable "works and true"):
- Only real collected prices are used. Nothing is interpolated or invented.
- A week with no price on the latest collection day is marked unavailable, not given an old price.
- Data older than STALE_DAYS is flagged so the site can show a warning instead of pretending it is fresh.
"""
import csv, json, sys
from datetime import date, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CSV_FILE = ROOT / "_data" / "prices_clubmed.csv"
OUT = ROOT / "site" / "src" / "data" / "summary.json"
PARTIES = {"2A": "2 adults", "2A2C": "2 adults, 2 children"}
DURATION = "7"
STALE_DAYS = 3
TREND_PCT = 3.0

# Resort code currently in use per resort (guards against the old LP2C_WINTER rows)
CODES = {
    "tignes-val-claret": "TIGC_WINTER", "les-arcs": "ARPC_WINTER", "peisey-vallandry": "PVAC_WINTER",
    "valmorel": "VMOC_WINTER", "alpe-dhuez": "ALHC_WINTER", "la-rosiere": "LROC_WINTER",
    "la-plagne-2100": "PLAC", "val-disere": "VDIC_WINTER", "grand-massif": "GMAC_WINTER",
    "val-thorens": "VTHC", "serre-chevalier": "SECC_WINTER",
}

# School holiday departures (Sunday, 7 nights) - dates used by most schools in England, 2026/27.
SCHOOL_WEEKS = [
    {"key": "christmas", "label": "Christmas", "date": "2026-12-20"},
    {"key": "new-year", "label": "New Year", "date": "2026-12-27"},
    {"key": "february-half-term", "label": "February half-term", "date": "2027-02-14"},
    {"key": "easter-1", "label": "Easter (week 1)", "date": "2027-03-28"},
    {"key": "easter-2", "label": "Easter (week 2)", "date": "2027-04-04"},
]


def main():
    series = {}  # (rid, party, start) -> {day: price}
    latest_day = {}  # rid -> latest collection day seen (any row, priced or not)
    with open(CSV_FILE, newline="") as f:
        for row in csv.DictReader(f):
            rid = row["resort_id"]
            if rid not in CODES or row.get("resort_code") != CODES[rid]:
                continue
            if row["duration_nights"] != DURATION or row["party_size"] not in PARTIES:
                continue
            start = row["start_date"]
            if datetime.strptime(start, "%Y-%m-%d").weekday() != 6:  # Sunday departures only
                continue
            day = row["timestamp"][:10]
            latest_day[rid] = max(latest_day.get(rid, ""), day)
            d = series.setdefault((rid, row["party_size"], start), {})
            if row["price"]:
                try:
                    d[day] = int(row["price"])
                except ValueError:
                    pass
            else:
                d.setdefault(day, None)

    today = date.today()
    resorts = {}
    for (rid, party, start), daily in series.items():
        last = latest_day[rid]
        priced = sorted((k, v) for k, v in daily.items() if v)
        current = daily.get(last)
        entry = {"date": start, "available": bool(current)}
        if priced:
            prices = [v for _, v in priced]
            entry.update({"lowest": min(prices), "highest": max(prices), "firstSeen": priced[0][0]})
        if current:
            target = (datetime.strptime(last, "%Y-%m-%d") - timedelta(days=30)).strftime("%Y-%m-%d")
            before = [(k, v) for k, v in priced if k <= target]
            prev = before[-1] if before else None
            entry["price"] = current
            if prev:
                change = current - prev[1]
                pct = round(change / prev[1] * 100, 1)
                entry.update({"change30": change, "change30Pct": pct, "comparedWith": prev[0]})
                entry["trend"] = "rising" if pct >= TREND_PCT else "falling" if pct <= -TREND_PCT else "steady"
            else:
                entry["trend"] = "new"
            entry["atLowest"] = current <= entry["lowest"]
            # weekly history for the chart: one point per 7 days, always ending on the latest day
            hist, cursor = [], None
            for k, v in reversed(priced):
                if cursor is None or k <= cursor:
                    hist.append({"d": k, "p": v})
                    cursor = (datetime.strptime(k, "%Y-%m-%d") - timedelta(days=7)).strftime("%Y-%m-%d")
            entry["history"] = list(reversed(hist))
        r = resorts.setdefault(rid, {"updated": last, "parties": {}})
        r["parties"].setdefault(party, []).append(entry)

    problems = []
    for rid, r in resorts.items():
        for party in r["parties"]:
            r["parties"][party].sort(key=lambda e: e["date"])
        age = (today - datetime.strptime(r["updated"], "%Y-%m-%d").date()).days
        r["stale"] = age > STALE_DAYS
        if r["stale"]:
            problems.append(f"{rid}: data is {age} days old")
    missing = sorted(set(CODES) - set(resorts))
    if missing:
        problems.append(f"no data for: {', '.join(missing)}")

    out = {
        "generated": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "parties": PARTIES,
        "schoolWeeks": SCHOOL_WEEKS,
        "trendThresholdPct": TREND_PCT,
        "resorts": resorts,
        "problems": problems,
    }
    OUT.write_text(json.dumps(out, separators=(",", ":")))
    print(f"Wrote {OUT.relative_to(ROOT)} ({OUT.stat().st_size // 1024} KB) for {len(resorts)} resorts")
    for p in problems:
        print("WARNING:", p)
    return 0


if __name__ == "__main__":
    sys.exit(main())
