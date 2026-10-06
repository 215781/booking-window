#!/usr/bin/env python3
"""Daily health check for When To Book (run by .github/workflows/data_health.yml).

Checks, using only the repo and the GitHub API:
  - every price CSV collected something recently, from every resort it should cover
  - CSVs are well under GitHub's 100 MB file limit
  - the site deploy, email job and data backup have succeeded recently
Prints a report, writes it to health_report.md and exits 1 if anything needs attention.
"""
import csv, json, os, sys, urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "_data"
REPO = os.environ.get("GITHUB_REPOSITORY", "215781/booking-window")
TOKEN = os.environ.get("GH_TOKEN", "")
NOW = datetime.now(timezone.utc)
TODAY = NOW.date()

# file, timestamp column, resort column, expected resorts, max age in days (schedules run late)
SOURCES = [
    ("prices_clubmed.csv", "timestamp", "resort_id", 11, 2, "Club Med Alps ski"),
    ("prices_clubmed_ski_international.csv", "collected_at", "resort_id", 8, 2, "Club Med international ski"),
    ("prices_clubmed_summer.csv", "collected_at", "resort_id", 22, 2, "Club Med sun"),
    ("prices_markwarner_summer.csv", "timestamp", "resort_id", 4, 2, "Mark Warner sun"),
    ("prices_markwarner.csv", "timestamp", "resort_id", 1, 2, "Mark Warner ski"),
]
SIZE_WARN_MB = 85
WORKFLOWS = [  # workflow file, max hours since last success
    ("deploy_site.yml", 36, "Site deploy (Cloudflare Pages)"),
    ("email.yml", 36, "Email automation (Kit)"),
]
BACKUP_MAX_DAYS = 5


def gh(path):
    req = urllib.request.Request(f"https://api.github.com/repos/{REPO}/{path}",
                                 headers={"Accept": "application/vnd.github+json",
                                          **({"Authorization": f"Bearer {TOKEN}"} if TOKEN else {})})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def tail_rows(path, nbytes=4_000_000):
    """Header + rows from the last few MB of a big append-only CSV (fast, enough for ~2 days)."""
    with open(path, "rb") as f:
        header = f.readline().decode()
        size = path.stat().st_size
        f.seek(max(len(header), size - nbytes))
        chunk = f.read().decode(errors="ignore")
    lines = chunk.split("\n")[1:] if size > nbytes else chunk.split("\n")
    return csv.DictReader([header] + [l for l in lines if l.strip()])


def check_sources(problems, lines):
    for name, tcol, rcol, expected, max_age, label in SOURCES:
        path = DATA / name
        if not path.exists():
            problems.append(f"{label}: {name} is missing")
            continue
        mb = path.stat().st_size / 1e6
        days, resorts = {}, {}
        for row in tail_rows(path):
            d = (row.get(tcol) or "")[:10]
            if len(d) == 10:
                days[d] = days.get(d, 0) + 1
                resorts.setdefault(d, set()).add(row.get(rcol))
        if not days:
            problems.append(f"{label}: no rows found")
            continue
        last = max(days)
        age = (TODAY - datetime.strptime(last, "%Y-%m-%d").date()).days
        # judge resort coverage on the latest day if complete, else the day before (batches still running)
        full = [d for d in sorted(days) if len(resorts[d]) >= expected]
        cover_day = full[-1] if full else last
        n = len(resorts[cover_day])
        lines.append(f"| {label} | {last} ({age}d) | {days[last]} | {n}/{expected} on {cover_day} | {mb:.1f} MB |")
        if age > max_age:
            problems.append(f"{label}: last collection {last} ({age} days ago)")
        if n < expected and (TODAY - datetime.strptime(cover_day, "%Y-%m-%d").date()).days > 1:
            problems.append(f"{label}: only {n} of {expected} resorts collected on {cover_day}")
        if mb > SIZE_WARN_MB:
            problems.append(f"{label}: {name} is {mb:.0f} MB - GitHub rejects files over 100 MB. Move to Neon now")


def check_workflows(problems, lines):
    for wf, max_h, label in WORKFLOWS:
        try:
            runs = gh(f"actions/workflows/{wf}/runs?status=success&per_page=1")["workflow_runs"]
        except Exception as e:  # noqa: BLE001
            problems.append(f"{label}: could not read runs ({e})")
            continue
        if not runs:
            problems.append(f"{label}: no successful run found")
            continue
        t = datetime.fromisoformat(runs[0]["updated_at"].replace("Z", "+00:00"))
        hours = (NOW - t).total_seconds() / 3600
        lines.append(f"| {label} | last success {t:%Y-%m-%d %H:%M} UTC ({hours:.0f}h ago) | | | |")
        if hours > max_h:
            problems.append(f"{label}: last success {hours:.0f} hours ago")


def check_backup(problems, lines):
    try:
        rels = [r for r in gh("releases?per_page=30") if r["tag_name"].startswith("backup-data-")]
    except Exception as e:  # noqa: BLE001
        problems.append(f"Backup: could not read releases ({e})")
        return
    if not rels:
        problems.append("Backup: no data snapshot release yet (backup.yml)")
        return
    t = datetime.fromisoformat(rels[0]["created_at"].replace("Z", "+00:00"))
    days = (NOW - t).days
    size = sum(a["size"] for a in rels[0]["assets"]) / 1e6
    lines.append(f"| Data backup | {rels[0]['tag_name']} ({days}d) | | | {size:.1f} MB |")
    if days > BACKUP_MAX_DAYS:
        problems.append(f"Backup: newest data snapshot is {days} days old")
    if size < 1:
        problems.append(f"Backup: newest snapshot is only {size:.2f} MB - looks empty")


def main():
    problems = []
    lines = ["| Check | Latest | Rows | Resorts | Size |", "|---|---|---|---|---|"]
    check_sources(problems, lines)
    check_workflows(problems, lines)
    check_backup(problems, lines)
    status = "ALL OK" if not problems else f"{len(problems)} problem(s)"
    report = [f"## When To Book health check {NOW:%Y-%m-%d %H:%M} UTC: {status}", ""]
    if problems:
        report += ["**Needs attention:**", ""] + [f"- {p}" for p in problems] + [""]
    report += lines
    text = "\n".join(report)
    print(text)
    Path("health_report.md").write_text(text + "\n")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
