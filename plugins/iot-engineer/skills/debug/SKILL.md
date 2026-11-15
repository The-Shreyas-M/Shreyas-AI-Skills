---
name: debug
description: Find and fix hardware, firmware and protocol faults fast (/iot-engineer:debug) — symptom lookup, power-and-wiring first, split the system in half, one-variable experiments, sniffers and simulators, like-for-like comparison. Covers boot loops, brownouts, dead buses, RS-485/Modbus/BACnet, Wi-Fi/Ethernet/MQTT/TLS, OTA and flashing. Use whenever something on a board does not work or behaves intermittently.
argument-hint: "[symptom]"
---

References in `${CLAUDE_PLUGIN_ROOT}/references/`: `debugging.md` (the full method and bench techniques), `gotchas.md` (known symptom → cause → fix), `protocols.md` (per-bus failure checks), `electronics-fundamentals.md`, `chips.md`.

## Do this, in order
1. Get the **raw evidence**: exact log lines, what was expected, what changed last, the exact chip/board (chip intake in `iot-engineer:start`).
2. **Grep `gotchas.md`** for the symptom words and the peripheral name. A hit saves the session.
3. Use the fast table below for the first check. Then follow `debugging.md` for the method.
4. One hypothesis, one experiment, expected outcomes stated before the owner runs it. Log in `tests/BENCH_LOG.md`.
5. After the fix: add a guard (counter, log, build check, host test) and one line to `gotchas.md`.

Two failed hypotheses → stop guessing; list proven vs assumed; choose the cheapest experiment that splits the remaining causes. Root-cause reasoning is never delegated to a cheap model.

## Fast fault table — symptom → likely causes → first check

| Symptom | Likely causes (most common first) | First check |
|---|---|---|
| Nothing on serial | wrong port/baud, charge-only cable, TX/RX not crossed, EN held low, no 3.3 V | port list, another cable, measure 3V3 and EN |
| Garbage characters | baud mismatch (ESP8266 boot = 74880), wrong crystal setting, no common ground | try 115200/74880; check ground |
| Boot loop, `rst:0x…` repeating | brownout, strapping pin pulled wrong, flash mode/size wrong, panic at start | read the reset reason line; disconnect all peripherals and retry |
| `Brownout detector was triggered` | weak USB port/cable, regulator too small, no bulk capacitor, load on 3V3 | power from a better supply; add 470 µF at 3V3; measure rail during Wi-Fi TX |
| `Guru Meditation` / panic | null pointer, stack overflow, ISR doing too much, heap exhausted | decode the backtrace (`idf.py monitor` does it); check stack high-water marks and free heap |
| Task watchdog fired | a task loops without yielding, a driver stuck waiting on dead hardware | which task is named in the log; add a timeout to the blocking call |
| Cannot flash / "Failed to connect" | not in download mode, wrong port, cable, GPIO0/boot path, another program holds the port | hold BOOT, tap EN; close serial monitors; lower baud |
| Flashed but old code runs | otadata points at the other slot; wrong app flashed | flash the full image set; print the version string at boot |
| I2C device not found | wiring SDA/SCL swapped, no pull-ups, wrong address, part unpowered, 5 V part | bus scan; measure SDA/SCL idle = 3.3 V |
| SPI device returns 0x00/0xFF | CS not toggling, MISO/MOSI swapped, mode/speed wrong, other device's CS floating | read the ID register at 1 MHz; hold other CS lines high |
| Sensor values noisy or wrong | floating input, no ground reference, ADC non-linearity/attenuation, wrong divider, supply noise | measure at the pin with a meter; average; check divider math |
| GPIO output does nothing | pin is input-only/strapping/used by flash-PSRAM-USB, wrong active level, load draws too much | toggle and measure at the MCU pin with the load removed |
| Relay chatters / board resets when a load switches | no flyback diode, shared supply sag, ground bounce | separate supply for the load, diode, bulk capacitor |
| RS-485: no reply | A/B swapped, baud/parity, wrong slave id, DE not driven, no ground reference, termination | passive sniffer on the bus: is the request there? is a reply there? |
| RS-485: some replies | inter-frame gap too short, timeout too short, noise/termination, two masters | sweep the gap/timeout and record success rate |
| Modbus exception 02 / wrong values | wrong register address (0- vs 1-based, 4xxxx offset), wrong function code, word order | read one known register with a PC tool, compare |
| Wi-Fi will not connect | wrong credentials, 5 GHz-only AP, weak signal, WPA3/enterprise, MAC filtering | scan: is the SSID seen and at what RSSI; try a phone hotspot |
| Wi-Fi connects, no IP / drops | DHCP blocked, power save, AP steering, antenna | DHCP trace; disable power save; hotspot comparison |
| MQTT/TLS fails | clock not set, wrong CA/cert SAN, port blocked, client id clash, broker ACL | print time; test the broker from a PC with the same certs |
| Ethernet no link / dead after minutes | PHY reset/clock, SPI routing, INT line, driver RX fault | read the PHY/chip ID; poll instead of INT; soak with ping |
| OTA fails or bricks | partition too small, wrong image type, power loss, no rollback handling | compare image size vs slot; check partition table; test on a spare unit |
| Works on the desk, fails in the field | supply noise, long cables, EMI from relays/VFDs, heat, network policy | reproduce with the field supply/cable; add logging of resets and RSSI |
| Works on devkit, fails on custom PCB | pin differences, missing pull-ups/caps, PSRAM/flash variant, antenna | `iot-engineer:schematic-review` Job A, then same firmware on both |
| Gets slower / crashes after hours | heap leak or fragmentation, handle leak, log flood | log free heap + largest block every minute; soak test |

## Asking the owner
One numbered action at a time, with the two pins/points named, the expected reading, and what each result means. Never "check the wiring".

## Delegation while debugging
- Haiku: condense a long log (first error, repeated lines with counts, reset timestamps); find a value in a datasheet; grep a vendor driver for where an error string comes from.
- Sonnet: write the simulator, sniffer or soak script from your spec.
- Images (board photo, scope shot) → vision-capable model only.

**Knowledge base:** if `~/.claude/workspace-registry.txt` exists, first look up the owner's hardware, installed tools, preferences and past lessons in `<that path>/knowledge/` (start at `INDEX.md`) yourself with Grep (no agent spawn), ask only what is missing, never reinstall what the registry shows as installed, and write new facts back with `shreyas-workspace-replicate:kb`.
