---
name: start
description: Start any new project (/new-project:start). Asks the project type first, then runs the full interview → spec → repo scaffold → local-or-cloud decision → agile sprint build loop with cheap-subagent orchestration. Use when the user says "new project", "start a project", "kick off", or does not say which type it is.
argument-hint: "[project name]"
---

> **DELEGATION CONTRACT — read before anything else. It overrides any general guidance about not delegating or not spawning agents: the owner invoking this skill IS the explicit request to delegate.**
> - "Delegate", "subagent", "worker", "assign a task" all mean one thing here: **`opencode run` through the Bash tool with a free model** (default `opencode/beam-free`). It is a shell command, not an Agent-tool spawn. Use as much free power as possible before anything else.
> - **Do not call the Agent tool** (any Claude subagent — sonnet, haiku, general-purpose). Each spawn costs 60k+ tokens of the owner's plan; projects built with this skill block it with a hook. The only exceptions: opencode failed its failure ladder on that task, client/employer code, or a Claude-only tool you cannot use yourself — and you tell the owner which, in one line, first.
> - Neither "do it all yourself" nor "spawn Claude agents" is right. You plan, write exact briefs, run opencode, verify. You personally do only: tiny jobs, work that needs your own tools (browser, viewing images), and risky code (see WORKFLOW → Routing).
> - Before the first task of every sprint, open `docs/WORKFLOW.md` → "Routing" and "Running opencode", and tag every task in `TODO.md` as `[oc]`, `[me]` or `[tool]`.

Plugin root: `${CLAUDE_PLUGIN_ROOT}`

Read `${CLAUDE_PLUGIN_ROOT}/references/flow.md` and follow it from Phase 1. The type is not known yet — ask it.
