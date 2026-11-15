---
name: iot-hardware
description: Start a new IoT / electronics / embedded project (/new-project:iot-hardware). Skips the type question and runs the hardware interview (exact chip, parts on the desk, buses, power, connectivity, OTA, bench gear), then spec, scaffold with wiring table, and the local build loop.
argument-hint: "[project name]"
---

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
