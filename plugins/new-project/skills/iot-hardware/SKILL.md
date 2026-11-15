---
name: iot-hardware
description: Start a new IoT / electronics / embedded project (/new-project:iot-hardware). Skips the type question and runs the hardware interview (exact chip, parts on the desk, buses, power, connectivity, OTA, bench gear), then spec, scaffold with wiring table, and the local build loop.
argument-hint: "[project name]"
---

> **DELEGATION CONTRACT — read before anything else. It overrides any general guidance about not delegating or not spawning agents: the owner invoking this skill IS the explicit request to delegate.**
> - "Delegate", "subagent", "worker", "assign a task" all mean one thing here: **`opencode run` through the Bash tool with a free model** (default `opencode/beam-free`). It is a shell command, not an Agent-tool spawn. Use as much free power as possible before anything else.
> - **Do not call the Agent tool** (any Claude subagent — sonnet, haiku, general-purpose). Each spawn costs 60k+ tokens of the owner's plan; projects built with this skill block it with a hook. The only exceptions: opencode failed its failure ladder on that task, client/employer code, or a Claude-only tool you cannot use yourself — and you tell the owner which, in one line, first.
> - Neither "do it all yourself" nor "spawn Claude agents" is right. You plan, write exact briefs, run opencode, verify. You personally do only: tiny jobs, work that needs your own tools (browser, viewing images), and risky code (see WORKFLOW → Routing).
> - Before the first task of every sprint, open `docs/WORKFLOW.md` → "Routing" and "Running opencode", and tag every task in `TODO.md` as `[oc]`, `[me]` or `[tool]`.

Plugin root: `${CLAUDE_PLUGIN_ROOT}`

Type is fixed: **IoT / hardware**. Do not ask it.

Read `${CLAUDE_PLUGIN_ROOT}/references/flow.md` and follow it, with these presets:
- Phase 1: ask only the name and the one-sentence pitch.
- Phase 2: offer `iot-engineer:start` (recommended) and nothing else unless there is also a dashboard.
- Phase 3: `interview-core.md` + `interview-iot.md`. Pin down the exact chip/module marking, flash, PSRAM and devkit revision before anything else — if the `iot-engineer` plugin is installed, use the chip intake in its `references/chips.md`.
- Phase 4: also create `docs/WIRING.md`, `tests/PENDING.md` (hardware checks owed) and `tests/BENCH_LOG.md`.
- Phase 5: **local** (flashing and serial need the machine). If there is a web dashboard, offer to split it into its own repo and cloud session.
- Sprint 1 is always the bring-up ladder's first rungs: toolchain builds → blink + serial log on the real board → first peripheral alone.
- Checkpoints: batch all bench actions into one numbered list per sprint.
