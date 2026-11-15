---
name: pcb-designer
description: Design a custom PCB like a hardware designer (/iot-engineer:pcb-designer) using free tools — requirements, schematic with the standard support circuits, part and footprint choice, layout rules, checks, fabrication files and assembly order, then bring-up. KiCad first. Use when a prototype must become a board, or an existing board needs a new revision.
argument-hint: "[board to design]"
---

References: `${CLAUDE_PLUGIN_ROOT}/references/` — `chips.md`, `electronics-fundamentals.md`, `protocols.md`. Fab limits, part stock and tool versions change: check the fab's current capabilities page and the part's current datasheet instead of trusting remembered numbers.

**How you help:** you cannot click in a GUI, so you produce what the owner (or a script) turns into the design, and you check what comes back:
- a connection list per sheet (net name → every pin on it), a BOM with footprints, placement and routing instructions;
- review of exported files: KiCad `.kicad_sch` / `.kicad_pcb` are text and can be read; also netlist, BOM CSV, PDF/PNG plots (images need a vision-capable model);
- command-line checks where KiCad is installed: `kicad-cli sch erc`, `kicad-cli pcb drc`, `kicad-cli sch export pdf|netlist|bom`, `kicad-cli pcb export gerbers|drill|pos` (confirm flags with `kicad-cli --help`).

Free tools: **KiCad** (default, offline, no limits), EasyEDA (browser, tied to one fab's parts library). Prototype fabs take Gerber + drill; assembly needs BOM + position (CPL) files.

## Stage 0 — do not start a PCB until
The circuit works on a devkit/breadboard, the pin plan is frozen, and the power budget is measured (`iot-engineer:prototype-designer`). A PCB fixes nothing that is wrong in the prototype.

## Stage 1 — board requirements (ask)
Size and mounting holes, enclosure, connectors and their positions, supply range, environment, 2 or 4 layers (2 is enough for most MCU + sensor boards; 4 for dense, RF-sensitive or noisy designs), hand-soldered or fab-assembled (decides package sizes: 0805/SOIC by hand, 0402/QFN for assembly), quantity, programming method, test access.

## Stage 2 — schematic

One sheet per function: power, MCU, comms, I/O, connectors. Then give the connection list. Include these standard circuits — each one missing is a classic dead-board cause:

**Power**
- Input protection: fuse or polyfuse, reverse-polarity (series Schottky or P-FET), TVS on external supply lines.
- Regulator sized to peak + 30–50 %: buck for large drops or currents, LDO for small drops / low noise. Follow the datasheet's layout and capacitor values exactly (type and ESR matter).
- 3.3 V for an ESP32: ≥ 500–600 mA capability, 10–22 µF + 100 nF at the module supply pin.
- 100 nF at **every** IC supply pin; bulk capacitor per rail; a power LED; test points on every rail.

**ESP32 module (take exact values from the module datasheet and the vendor's hardware design guidelines)**
- `EN`: 10 k pull-up + 1 µF to ground (reset delay); reset button to ground.
- Boot/strapping pins at their required levels at reset; boot button on the boot pin (GPIO0 on most chips, GPIO9 on C3) — nothing else that can pull it wrong at power-on.
- Programming: native USB (S2/S3/C3/C6: D−/D+ straight to the USB pins, 5.1 k on each CC pin for USB-C) **or** a USB-UART bridge with the two-transistor DTR/RTS auto-program circuit; at minimum a header with 3V3, GND, TX, RX, EN, boot pin.
- Avoid: flash/PSRAM pins, strapping pins for anything that loads them, input-only pins for outputs, ADC2 with Wi-Fi on the classic ESP32.
- Antenna: module antenna at the board edge, pointing outward, with the copper keep-out the datasheet shows (all layers).

**Interfaces**
- USB: ESD protection diodes on D+/D−; shield via RC to ground.
- I2C: one pair of pull-ups. Buttons: pull-up + optional 100 nF. Every off-board signal: series resistor and/or TVS.
- RS-485: transceiver with fail-safe, 120 Ω termination and bias resistors via jumpers, TVS on A/B, ground terminal; isolated transceiver + isolated DC-DC for field buses that leave the cabinet.
- Relays/motors/solenoids: low-side N-FET or driver, gate pulldown, flyback diode; opto or isolated driver for mains switching; keep mains creepage/clearance and add slots where needed.
- Analog inputs: divider + RC filter + clamp; 4–20 mA via shunt.
- Crystal (if any): load capacitors from the crystal's CL; keep the loop tiny.

**Hygiene:** name every net that leaves a sheet; no unconnected pins without a no-connect flag; reference designators and values on everything; choose parts with real stock and note one alternate; mark DNP parts; add a revision and date in the title block. Run ERC to zero errors.

## Stage 3 — footprints
Assign from the manufacturer's datasheet land pattern, not by name similarity. Check pin 1, pin numbering (SOT-23 variants, regulators differ between vendors), connector orientation and pitch, and mechanical parts against a 1:1 printout or the 3D view.

## Stage 4 — layout (in this order)
1. Board outline, mounting holes, connectors and anything fixed by the enclosure.
2. MCU/module with the antenna at an edge. Then regulators near the input. Then each IC with its decoupling capacitor touching its supply pin.
3. Group by function; keep noisy (switching regulator, relays, motors) away from analog and RF.
4. Route in this order: critical short loops (buck converter hot loop, crystal), USB pair (matched, short, over solid ground), power traces, then signals.
5. Ground: a solid unbroken ground plane on one layer; stitch top-side ground with vias; never route a signal across a gap in the plane.

Starting numbers (confirm against the fab's limits): signal traces 0.2–0.25 mm; power 0.5 mm per amp as a floor (wider is free); clearance 0.2 mm; vias 0.3 mm hole / 0.6 mm pad; text ≥ 0.8 mm high. Mains: keep the clearance and creepage the applicable safety standard requires and isolate with slots.

Silkscreen that saves hours later: pin names on every header, polarity marks, board name + revision, test point labels (`3V3`, `GND`, `TX`, `RX`, `EN`, `BOOT`).

## Stage 5 — checks before ordering
- DRC with the fab's rule set: zero errors, no unrouted nets.
- **Print 1:1 and place the real parts on the paper.**
- Re-read against the schematic: every IC has decoupling; pull-ups present once; TX↔RX crossed where they should be; connector pinouts match the mating cable; polarised parts oriented; antenna keep-out clear; mounting holes clear of copper.
- Run `iot-engineer:schematic-review` as an independent pass (a fresh subagent on the main model, given only the files).
- Order 5–10 boards; first revision always has a bug — add test points and a few spare pads/0 Ω links so it can be patched.

## Stage 6 — outputs
Gerbers for all copper, mask, silk and edge layers + drill files (zip); BOM (designator, value, footprint, manufacturer part number); position file for assembly; PDF schematic; keep all of it under version control in `hardware/` with a `REV` note of changes.

## Stage 7 — after the boards arrive
Go to `iot-engineer:board-bringup`. Record every fault and rework in `hardware/ERRATA.md` — it is the input for revision B.

**Knowledge base:** if `~/.claude/workspace-registry.txt` exists, first look up the owner's hardware, installed tools, preferences and past lessons in `<that path>/knowledge/` (start at `INDEX.md`) with one haiku agent, ask only what is missing, never reinstall what the registry shows as installed, and write new facts back with `shreyas-workspace-replicate:kb`.
