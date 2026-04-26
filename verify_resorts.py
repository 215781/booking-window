#!/usr/bin/env python3
"""
verify_resorts.py — probe unverified resort codes and departure days.
Tests Saturday (5) and Sunday (6) departures across the full ski season.
"""

import requests
import json
from datetime import datetime, timedelta

GRAPHQL_URL = "https://graphql.dcx.clubmed/"
HEADERS = {
    "Content-Type":    "application/json",
    "Accept":          "application/graphql-response+json,application/json;q=0.9",
    "Accept-Language": "en-GB",
    "Origin":          "https://www.clubmed.co.uk",
    "Referer":         "https://www.clubmed.co.uk/",
    "User-Agent":      "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/147.0.0.0 Safari/537.36",
}

QUERY = """mutation SearchPrice($id: ID!, $options: SearchPriceOptions) {
    searchPrice(id: $id, options: $options) {
        productId
        price { bestPrice }
        noPrice { reason }
    }
}"""

# Resorts to verify: (name, code, currently_set_day)
VERIFY = [
    # Previously verified code, departure day unknown
    ("Tignes",                  "TIGC_WINTER", None),
    ("Les Arcs Panorama",       "ARPC_WINTER", None),
    ("Peisey-Vallandry",        "PVAC_WINTER", None),
    ("Valmorel",                "VMOC_WINTER", None),
    ("Alpe d'Huez",             "ALHC_WINTER", None),
    ("La Rosière",              "LROC_WINTER", None),
    # Unverified code AND departure day
    ("Val d'Isère",             "VDIC_WINTER", None),
    ("Grand Massif",            "GMSM_WINTER", None),
    ("Val Thorens Sensations",  "VTSC_WINTER", None),
    ("Serre-Chevalier",         "SRCC_WINTER", None),
]

SKI_MONTHS = [(2026, 12)] + [(2027, m) for m in range(1, 5)]

def saturdays_sundays_in_month(year, month):
    """Return first Saturday and first Sunday in the month."""
    results = {5: None, 6: None}
    d = datetime(year, month, 1)
    while d.month == month and not all(results.values()):
        wd = d.weekday()
        if wd in results and results[wd] is None:
            results[wd] = d
        d += timedelta(days=1)
    return results  # {5: datetime_sat, 6: datetime_sun}

def probe(code, start_dt):
    end_dt = start_dt + timedelta(days=7)
    payload = {
        "operationName": "SearchPrice",
        "variables": {
            "id": code,
            "options": {
                "adults": 2, "children": 0, "birthdates": [],
                "startDate": start_dt.strftime("%Y-%m-%d"),
                "endDate":   end_dt.strftime("%Y-%m-%d"),
                "flexible": None,
                "departureCity": "NO",
                "isExclusiveSpacePage": False,
                "shouldGetRealPrice": True,
            },
        },
        "query": QUERY,
    }
    try:
        r = requests.post(GRAPHQL_URL, json=payload, headers=HEADERS, timeout=15)
        r.raise_for_status()
        data = r.json()
        result = data.get("data", {}).get("searchPrice", {})
        price_obj = result.get("price")
        if price_obj and price_obj.get("bestPrice"):
            return int(price_obj["bestPrice"]), "PRICE"
        no_price = result.get("noPrice")
        if no_price:
            reason = no_price.get("reason", "?")
            if "not for sale" in reason.lower():
                return None, "not_for_sale"
            elif "closed" in reason.lower():
                return None, "closed"
            else:
                return None, f"no_price:{reason}"
        return None, "empty"
    except Exception as e:
        return None, f"ERROR:{e}"

print(f"{'Resort':<30} {'Code':<18} {'Month':<10} {'Sat':<20} {'Sun':<20}")
print("-" * 100)

for name, code, _ in VERIFY:
    sat_hits = []
    sun_hits = []
    sat_statuses = set()
    sun_statuses = set()

    for year, month in SKI_MONTHS:
        dates = saturdays_sundays_in_month(year, month)
        month_label = f"{year}-{month:02d}"

        sat_dt = dates[5]
        sun_dt = dates[6]

        if sat_dt:
            price, status = probe(code, sat_dt)
            sat_statuses.add(status)
            if status == "PRICE":
                sat_hits.append(f"{month_label}=£{price}")

        if sun_dt:
            price, status = probe(code, sun_dt)
            sun_statuses.add(status)
            if status == "PRICE":
                sun_hits.append(f"{month_label}=£{price}")

    sat_summary = ", ".join(sat_hits) if sat_hits else f"none ({', '.join(sat_statuses)})"
    sun_summary = ", ".join(sun_hits) if sun_hits else f"none ({', '.join(sun_statuses)})"
    print(f"{name:<30} {code:<18} {'all':<10} SAT: {sat_summary}")
    print(f"{'':<30} {'':<18} {'':<10} SUN: {sun_summary}")
    print()
