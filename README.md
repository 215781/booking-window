# Booking Window

Club Med ski resort price intelligence. Tracks live pricing across all major French Alps resorts twice daily, building the historical context that tells you whether today's price is an opportunity.

Built by Drop Media Ltd.

---

## Repo structure

```
BookingWindow.html      — the website (single file, open directly in browser)
clubmed_checker.py      — price checker script
_data/price_history.csv — full price log (every check, never deleted; not served by GitHub Pages)
.github/workflows/
  price_checker.yml     — GitHub Actions cron (runs at 06:00 and 18:00 UTC)
```

---

## Running the checker locally

Requires Python 3.9+ and `requests`:

```bash
pip install requests

# Test mode — fetches prices, prints results, writes nothing
python clubmed_checker.py --test

# Verify the API is reachable from your IP
python clubmed_checker.py --verify

# Normal run — fetches prices, updates HTML and CSV
python clubmed_checker.py
```

**Important:** The Club Med API blocks datacenter IPs. Run locally from home broadband, or via GitHub Actions (which uses non-datacenter IPs). Do not run from a standard VPS or cloud function without a residential proxy.

---

## GitHub Actions setup

The workflow runs automatically at 06:00 and 18:00 UTC. To enable email alerts, add three repository secrets (Settings > Secrets and variables > Actions):

| Secret | Value |
|---|---|
| `GMAIL_ADDRESS` | Your Gmail address |
| `GMAIL_APP_PASS` | 16-character Gmail App Password (not your normal password) |
| `ALERT_TO` | Email address to receive alerts |

To generate a Gmail App Password: Google Account > Security > 2-Step Verification > App Passwords.

You can also trigger a manual run from the Actions tab at any time.

---

## Resort codes

| Resort | Code | Status |
|---|---|---|
| Tignes Val Claret | `GRVA` | Verified |
| Les Arcs Panorama | `ARCS` | Unverified |
| Peisey-Vallandry | `PEIS` | Unverified |
| Valmorel | `VALM` | Unverified |
| Alpe d'Huez | `ADHU` | Unverified |
| La Rosière | `LROS` | Unverified |

To verify a code: visit the resort page on clubmed.co.uk, open browser devtools (F12), go to the Network tab, trigger a price search, and look for the GraphQL `SearchPrice` request. The `id` field in the request payload is the resort code.

---

## Signal logic

| Signal | Condition |
|---|---|
| Book Now | Price dropped £50+ in 14 days AND below 30-day average |
| Watch | Price risen £50+ in 14 days, OR below average but no clear drop |
| Hold | Stable or insufficient data |

Signals improve in accuracy as price history accumulates. In the first few weeks, most resorts will show Hold — this is expected.

---

## Data notes

- All prices are accommodation only (`departureCity: "NO"`) — flight prices are excluded intentionally as they are too volatile and would cause false signals.
- Saturday departures only, 7-night stays.
- `_data/price_history.csv` is append-only. Never delete it — the historical record is the product.

---

© 2026 Drop Media Ltd
