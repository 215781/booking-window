#!/usr/bin/env python3
"""Build site/src/data/summary.json from the price CSVs (one pass per CSV).

For every collection x resort x party size x future 7-night departure: latest price,
price ~30 days earlier, lowest/highest seen and a short weekly history.

Rules ("works and true"):
- Only real collected prices. Nothing interpolated or invented.
- A departure with no price on the resort's latest collection day is marked unavailable.
- Past departures are dropped. Stale collections are flagged so the site can say so.
"""
import csv, json, sys
from datetime import date, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "site" / "src" / "data" / "summary.json"
PARTIES = {"2A": "2 adults", "2A2C": "2 adults, 2 children"}
STALE_DAYS = 3
TREND_PCT = 3.0
HISTORY_POINTS = 16

COLLECTIONS = {
    "clubmed-ski": {
        "csv": "prices_clubmed.csv", "time": "timestamp", "dep": "start_date", "price": "price",
        "where": lambda r: r["duration_nights"] == "7",
        # current resort code per resort (guards against the old LP2C_WINTER rows)
        "codes": {"tignes-val-claret": "TIGC_WINTER", "les-arcs": "ARPC_WINTER", "peisey-vallandry": "PVAC_WINTER",
                  "valmorel": "VMOC_WINTER", "alpe-dhuez": "ALHC_WINTER", "la-rosiere": "LROC_WINTER",
                  "la-plagne-2100": "PLAC", "val-disere": "VDIC_WINTER", "grand-massif": "GMAC_WINTER",
                  "val-thorens": "VTHC", "serre-chevalier": "SECC_WINTER"},
    },
    "clubmed-sun": {
        "csv": "prices_clubmed_summer.csv", "time": "collected_at", "dep": "departure_date", "price": "price_pp",
        "where": lambda r: r["duration_nights"] == "7",
    },
    "markwarner-sun": {
        "csv": "prices_markwarner_summer.csv", "time": "timestamp", "dep": "start_date", "price": "price",
        "where": lambda r: r["duration_nights"] == "7" and r["airport"] == "LGW",
    },
}


def summarise(cfg, today):
    series, latest_day = {}, {}
    path = ROOT / "_data" / cfg["csv"]
    if not path.exists():
        return {}, [f"{cfg['csv']} missing"]
    codes = cfg.get("codes")
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            rid = row["resort_id"]
            if codes and (rid not in codes or row.get("resort_code") != codes[rid]):
                continue
            if row["party_size"] not in PARTIES or not cfg["where"](row):
                continue
            day = row[cfg["time"]][:10]
            latest_day[rid] = max(latest_day.get(rid, ""), day)
            d = series.setdefault((rid, row["party_size"], row[cfg["dep"]]), {})
            raw = row[cfg["price"]]
            if raw:
                try:
                    d[day] = int(float(raw))
                except ValueError:
                    pass
            else:
                d.setdefault(day, None)

    resorts, problems = {}, []
    todays = today.isoformat()
    for (rid, party, start), daily in series.items():
        if start <= todays:
            continue
        last = latest_day[rid]
        priced = sorted((k, v) for k, v in daily.items() if v)
        current = daily.get(last)
        e = {"date": start, "available": bool(current)}
        if priced:
            prices = [v for _, v in priced]
            e.update({"lowest": min(prices), "highest": max(prices), "firstSeen": priced[0][0]})
        if current:
            target = (datetime.strptime(last, "%Y-%m-%d") - timedelta(days=30)).strftime("%Y-%m-%d")
            before = [(k, v) for k, v in priced if k <= target]
            e["price"] = current
            if before:
                prev = before[-1]
                change = current - prev[1]
                pct = round(change / prev[1] * 100, 1)
                e.update({"change30": change, "change30Pct": pct, "comparedWith": prev[0],
                          "trend": "rising" if pct >= TREND_PCT else "falling" if pct <= -TREND_PCT else "steady"})
            else:
                e["trend"] = "new"
            e["atLowest"] = current <= e["lowest"]
            hist, cursor = [], None
            for k, v in reversed(priced):
                if cursor is None or k <= cursor:
                    hist.append({"d": k, "p": v})
                    cursor = (datetime.strptime(k, "%Y-%m-%d") - timedelta(days=7)).strftime("%Y-%m-%d")
                if len(hist) >= HISTORY_POINTS:
                    break
            e["history"] = list(reversed(hist))
        r = resorts.setdefault(rid, {"updated": last, "parties": {}})
        r["parties"].setdefault(party, []).append(e)

    for rid, r in resorts.items():
        for party in r["parties"]:
            r["parties"][party].sort(key=lambda x: x["date"])
        age = (today - datetime.strptime(r["updated"], "%Y-%m-%d").date()).days
        r["stale"] = age > STALE_DAYS
        if r["stale"]:
            problems.append(f"{rid}: latest check is {age} days old")
    if codes:
        missing = sorted(set(codes) - set(resorts))
        if missing:
            problems.append(f"no data for: {', '.join(missing)}")
    return resorts, problems


def main():
    today = date.today()
    out = {"generated": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"), "parties": PARTIES,
           "trendThresholdPct": TREND_PCT, "collections": {}, "problems": {}}
    for key, cfg in COLLECTIONS.items():
        resorts, problems = summarise(cfg, today)
        out["collections"][key] = resorts
        out["problems"][key] = problems
        n = sum(len(v) for r in resorts.values() for v in r["parties"].values())
        print(f"{key}: {len(resorts)} resorts, {n} future departures")
        for p in problems:
            print(f"  WARNING {key}: {p}")
    OUT.write_text(json.dumps(out, separators=(",", ":")))
    print(f"Wrote {OUT.relative_to(ROOT)} ({OUT.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    sys.exit(main())
