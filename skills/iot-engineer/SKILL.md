---
name: iot-engineer
description: Shreyas's method for electronics, embedded and IoT work (/iot-engineer). ESP32 / ESP-IDF first, any hardware in general. Use to start a firmware project or a full reusable ESP-IDF component stack from scratch, to continue one, to produce wiring tables for devkits, and to debug hardware, buses and protocols (RS-485, Modbus, BACnet, MQTT/TLS, Wi-Fi, Ethernet W5500, LoRa, cellular, OTA, NVS, I2C, SPI). Use whenever the user is stuck on hardware, says "hardware guy", or works on an ESP32, sensor, PCB, devkit or industrial protocol.
argument-hint: "[what you are building or what is broken]"
---

# /iot-engineer

Pick the mode from the request, then load only the reference that mode names.

| Mode | When | Load |
|---|---|---|
| **Start** | new firmware, new stack, new board | `references/esp-idf-stack.md` |
| **Continue** | add a module/feature to an existing project | the project's `AGENTS.md`/`HANDOFF.md` first, then `references/esp-idf-stack.md` if it follows this pattern |
| **Debug** | something does not work | `references/debugging.md`, then search `references/gotchas.md` for the symptom |
| **Wire** | owner needs to connect parts | the Wiring table section below |

Non-ESP hardware (Pi, STM32, Rust targets, Arduino): the method, debugging and
wiring sections apply unchanged; skip the ESP-IDF specifics.

## Ground rules (always)

1. **Words mean evidence.** "Built" = compiles. "Host-tested" = logic tests pass on the PC. "Works" = seen on the real board. Never say "works" for the first two. Every claim that needs a board gets a row in `tests/PENDING.md`.
2. **You cannot see the bench.** Ask the owner for exactly one observation at a time (a log, a meter reading, an LED), and say what each outcome will mean before they look.
3. **Pins come from evidence**, never from memory or a similar board: schematic, datasheet, working old firmware, or confirmed on the PCB. Unconfirmed pins are marked as such and the module stays compile-only.
4. **Only what was asked.** Reuse IDF built-ins and registry components before writing code. One module per protocol stack; products are glue.
5. **Do not flash unknown boards, burn eFuses, or enable Secure Boot / flash encryption** without the owner saying so in this conversation.
6. Do not commit or push unless asked. Before any commit, check `git diff --cached` for secrets, certificates and Wi-Fi passwords.

## Wiring table (devkit work)

Whenever parts must be connected, give this table before any code — the owner wires from it directly:

| Part pin (label on the part) | Devkit pin (label on the board) | GPIO | Wire | Note |
|---|---|---|---|---|
| MAX485 `RO` | `RX` / `18` | GPIO18 | yellow | UART1 RX |
| MAX485 `VCC` | `3V3` | — | red | 3.3 V only |

Rules:
- Use the labels printed on the silkscreen, plus the GPIO number.
- Always include power, ground, and every pull-up/termination/jumper. State the voltage of every part; flag any 5 V signal into a 3.3 V pin.
- Add an **Evidence** column for custom PCBs: schematic / old firmware / confirmed on PCB / unconfirmed.
- List pins to avoid for that chip under the table. ESP32-S3: 0, 3, 45, 46 (strapping); 19, 20 (native USB); 26–32 (flash); 33–37 (octal PSRAM on R8 modules); 43, 44 (console UART).
- Save it as `docs/WIRING.md` and keep it equal to the pin config in the code (Kconfig / `sdkconfig.defaults`). One changes → both change.
- End with a 3-step power-on check: what to measure or see before trusting the wiring.

## Start mode — order of work

1. **Requirements:** if the project was not started with `/new-project`, ask its IoT question set (board, parts on the desk, buses, connectivity, power, config method, OTA, time, fleet size, bench gear). No code until these are known.
2. **Bring-up ladder** — each rung proven on the board before the next:
   blink + serial log → each peripheral alone (a tiny test app per bus) → storage and config → network link → protocol against a simulator → protocol against the real device → the product glue → soak test.
3. **Structure** (`references/esp-idf-stack.md`): header first as the documentation; pure logic in files with no IDF includes so it can be host-tested; everything tunable in Kconfig; a `buildcheck` app that references every module and must always build clean.
4. **Docs created on day one:** `AGENTS.md` (how to assemble a product from the modules), `HANDOFF.md`, `docs/WIRING.md`, `docs/NVS.md` (key layout), `tests/PENDING.md` (hardware checks owed), `tests/BENCH_LOG.md` (dated results and root causes).

## Orchestration — good firmware for few tokens

You (the main model) own: module boundaries and public headers, pin and partition decisions, concurrency/ownership rules, root-cause analysis, and review of every diff. Delegate the rest:

| Work | Give to |
|---|---|
| Find where something is; run a build and return the first real error; summarise a long serial log; grep a datasheet/PDF for a register or pin | haiku (`scout`) |
| Implement one module's `.c` from a header you wrote; write host tests for a pure-logic file; write a simulator or bench script; a web page for an existing API | sonnet (`builder`) |
| Kconfig menus, CMakeLists, doc tables, README, boilerplate from a pattern that already exists in the repo | free tier (`opencode run -m opencode/big-pickle --auto`) or haiku — **personal projects only** |
| Module docs, `HANDOFF.md`, `PENDING.md` rows | haiku (`scribe`) — then verify identifiers by grep and read the prose once |

Rules that keep quality up:
- **Header-first contract:** you write `include/<mod>.h` with full comments; the subagent implements against it and may not change it.
- **One writer per component folder.** Independent modules build in parallel; shared files (`sdkconfig.defaults`, top `CMakeLists.txt`, `AGENTS.md`) are edited only by you.
- **The build is the judge:** after every delegated change, run the filtered build and host tests yourself. Builds take 3–5 minutes — run them in the background with a 15-minute timeout and batch several module changes per build.
- **Brief format:** Goal / Files / Context (header, the 3–8 facts, the existing module to copy the pattern from) / Check (build command + test) / Report ≤150 words.
- Fails twice at one tier → escalate one tier with the error output. Never loop a cheap model on a hardware bug: hardware bugs are yours, with the owner's observations.
- Client or employer firmware never goes to free models.

## Checkpoints with the owner

Stop and ask only when you need hands or eyes: wiring, flashing, a measurement, a visual check, a real device on the bus. Batch them: give one numbered bench list (what to do → what to report) at the end of a sprint, not one question per task. Record each result in `tests/BENCH_LOG.md` and clear or update the `PENDING.md` row.

## After the session

New root cause found? Add one line (symptom → cause → fix) to `references/gotchas.md` in the skills repo. That file is the memory that makes the next build faster.
