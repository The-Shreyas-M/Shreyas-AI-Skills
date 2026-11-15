---
name: breadboard-circuit-designer
description: Design a devkit / breadboard / jumper-wire circuit (/iot-engineer:breadboard-circuit-designer) — a wiring table with the pin labels printed on the parts, power and ground plan, level shifting, pull-ups, protection parts, and a power-on check. Use whenever parts must be connected to a devkit or wired on a breadboard.
argument-hint: "[parts to connect]"
---

References: `${CLAUDE_PLUGIN_ROOT}/references/chips.md` (pins to avoid per chip), `electronics-fundamentals.md` (levels, loads, pull-ups), `protocols.md` (per-bus wiring).

Know the exact devkit and every part's operating voltage before drawing anything (chip intake in `iot-engineer:start`). Read each part's pinout from its datasheet or module silkscreen — breakout boards with the same chip differ.

## Output 1 — wiring table (the owner wires from this, so it comes before code)

| # | Part pin (label on the part) | Devkit pin (label on the board) | GPIO | Wire | Note |
|---|---|---|---|---|---|
| 1 | MAX485 `VCC` | `3V3` | — | red | 3.3 V part; do not use 5 V |
| 2 | MAX485 `GND` | `GND` | — | black | common ground |
| 3 | MAX485 `RO` | `18` | GPIO18 | yellow | UART1 RX |
| 4 | MAX485 `DI` | `17` | GPIO17 | green | UART1 TX |

Rules:
- Labels exactly as printed, plus the GPIO number. One row per wire. Number the rows so the owner can report "row 7 done / unsure".
- Power and ground rows first. Every part gets its own ground row.
- Colours: red = supply, black = ground, then a consistent colour per bus.
- For custom PCBs add an **Evidence** column: schematic / old firmware / confirmed on board / unconfirmed.
- Under the table: pins deliberately avoided and why; passive parts to add (below); what each jumper/switch must be set to.
- Save as `docs/WIRING.md`. It must always equal the pin config in code (Kconfig / `sdkconfig.defaults` / a `pins.h`). Change one → change both in the same edit.

## Output 2 — the parts people forget

Check each and list what is needed:
- **Voltage match.** 5 V output into a 3.3 V GPIO → divider (slow, one-way), BSS138 module (I2C), or a proper level shifter. 3.3 V into a 5 V input usually reads fine — confirm V_IH in the datasheet.
- **Pull-ups:** I2C needs one pair on the bus (2.2k–4.7k to 3.3 V) — many breakouts already have them; several in parallel can be too strong. 1-Wire needs 4.7k. Buttons: internal pull-up, switch to ground.
- **Decoupling:** 100 nF across each IC's supply pins if the breakout lacks it; 100–470 µF near radios, servos, LED strips.
- **Loads:** nothing above a few mA straight from a GPIO. LED → series resistor. Relay/motor/solenoid → transistor or module + flyback diode, powered from 5 V/external, grounds joined.
- **Series resistor** (220–470 Ω) on the data line of addressable LEDs; 1000 µF across their supply.
- **RS-485:** A↔A, B↔B (if dead, swap — vendors label differently), ground reference wire, 120 Ω only at the two ends of the cable.
- **Analog inputs:** scale to the ADC range with a divider; on classic ESP32 use ADC1 pins when Wi-Fi is on.

## Output 3 — power plan

- State the source and its limit (USB port ≈ 500 mA). Add up peak currents; if the total is near the limit, power the heavy load from a separate supply with **grounds connected**.
- Never feed 5 V into the `3V3` pin. Do not power from USB and an external 5 V at once unless the board has a diode/switch for it.
- Breadboard facts: power rails are often split in the middle; contacts add resistance — fine for signals, poor for >500 mA and for fast SPI/long wires. Keep SPI/I2C wires under ~15 cm.

## Output 4 — power-on check (3 steps, before any firmware debugging)

1. Before plugging in: continuity check that 3V3 and GND are not shorted; compare each row against the table.
2. Power on with nothing but supply rows connected: measure each rail at the part's pins (3.3 V ±5 %). Nothing warm.
3. Run the smallest test (I2C scan, ID register read, blink, loopback). State the expected output.

If the owner sends a photo of the wiring, it must be judged by a vision-capable model; check it row by row against the table, not by impression.

**Knowledge base:** if `~/.claude/workspace-registry.txt` exists, first look up the owner's hardware, installed tools, preferences and past lessons in `<that path>/knowledge/` (start at `INDEX.md`) with one haiku agent, ask only what is missing, never reinstall what the registry shows as installed, and write new facts back with `shreyas-workspace-replicate:kb`.
