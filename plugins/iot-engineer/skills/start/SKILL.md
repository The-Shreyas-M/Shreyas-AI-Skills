---
name: start
description: Front door for any electronics, embedded or IoT work (/iot-engineer:start). Pins down the exact chip and board, picks the right sub-skill (prototype, breadboard, PCB, schematic review, ESP-IDF or Arduino firmware, bring-up, debug) and applies the ground rules and cheap-subagent orchestration. Use whenever the user works on an ESP32, Arduino, sensor, devkit, PCB or industrial protocol, is stuck on hardware, or says "hardware guy".
argument-hint: "[what you are building or what is broken]"
---

Plugin root: `${CLAUDE_PLUGIN_ROOT}` — references live in `${CLAUDE_PLUGIN_ROOT}/references/`.

## 1. Know the hardware first (chip intake)

Never design, wire or debug against a guessed part. If any of these is unknown, ask (one round) or read it from the board — details and commands in `references/chips.md`:

- Exact module marking (e.g. `ESP32-S3-WROOM-1-N8R8`) → chip, flash MB, PSRAM MB and type, antenna.
- Board: devkit name and revision, or custom PCB (then: schematic available?).
- USB path: native USB or a bridge chip (CP210x / CH340), which port.
- Supply: USB, mains module, battery; regulator current.
- Every connected part with part number and operating voltage.
- Framework and version (ESP-IDF x.y / Arduino core / PlatformIO).
- What is on the bench: second devkit, USB-UART, USB-RS485, logic analyser, multimeter, bench supply.

Record the answers in the project's `docs/HARDWARE.md` (or SPEC §Hardware) so no session asks twice.

## 2. Route to the sub-skill

| The job | Use |
|---|---|
| Idea → block diagram, part selection, power budget, build plan | `iot-engineer:prototype-designer` |
| Connect parts on a devkit/breadboard: wiring table, levels, pull-ups | `iot-engineer:breadboard-circuit-designer` |
| Design a custom board: schematic, layout, fabrication files | `iot-engineer:pcb-designer` |
| Check someone's schematic or board before ordering or blaming firmware | `iot-engineer:schematic-review` |
| ESP-IDF firmware or a reusable component stack | `iot-engineer:firmware-esp-idf` |
| Arduino / PlatformIO firmware | `iot-engineer:firmware-arduino` |
| First power-on of a new board | `iot-engineer:board-bringup` |
| Something does not work | `iot-engineer:debug` |

Load one sub-skill at a time. Background knowledge is in `references/`: `electronics-fundamentals.md`, `protocols.md`, `chips.md`, `esp-idf-stack.md`, `debugging.md`, `gotchas.md` — read only the section the task needs.

## 3. Ground rules (every sub-skill)

1. **Words mean evidence.** "Built" = compiles. "Host-tested" = logic tests pass on the PC. "Works" = seen on the real board. Each claim that needs a board gets a row in `tests/PENDING.md`.
2. **You cannot see the bench.** Ask for one observation at a time and say what each outcome means before the owner looks.
3. **Pins and values come from evidence** — datasheet, schematic, working firmware, or confirmed on the board — never from memory of a similar part. Mark anything unconfirmed.
4. **Safety first:** mains voltage, lithium batteries and motors get an explicit warning and an isolated/fused design. Never tell the owner to probe live mains.
5. **Only what was asked.** Reuse framework built-ins and maintained libraries. One module per protocol; products are glue.
6. Do not flash unknown boards, burn eFuses or enable Secure Boot / flash encryption unless the owner says so now. Do not commit or push unless asked; check `git diff --cached` for secrets first.

## 4. Orchestration — good hardware work for few tokens

You (main model) own: architecture, module interfaces (public headers), pin/partition/power decisions, root-cause analysis, review of every diff and every design before it is ordered. Delegate the rest:

| Work | Give to |
|---|---|
| Find things in code; run a build and return the first real error; summarise a long serial log; pull a pin table, register or timing value from a datasheet PDF | haiku |
| Implement one module from a header you wrote; host tests; simulators and bench scripts; a web page for an existing API; BOM lookup of alternates | sonnet |
| Kconfig menus, CMake files, doc tables, boilerplate copied from an existing pattern | free model via `opencode run` (personal projects only; pick the model for the task) or haiku |
| Judging a photo of a board, a scope shot or a schematic image | a vision-capable model only (haiku or better; a free model only if it is a vision model) |
| Docs: `HANDOFF.md`, `WIRING.md`, `PENDING.md`, `TOOLCHAIN.md` | haiku — then grep identifiers and read the prose once |

- **Header-first contract:** you write the public header with full comments; the subagent implements against it and may not change it.
- **One writer per component folder.** Shared files (`sdkconfig.defaults`, top-level CMake, `AGENTS.md`) are edited only by you.
- **The build is the judge:** run the filtered build and host tests yourself after delegated changes. Firmware builds take minutes — background them and batch changes.
- **Brief:** Goal / Files / Context (header, 3–8 facts, an existing module to copy) / Check / Report ≤150 words.
- Fails twice at a tier → escalate with the error output. Hardware root causes are never delegated to a cheap model.
- Client or employer designs and firmware never go to free models.

## 5. Checkpoints and memory

- Stop for the owner only for hands or eyes: wiring, flashing, measuring, looking. Batch into one numbered bench list (do → report) per sprint; log results in `tests/BENCH_LOG.md`.
- New root cause found → add one line (symptom → cause → fix) to `references/gotchas.md` in the skills repo (path in `~/.claude/workspace-registry.txt`).
- New tool or toolchain installed → log it (`shreyas-workspace-replicate:log-tool`).
