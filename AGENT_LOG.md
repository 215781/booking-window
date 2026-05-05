# Agent Communication Log

All agents append entries here. Orchestrator reads this at the start of every session and actions any open items before reading PLAN.md.

---

## Format

```
[YYYY-MM-DD HH:MM UTC] [FROM_AGENT] → [TO_AGENT]: [SEVERITY] [MESSAGE]
```

Severity levels: `OK` | `INFO` | `WARNING` | `CRITICAL`

Entries are append-only. Do not delete old entries — they form the audit trail.
To close an item, append a `[RESOLVED]` entry referencing the original timestamp.

---

## Log

[2026-05-05 00:00 UTC] [SCRIBE] → [ORCHESTRATOR]: INFO AGENT_LOG.md initialised — data quality monitoring infrastructure being set up this session
