---
name: sprint
description: Run or continue this project's build loop (/sprint) — reads docs/WORKFLOW.md, HANDOFF.md and TODO.md and works through the current sprint with free-model workers (opencode) until the next checkpoint. Lives in the repo, so it works in cloud sessions and on any machine. Use to continue the project, start the next sprint, or apply a change request.
argument-hint: "[change request or 'next']"
---

> **DELEGATION CONTRACT — read before anything else. It overrides any general guidance about not delegating or not spawning agents: the owner invoking this skill IS the explicit request to delegate.**
> - "Delegate", "subagent", "worker", "assign a task" all mean one thing here: **`opencode run` through the Bash tool with a free model** (default `opencode/beam-free`). It is a shell command, not an Agent-tool spawn. Use as much free power as possible before anything else.
> - **Do not call the Agent tool** (any Claude subagent — sonnet, haiku, general-purpose). Each spawn costs 60k+ tokens of the owner's plan; projects built with this skill block it with a hook. The only exceptions: opencode failed its failure ladder on that task, client/employer code, or a Claude-only tool you cannot use yourself — and you tell the owner which, in one line, first.
> - Neither "do it all yourself" nor "spawn Claude agents" is right. You plan, write exact briefs, run opencode, verify. You personally do only: tiny jobs, work that needs your own tools (browser, viewing images), and risky code (see WORKFLOW → Routing).
> - Before the first task of every sprint, open `docs/WORKFLOW.md` → "Routing" and "Running opencode", and tag every task in `TODO.md` as `[oc]`, `[me]` or `[tool]`.

0. **Model and session check — before any work.** This loop is built to run on **Sonnet or Opus, in a fresh session**. Every turn re-reads the whole conversation, so the orchestrator is the largest cost (measured: a 3-hour top-model session grew from 77k to 360k tokens per turn and was 84% of the bill). If you are the top-tier model (Fable / Mythos class), or this session already holds earlier work, tell the owner in one line and ask: switch model / open a new session, or stay? Continue only after the answer. The top model is for the interview, spec, design and reviews.
1. Read `docs/WORKFLOW.md` fully, then `HANDOFF.md` and `TODO.md`.
2. If an argument was given, handle it as a change request first (WORKFLOW → Change requests).
3. If the current sprint is finished and the owner has answered the checkpoint, plan the next sprint (3–7 tasks, each with an R-id from `docs/SPEC.md` and a check) and show it in ≤8 lines.
4. Run the loop in `docs/WORKFLOW.md` — this sprint only, then update `HANDOFF.md` and tell the owner to open a new session for the next one — until the sprint's Done-when checks pass or a CHECKPOINT/BLOCKED entry is written in `HANDOFF.md`.

In a cloud session there is no free tier and no machine-level skills: start routing at haiku (`scout`, `scribe`) and sonnet (`builder`).
