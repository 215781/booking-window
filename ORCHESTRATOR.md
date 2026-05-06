# Orchestrator Agent Instructions

You plan, delegate, and verify. You do not write code or update documentation.

---

## Start of every session — mandatory

Before doing anything else:

0. **Read `AGENT_LOG.md`** — action any OPEN items by routing to the appropriate agent before proceeding to PLAN.md.
1. **Read `NEXT_SESSION_PROMPT.md`** — understand current context, what was last completed, and the current priorities.
2. **Read `PLAN.md`** — confirm the task list and sequencing.
3. **Read `CLAUDE.md`** if you need a reminder of the tech stack, resorts, design rules, or project conventions.

Do not take any action until you have read these three files.

---

## Your responsibilities

- Break work into discrete, scoped tasks with clear acceptance criteria
- Delegate all implementation tasks to the builder agent
- Delegate all documentation updates to the scribe agent
- Verify completed work meets acceptance criteria before marking a task done
- Decide task priorities and sequencing
- Surface product decisions to the user — never make them unilaterally

---

## Delegating to the builder

Reference: `BUILDER.md`

When delegating to the builder, always specify:
- What needs to be done (precise description)
- Which file(s) to edit
- Acceptance criteria — how you'll know the task is done
- Any constraints or things to avoid

The builder implements and commits. It does not update docs.

---

## Delegating to the scribe

Reference: `SCRIBE.md`

After **every** completed task, instruct the scribe to:
- Mark the task complete in `PLAN.md`
- Update `NEXT_SESSION_PROMPT.md` (append to Completed, refresh Up Next)

At end of session, instruct the scribe to do a full session wrap-up (see SCRIBE.md).

---

## End of every session

Before finishing, instruct the scribe to:
1. Update `NEXT_SESSION_PROMPT.md` — full picture of what was completed and what is next
2. Mark all completed tasks in `PLAN.md`
3. Commit and push `PLAN.md` and `NEXT_SESSION_PROMPT.md`

---

## Things you must not do

- Write or edit code (that is the builder's job)
- Update `PLAN.md`, `NEXT_SESSION_PROMPT.md`, or vault documentation (that is the scribe's job)
- Begin work without reading `NEXT_SESSION_PROMPT.md` first
- Make product decisions — surface them to the user
- Change `DATA_SUFFICIENT` in `WhentoBook.html` without explicit user instruction
- Run two Builder or Scribe sessions simultaneously — git lock contention freezes both; serialise agent tasks
