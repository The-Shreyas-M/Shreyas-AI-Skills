---
name: start
description: Front door for any electronics, embedded or IoT work (/iot-engineer:start). Pins down the exact chip and board, picks the right sub-skill (prototype, breadboard, PCB, schematic review, ESP-IDF or Arduino firmware, bring-up, debug) and applies the ground rules and cheap-subagent orchestration. Use whenever the user works on an ESP32, Arduino, sensor, devkit, PCB or industrial protocol, is stuck on hardware, or says "hardware guy".
argument-hint: "[what you are building or what is broken]"
---

Plugin root: `${CLAUDE_PLUGIN_ROOT}` — references live in `${CLAUDE_PLUGIN_ROOT}/references/`.

## 1. Know the hardware first (chip intake)

**Knowledge base first.** If `~/.claude/workspace-registry.txt` exists, the owner's private knowledge base is at `<that path>/knowledge/` (`INDEX.md` maps it). Before asking anything below, answer these yourself with Grep (targeted terms, no agent spawn) from `hardware-inventory.md`, `domains/iot.md`, `workspace.md`, `lessons.md` and the tool registry: which of these intake items are on record, which boards/parts/bench gear the owner has, which toolchains are installed (confirm with `--version`), and any past lesson about this chip or protocol. Use what it finds, show it as "on record — correct me if wrong", ask only the gaps, and write new facts back (`shreyas-workspace-replicate:kb`; newly bought parts go to `hardware-inventory.md`). Every `iot-engineer` sub-skill follows this rule.

Never design, wire or debug against a guessed part. If any of these is unknown after that, ask (one round) or read it from the board — details and commands in `references/chips.md`:

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
| Implement one module from a header you wrote; host tests; simulators and bench scripts; a web page for an existing API; Kconfig menus, CMake files, doc tables, boilerplate | **free model via `opencode run`** with an exact brief (the default writer on personal projects; command and brief format in the project's `docs/WORKFLOW.md`). Sonnet only after opencode fails its ladder, or on client/employer code |
| A lookup, a one-line fix, running a build and reading the filtered output, a doc row | yourself — never an agent spawn |
| Summarise a long serial log; pull a pin table, register or timing value from a long datasheet; list where something is used | short → yourself with grep; long → `opencode run` with a read-only brief. Not a Claude agent |
| Judging a photo of a board, a scope shot or a schematic image | yourself — look at the image directly. Many images (10+) → a free model that passed a vision probe (`opencode/beam-free` has vision) |
| Docs: `HANDOFF.md`, `WIRING.md`, `PENDING.md`, `TOOLCHAIN.md` | small edits yourself; bulk writing via `opencode run` — then grep identifiers and read the prose once |

Every Claude subagent spawn (haiku or sonnet) costs 60k+ tokens of the owner's plan however small the job; `opencode run` costs none. So: opencode writes, you brief and verify, Claude subagents are the exception.

**When an agent pays off.** A Claude subagent costs 60k+ tokens just to start, so it saves tokens only when the job would otherwise put more than about that much into your own context (which you then re-read on every later turn) *and* a free model cannot do it. Everything smaller you do yourself: send command output to a file and grep it, read only the lines you need. Writing and long reading go to `opencode run`.

- **Header-first contract:** you write the public header with full comments; the subagent implements against it and may not change it.
- **One writer per component folder.** Shared files (`sdkconfig.defaults`, top-level CMake, `AGENTS.md`) are edited only by you.
- **The build is the judge:** run the filtered build and host tests yourself after delegated changes. Firmware builds take minutes — background them and batch changes.
- **Brief:** Goal / Files / Context (header, 3–8 facts, an existing module to copy) / Check / Report ≤150 words.
- Fails twice at a tier → escalate with the error output. Hardware root causes are never delegated to a cheap model.
- Client or employer designs and firmware never go to free models.

## 5. Checkpoints and memory

- Stop for the owner only for hands or eyes: wiring, flashing, measuring, looking. Batch into one numbered bench list (do → report) per sprint; log results in `tests/BENCH_LOG.md`.
- New root cause found → add one line (symptom → cause → fix) to this plugin's `references/gotchas.md` in the local clone of the skills repo (`claude plugin marketplace list` shows its path) and push it.
- New tool or toolchain installed → log it (`shreyas-workspace-replicate:log-tool`).

**Workers:** "delegate" and "subagent" in this plugin mean `opencode run` through the Bash tool (default model `opencode/beam-free`, which also has vision), with the exact brief and tested command from the project `docs/WORKFLOW.md`. Do not call the Agent tool for hardware projects that are personal; the owner invoking this skill is the request to delegate to free models. Work that needs your own tools (viewing a board photo, the browser for a datasheet site) you do yourself; flashing and anything that can damage hardware is reviewed by you and is a checkpoint.
