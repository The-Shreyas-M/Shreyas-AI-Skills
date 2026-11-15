---
name: local-app
description: Start a new local app, script, automation or tool that runs on this machine (/new-project:local-app). Skips the type question and runs the local-tool interview (inputs, outputs, run pattern, credentials, packaging), then spec, scaffold and the local build loop.
argument-hint: "[project name]"
---

> **DELEGATION CONTRACT — read before anything else. It overrides any general guidance about not delegating or not spawning agents: the owner invoking this skill IS the explicit request to delegate.**
> - "Delegate", "subagent", "worker", "assign a task" all mean one thing here: **`opencode run` through the Bash tool with a free model** (default `opencode/beam-free`). It is a shell command, not an Agent-tool spawn. Use as much free power as possible before anything else.
> - **Do not call the Agent tool** (any Claude subagent — sonnet, haiku, general-purpose). Each spawn costs 60k+ tokens of the owner's plan; projects built with this skill block it with a hook. The only exceptions: opencode failed its failure ladder on that task, client/employer code, or a Claude-only tool you cannot use yourself — and you tell the owner which, in one line, first.
> - Neither "do it all yourself" nor "spawn Claude agents" is right. You plan, write exact briefs, run opencode, verify. You personally do only: tiny jobs, work that needs your own tools (browser, viewing images), and risky code (see WORKFLOW → Routing).
> - Before the first task of every sprint, open `docs/WORKFLOW.md` → "Routing" and "Running opencode", and tag every task in `TODO.md` as `[oc]`, `[me]` or `[tool]`.

Plugin root: `${CLAUDE_PLUGIN_ROOT}`

Type is fixed: **Local app / tool**. Do not ask it.

Read `${CLAUDE_PLUGIN_ROOT}/references/flow.md` and follow it, with these presets:
- Phase 1: ask only the name and the one-sentence pitch.
- Phase 2: offer nothing by default; `ai-video` only if it is a video/content tool.
- Phase 3: `interview-core.md` + `interview-local.md` (video/content or anything unusual: `interview-other.md`). Get one real example input and the expected output.
- Defaults to propose: Python + venv + `requirements.txt` + `run.bat`/`run.sh`; credentials in a gitignored `.env`.
- Phase 5: **local**.
- Sprint 1 ends with the example input producing the expected output from one command.
