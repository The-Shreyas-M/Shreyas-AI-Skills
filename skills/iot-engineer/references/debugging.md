# Debugging hardware — the method

## The order (do not skip rungs)

1. **Write the symptom exactly:** what was expected, what happened, since when, what changed last. Get the raw log, not a description of it.
2. **Search `gotchas.md`** for the symptom. Many "new" bugs are old ones.
3. **Power and wiring first.** Voltage at the part's pins under load, common ground, TX↔RX crossed, A/B polarity, termination, pull-ups, antenna attached. Compare against `docs/WIRING.md` pin by pin.
4. **Split the system in half.** Find the last point where the signal is right. Layers: power → pins → bus/peripheral driver → link → protocol → application → cloud. Test one layer alone.
5. **One variable per experiment.** State the hypothesis and what each outcome means *before* the owner runs it. Write the result in `tests/BENCH_LOG.md`.
6. **Measure, do not guess.** Sweep the parameter (baud, gap, SPI clock, timeout) and record the success rate per value.
7. **Like-for-like comparison.** Same firmware image on a known-good devkit; same board with a known-good firmware. Do not blame the PCB or the code until one of these differs.
8. **Fix the cause, then add the guard:** a counter, a log line, a build-time check or a host test so it cannot return silently. Add the line to `gotchas.md`.

Two failed hypotheses in a row → stop, list what is *proven* versus assumed, and pick the cheapest experiment that separates the remaining causes.

## Techniques that worked

**Serial buses (RS-485 / Modbus / BACnet MS-TP)**
- **Daisy-chain a USB-RS485 adapter onto the same bus** as a passive sniffer. It is the ground truth for two questions: is the master asking, and is the slave answering? This separates firmware, wiring and device in one look.
- Run a **slave simulator** on that adapter (pymodbus 3.6.x) with a register map that matches the device config. It must not answer the ids of real slaves on the bus. A read past the simulated block gets no reply — that looks like a flaky slave but is the simulator.
- Then swap the simulator for the real device. If the simulator works and the device does not: timing (inter-frame gap), address, baud/parity, word order.
- Check there is no echo of your own frames and no CRC errors in the counters (auto-direction transceivers need no DE pin).
- Scale test: many simulated slaves with a control file to silence chosen ids, to see how offline devices affect the rest.

**SPI / I2C parts**
- Read a known ID/version register first. Wrong value → wiring, CS, clock speed or pin routing, not the driver.
- Bit-bang one register read on plain GPIO to separate wiring from the peripheral driver.
- Lower the clock (1–4 MHz SPI, 100 kHz I2C) before anything else. I2C: scan the bus, check pull-ups.
- Shared SPI bus: hold every other chip's CS (and RESET) high before the bus starts.

**Pins and boards**
- Unknown button pin → sweep GPIOs and print changes; poll at ≤10 ms (a loop with a 1 s delay misses taps).
- Unknown LED polarity → blink test both levels.
- No BOOT button → DTR on the GPIO0 header pin; download mode broken → serial OTA over the console.
- COM port numbers change per plug-in; "Unknown device" in Device Manager usually means a cable or power fault.

**Network**
- Bisect with one change at a time: AP off, power save off, 20 MHz, 11b-only, Ethernet compiled out.
- Trace DHCP in lwIP (DISCOVER sent? OFFER received?) before blaming the application.
- Suspect the network itself: campus/office networks block unregistered devices and ports. Reproduce on a phone hotspot and with a broker on the laptop (`sdkconfig.local`).
- TLS fails → check the clock first, then the certificate SANs.

**Soak and regression**
- A soak script that runs ping + HTTP + every protocol for several minutes while capturing serial **without resetting the board**. Intermittent faults only show here.
- Web UI: test against a mock `/api` server or headless browser; no board needed.
- Logic bugs: reproduce in a host test from the captured bytes, then fix.

## Asking the owner (they are your hands)

Give a numbered list; each item is one action and one thing to report:

```
1. Measure DC volts between module VCC and GND while it transmits. Report the number.
   ≥3.2 V → power is fine, go to 2.   <3.0 V → supply sag; add a capacitor / separate supply.
2. Run: python tools/console.py COM7 "status"   Paste the output.
```

Never ask for "check the wiring". Name the two pins and the expected reading.

## Delegation while debugging

- Root-cause reasoning stays with the main model. Do not hand a hardware bug to a cheap model to "try things".
- Delegate: summarising a long serial log (first error, repeated lines with counts, timestamps of resets), finding a register/timing value in a datasheet, writing the simulator or soak script, grepping the vendor driver for where an error string is raised.
