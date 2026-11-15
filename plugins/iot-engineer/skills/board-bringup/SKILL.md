---
name: board-bringup
description: First power-on and bring-up of a new or unknown board (/iot-engineer:board-bringup) — safe power checks, getting a serial log, flashing, then proving each peripheral one at a time with minimal tests. Use for a fresh custom PCB, a new devkit model, or a board whose pins are not yet confirmed.
argument-hint: "[board]"
---

References: `${CLAUDE_PLUGIN_ROOT}/references/` — `chips.md`, `debugging.md`, `gotchas.md`, `electronics-fundamentals.md` (§ bench tools).

Give the owner one numbered step at a time with the expected result; record each result in `tests/BENCH_LOG.md`. Stop at the first failure and switch to `iot-engineer:debug`.

## 0. Before power
- Visual: solder bridges, missing/rotated parts (diodes, electrolytics, IC pin 1), flux residue.
- Multimeter, unpowered: resistance from each rail to ground is not a short (a few ohms = stop); continuity of ground between connectors.

## 1. First power
- Bench supply with the current limit at ~100 mA (or a USB port through a USB power meter). Current far above expectation or a hot part → power off.
- Measure every rail at its test point: within ±5 %. Check EN/reset is high.

## 2. Is the MCU alive?
- Connect USB/UART. ESP32: the ROM prints a boot message at 115200 baud on UART0 (74880 on ESP8266) even with empty flash. Nothing → check EN, 3.3 V at the module, TX/RX crossed, the right COM port, a cable that carries data.
- Read identity: `python -m esptool chip_id` and `flash_id` → confirms chip, flash size, and that download mode works. No BOOT button → hold the boot pin low during reset, or DTR/RTS wiring; if download mode is unusable, plan serial OTA.

## 3. First firmware
- Flash a minimal app: log line every second + blink. Confirms flash, clock, console pin and LED polarity.
- Print reset reason and free heap at boot — keep this in every later build.

## 4. One peripheral at a time (tiny test each)
| Peripheral | Minimal proof |
|---|---|
| LED / relay outputs | toggle each; confirm active level |
| Buttons / digital inputs | print level changes; poll ≤10 ms; unknown pin → sweep GPIOs |
| I2C | bus scan lists the expected addresses |
| SPI device | read its ID/version register at 1–4 MHz |
| UART / RS-485 | loopback, then a USB adapter on the other end; then a simulator |
| ADC | known voltage → expected counts; check divider ratio |
| Wi-Fi | scan shows networks with sane RSSI; then connect + get IP |
| Ethernet | link up, DHCP lease, ping for 5 minutes |
| Radio (LoRa etc.) | chip version register, then TX/RX with a second unit at close range |
| Flash/FS/NVS | write, reboot, read back |
| Sleep | measure current in sleep against the budget |

Unconfirmed pins stay "Not configured" in firmware and in `docs/WIRING.md` until proven here.

## 5. Together, then soak
Enable everything; watch for brownouts when the radio transmits or relays switch. Run the soak script for hours with serial capture (no reset on port open). Log heap over time.

## 6. Close out
Update `docs/WIRING.md` evidence column to "confirmed on board", clear `tests/PENDING.md` rows, write faults and reworks into `hardware/ERRATA.md`, add new root causes to `gotchas.md`.

**Knowledge base:** if `~/.claude/workspace-registry.txt` exists, first look up the owner's hardware, installed tools, preferences and past lessons in `<that path>/knowledge/` (start at `INDEX.md`) with one haiku agent, ask only what is missing, never reinstall what the registry shows as installed, and write new facts back with `shreyas-workspace-replicate:kb`.
