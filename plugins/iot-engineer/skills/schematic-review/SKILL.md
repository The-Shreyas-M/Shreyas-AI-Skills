---
name: schematic-review
description: Read and review a schematic or PCB design (/iot-engineer:schematic-review) — extract the real pin map, find design errors before ordering, or decide whether a fault is hardware or firmware. Works from KiCad files, netlists, PDFs or images. Use when given a schematic, when pins must be confirmed for firmware, or before sending a board to fabrication.
argument-hint: "[path to schematic or what to check]"
---

References: `${CLAUDE_PLUGIN_ROOT}/references/` — `chips.md` (pin rules), `electronics-fundamentals.md` (§ reading a schematic, protection), `protocols.md`.

## Input handling
- Text formats first: `.kicad_sch`, netlist, BOM CSV — grep by net and designator; do not read the whole file into context. A haiku agent can extract "every net connected to U1" as a table.
- PDF/image: needs a vision-capable model. Read one sheet at a time; quote the net label and designator for every claim. If a label is unreadable, say so — never guess a pin.
- Always get the datasheets of the MCU/module and each IC whose pins matter (pinout page + absolute maximum table only).

## Job A — pin map for firmware
Trace each signal from connector → protection → IC → MCU pin. Output:

| Function | MCU pin / GPIO | Via (parts on the path) | Active level | Evidence (sheet, net, designator) | Confidence |
|---|---|---|---|---|---|

Include: UART pairs per port (and whether TX/RX are crossed on the board), DE/RE control or auto-direction, I2C bus and pull-ups, SPI bus + each CS/RST/INT/BUSY, LEDs and buttons with polarity, relay/driver polarity (a transistor inverts), power-enable pins, ADC dividers with their ratio. Anything not traceable = "unconfirmed" and stays unconfigured in firmware.

## Job B — design review (report findings by severity)

**Will not work**
- Supply: regulator current vs peak load; dropout; missing input/output capacitors; no decoupling at an IC; rails not actually connected (label typo, missing power flag).
- MCU: EN/reset circuit missing; strapping pins loaded or tied wrong; flash/PSRAM/USB pins reused; input-only pin used as output; no way to program it (no USB, no header, no boot button).
- Buses: TX wired to TX; I2C without pull-ups or with 5 V pull-ups on a 3.3 V MCU; SPI CS shared; RS-485 A/B or DE polarity wrong; address conflicts.
- Levels: 5 V signal into a 3.3 V pin; logic-level mismatch on a MOSFET gate (V_GS(th) too high for 3.3 V drive).
- Footprint/pinout: regulator or transistor pin order vs the chosen part; connector mirrored; pin 1 marks.

**Will work badly or die early**
- No flyback diode on inductive loads; relay coil driven from a GPIO; no gate pulldown.
- No protection on external lines (TVS, series resistor, fuse, reverse polarity).
- Antenna boxed in by copper or placed mid-board; crystal far from the chip.
- Switching regulator layout loop large; analog input unfiltered next to a noisy trace.
- Mains: insufficient isolation distance, no fuse, no varistor.
- Thermal: LDO dissipating (Vin−Vout)×I above about 0.5–1 W without copper area.

**Makes life hard**
- No test points on rails/UART/EN/BOOT; no power LED; unlabelled headers; no revision marking; no spare GPIO broken out; parts with no stock or a single source.

For each finding: where (sheet/designator/net), why it matters, the fix. End with a verdict: order / fix first, and the list of things you could not verify.

## Job C — hardware or firmware?
From the symptom, name the nets involved, what a correct board would measure at which test point, and one measurement that separates the two (e.g. "3.3 V on EN and a 115200-baud boot message on TX0 → hardware is alive; look at firmware"). Then continue in `iot-engineer:debug`.

Independent review rule: the reviewer must not be the session that designed the board. Run this as a fresh subagent on a capable model with only the files and this skill.
