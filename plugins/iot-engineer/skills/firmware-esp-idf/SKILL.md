---
name: firmware-esp-idf
description: ESP-IDF firmware (/iot-engineer:firmware-esp-idf) — start a project or a full reusable component stack from scratch, add modules to an existing one, set up build/flash/host-test tooling, storage, OTA and the docs that let smaller models assemble products. Use for any ESP32 work on ESP-IDF.
argument-hint: "[what to build or add]"
---

Read `${CLAUDE_PLUGIN_ROOT}/references/esp-idf-stack.md` — it is the full method (repo layout, architecture rules, component and app templates, storage/config/OTA, Windows build and flash commands, library per protocol, build order). Search `${CLAUDE_PLUGIN_ROOT}/references/gotchas.md` for every peripheral and protocol you are about to touch **before** writing code for it.

## Starting from nothing
1. Chip intake done (`iot-engineer:start`); requirements known (use `/new-project:iot-hardware` if not).
2. Confirm the toolchain: `idf.py --version`, target set (`idf.py set-target esp32s3`), a clean `hello_world` builds and flashes on this board. Log the toolchain version in `docs/TOOLCHAIN.md`.
3. Decide size: **single app** (one product, few modules → plain `main/` + `components/`) or **stack** (several products share modules → full layout in the reference). Do not build a stack for one small device.
4. Follow the reference's build order. Each step ends with: clean build, host tests pass, and a bench check listed in `tests/PENDING.md`.

## Adding to an existing project
Read its `AGENTS.md`/`HANDOFF.md` first; its rules win over this skill. Copy the pattern of the nearest existing module. Keep `buildcheck` (or the main app) building clean after every module.

## Always
- Header first, fully commented; pure logic in files without IDF includes + a host test; tunables in Kconfig; pins only in Kconfig/`sdkconfig.defaults` and mirrored in `docs/WIRING.md`.
- IDF APIs change between versions — check the installed version's headers or docs (`$IDF_PATH/components/...`) instead of remembered signatures; a haiku agent can look one up.
- Use the filtered build script; never paste full build logs into context.
- Say "built" / "host-tested" / "works on the board" precisely.
- Orchestration and delegation rules: `iot-engineer:start` §4.

**Knowledge base:** if `~/.claude/workspace-registry.txt` exists, first look up the owner's hardware, installed tools, preferences and past lessons in `<that path>/knowledge/` (start at `INDEX.md`) yourself with Grep (no agent spawn), ask only what is missing, never reinstall what the registry shows as installed, and write new facts back with `shreyas-workspace-replicate:kb`.
