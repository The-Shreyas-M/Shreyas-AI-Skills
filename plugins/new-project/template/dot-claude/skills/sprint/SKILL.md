---
name: sprint
description: Run or continue this project's build loop (/sprint) — reads docs/WORKFLOW.md, HANDOFF.md and TODO.md and works through the current sprint with cheap subagents until the next checkpoint. Lives in the repo, so it works in cloud sessions and on any machine. Use to continue the project, start the next sprint, or apply a change request.
argument-hint: "[change request or 'next']"
---

1. Read `docs/WORKFLOW.md` fully, then `HANDOFF.md` and `TODO.md`.
2. If an argument was given, handle it as a change request first (WORKFLOW → Change requests).
3. If the current sprint is finished and the owner has answered the checkpoint, plan the next sprint (3–7 tasks, each with an R-id from `docs/SPEC.md` and a check) and show it in ≤8 lines.
4. Run the loop in `docs/WORKFLOW.md` until the sprint's Done-when checks pass or a CHECKPOINT/BLOCKED entry is written in `HANDOFF.md`.

In a cloud session there is no free tier and no machine-level skills: start routing at haiku (`scout`, `scribe`) and sonnet (`builder`).
