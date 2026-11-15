---
name: prototype-designer
description: Turn a hardware idea into a buildable prototype plan (/iot-engineer:prototype-designer) — requirements, block diagram, chip and part selection with reasons, power budget, pin plan, risk list, bill of materials and the order to build and prove it. Use before buying parts or writing firmware for a new device.
argument-hint: "[what the device should do]"
---

References: `${CLAUDE_PLUGIN_ROOT}/references/` — `chips.md` (chip choice, pin rules), `electronics-fundamentals.md` (power, levels, loads, sensors), `protocols.md` (bus choice).

Produce the sections below, in order, as `docs/PROTOTYPE.md`. Keep it to what this device needs.

## 1. Requirements (ask what is missing, one round)

- What it senses, controls, displays and reports — each with range, accuracy and how often.
- Where it lives: indoor/outdoor, temperature, enclosure, distance to router/gateway, cable lengths.
- Power available: USB, mains, battery (target life), PoE, solar.
- Connectivity: Wi-Fi, Ethernet, BLE, LoRa, cellular, RS-485/CAN to other equipment.
- Quantity (1, 10, 1000) and budget per unit. Deadline.
- What the owner already has on the desk — design around it when it fits.

## 2. Block diagram

Text diagram: power path, MCU, each peripheral with its bus and voltage, external connectors, isolation boundaries.

```
[12 V in]→[buck 5 V]→[LDO 3.3 V]→ MCU ──I2C── sensor (3.3 V)
                                   ├─UART─→ RS-485 xcvr ⇄ field bus (isolated?)
                                   └─GPIO─→ MOSFET → relay coil (5 V, flyback diode)
```

## 3. Part selection (table)

| Function | Part | Why this one | Voltage | Interface | Alternatives |
|---|---|---|---|---|---|

Rules:
- Choose the **MCU** from needs: radios, GPIO count after reserved pins, ADC channels, native USB, flash/PSRAM for OTA and TLS, sleep current (see `chips.md` "Picking a chip").
- Prefer parts that exist as breakout modules for the prototype **and** as bare ICs for a later PCB, with a maintained driver/library and stock at mainstream distributors.
- Prefer 3.3 V I2C/SPI digital sensors over analog ones; prefer parts the owner has used before.
- Anything touching mains, the outside world or long cables: pick the isolated / protected version now.

## 4. Power budget

| Rail | Consumer | Typical mA | Peak mA |
|---|---|---|---|

Sum the peaks, add 30–50 % margin, then choose the regulator. Radios and modems need bulk capacitance next to them (ESP32 Wi-Fi bursts, cellular 2 A peaks). For batteries: average current = Σ(current × duty); life = capacity × 0.8 / average. State the sleep strategy if life matters.

## 5. Pin plan

Assign every signal to a GPIO using the chip's rules (strapping, flash/PSRAM, USB, input-only, ADC with Wi-Fi). Output the wiring table format of `iot-engineer:breadboard-circuit-designer`. Leave UART0/USB free for logs. Note spare pins.

## 6. Risks and unknowns

List what could sink the design and the cheapest experiment that settles each (range test, sensor accuracy check, current measurement, library availability on this framework). The riskiest item is built first.

## 7. Build order

Bring-up ladder — each rung proven on the bench before the next:
1. Devkit alone: blink + serial log.
2. Each peripheral alone with a minimal test sketch/app.
3. Power from the real supply; measure rails under load.
4. Peripherals together; network link.
5. Protocol against a simulator, then the real equipment.
6. Product logic; then a soak test (hours).
7. Only then: enclosure and PCB (`iot-engineer:pcb-designer`).

## 8. Bill of materials

| Qty | Part | Value / part number | For | Have it? |
|---|---|---|---|---|

Include the small things: pull-ups, decoupling capacitors, flyback diodes, level shifters, terminal blocks, headers, wire, fuse.

End by asking the owner to confirm the part list before any firmware is written.
