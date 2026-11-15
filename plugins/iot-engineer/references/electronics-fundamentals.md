# Electronics fundamentals (bench reference)

Rule: when a value depends on the exact part, write "check datasheet". Never guess pinouts.

## 1. Units and the five daily formulas
| Quantity | Unit | Prefixes |
|---|---|---|
| Voltage V | volt | m = 1e-3, µ = 1e-6, n = 1e-9, p = 1e-12 |
| Current I | ampere | k = 1e3, M = 1e6 |
| Resistance R | ohm (Ω) | 4k7 = 4.7 kΩ, 2M2 = 2.2 MΩ |
| Power P | watt | 1 W = 1 V x 1 A |
| Capacitance C | farad | 100 nF = 0.1 µF = 100000 pF |
| Frequency f / period T | Hz / s | T = 1/f |

| # | Formula | Worked example at 3.3 V |
|---|---|---|
| 1 Ohm | V = I·R, I = V/R, R = V/I | 3.3 V across 1 kΩ -> 3.3 mA |
| 2 Power | P = V·I = I²·R = V²/R | 3.3 V across 330 Ω -> 10 mA, P = 33 mW (1/8 W resistor is fine) |
| 3 Divider | Vout = Vin·R2/(R1+R2) (R2 to GND) | 10k/10k from 3.3 V -> 1.65 V. 12 V -> 33k/10k -> 2.79 V |
| 4 RC | tau = R·C; 63 % after 1 tau, 95 % after 3, 99 % after 5 | 10 kΩ x 100 nF = 1 ms; settled (5 tau) in 5 ms |
| 5 LED resistor | R = (Vsupply − Vf)/I | Red Vf ~2.0 V, 5 mA: (3.3−2.0)/0.005 = 260 -> use 270 Ω (4.8 mA). Blue/white Vf ~3.0 V: at 3.3 V only ~0.3 V left, use 47–100 Ω or a 5 V supply |

- Round R up to the next E12/E24 value (220, 270, 330, 470, 680, 1k, 2k2, 4k7, 10k).
- Series R add; parallel: 1/Rt = 1/R1 + 1/R2 (two equal -> half).
- Divider loads: the load in parallel with R2 changes Vout; keep load impedance >= 10x R2.
- LED current 1–5 mA is visible on modern LEDs; 20 mA is a maximum, not a target.

## 2. Power
### USB and devkit supply
| Source | Limit |
|---|---|
| USB 2.0 port | 100 mA before enumeration, 500 mA after |
| USB 3.x port | 900 mA |
| USB charger / BC1.2 / USB-C default | 1.5 A / 1.5 A / 3 A (USB-C needs 5.1 kΩ on each CC pin to be sourced) |
| ESP32 devkit on-board LDO (AMS1117 or AP2112) | AMS1117 ~800 mA, AP2112 ~600 mA nominal; real limit is heat. check datasheet / board schematic |
| ESP32 Wi-Fi TX peak | ~250–400 mA for ~ms bursts, check datasheet |
- Devkit 3V3 pin: budget ~100–200 mA for external sensors. Anything bigger gets its own regulator.
- Cheap/thin USB cable = voltage drop = brownout. Use short, thick cable; measure 5 V at the board.

### LDO vs buck
| | LDO | Buck |
|---|---|---|
| Efficiency | Vout/Vin | 85–95 % |
| Noise | very low | switching ripple, needs inductor/layout |
| Heat | (Vin − Vout)·I | low |
| Parts | 2 caps | inductor, diode/FET, caps (modules: MP1584, LM2596) |
| Use | small load, small drop (5 V -> 3.3 V at <150 mA), analog/RF | Vin >> Vout (12/24 V), load >200 mA, battery |
- Dropout = minimum Vin − Vout for regulation (AMS1117 ~1.1 V, AP2112 ~0.25 V at full load). check datasheet.
- Example: 12 V -> 3.3 V at 100 mA LDO: 8.7 V x 0.1 A = 0.87 W, too hot for SOT-223 without copper. Use buck.
- Adjustable buck modules (MP1584, LM2596): set output with a multimeter BEFORE connecting the load.

### Batteries
| Chemistry | Full | Nominal | Cutoff | Notes |
|---|---|---|---|---|
| Li-ion / LiPo | 4.2 V | 3.6–3.7 V | 3.0 V (protected cell cuts ~2.5–3.0) | needs charger IC (TP4056 ~4.2 V, set current <= 1C); never charge <0 °C; needs protection board |
| LiFePO4 | 3.65 V | 3.2 V | 2.5 V | flat curve, safer, 3.3 V rail directly possible |
| AA alkaline | 1.6 V | 1.5 V | ~0.9 V | 2xAA = 3.0 V fresh, drops below 3.3 V -> need boost for 3.3 V |
| AA NiMH | 1.4 V | 1.2 V | 1.0 V | 3xAA = 3.6 V OK, 4xAA = 4.8 V |
- Li-ion straight to ESP32 3.3 V LDO: works to ~3.5 V (LDO dropout). Low-dropout LDO or buck-boost extends.
- Battery life (h) = capacity (mAh) / average mA x ~0.7 (derate). Deep sleep average current dominates.

### Sizing a supply
1. Sum worst-case currents of every load (peak, not average). 2. Add 30–50 % margin. 3. Check regulator rating and heat. 4. Check source can deliver it.
- Example: ESP32 400 mA peak + sensor 50 mA + relay coil 70 mA = 520 mA -> x1.5 = 780 mA -> choose 1 A supply.

### Decoupling
- 100 nF ceramic (X7R) on every VCC pin, as close to the pin as possible, short path to GND.
- Bulk 10–100 µF near radios (ESP32 module, LoRa PA, cellular needs 470–1000 µF), motors, servos, LED strips.
- Regulator in/out caps per datasheet (AMS1117 needs ESR-bound output cap: check datasheet).

### Brownout symptoms
Random resets on Wi-Fi start or relay click; "Brownout detector was triggered"; flash/NVS corruption; ADC noise; UART garbage at TX bursts; Wi-Fi drops. Check: 3.3 V rail on scope/multimeter min-hold, cable, shared supply with motor, missing bulk cap.

### Grounding
- Every device that exchanges a signal must share a common GND (UART, I2C, SPI, analog, 3.3 V logic from two supplies). Without it levels are meaningless.
- Exceptions: isolated links (opto, isolated RS-485/DC-DC). Then each side has its own ground, never joined.
- High-current returns (motors, relays, LED strips) go back to the supply directly, not through the MCU GND pin or breadboard rail.
- NEVER power motors, relays, servos, solenoids, LED strips from the MCU 3.3 V pin or from a GPIO. Use separate supply + switch device (section 4).

## 3. Logic levels
| Level | VOH/VIH typical | Note |
|---|---|---|
| 3.3 V CMOS | VIH ~0.75·VDD (ESP32: check datasheet) | ESP32 GPIO are NOT 5 V tolerant |
| 5 V TTL/CMOS | VIH 2.0 V (TTL) or 0.7·5 = 3.5 V (CMOS) | |
- Dangerous direction: 5 V output -> 3.3 V input (damages ESP32 over time or instantly). 3.3 V -> 5 V input is usually safe for TTL-threshold inputs (2.0 V) but fails for CMOS-threshold (e.g. WS2812 needs 0.7·VDD = 3.5 V).
- Never connect a 5 V UART TX (e.g. Arduino Uno) directly to ESP32 RX; use a divider or shifter.

| Method | Use | Notes |
|---|---|---|
| Resistor divider 1k/2k (or 2k2/3k3) | slow, one-way 5 V -> 3.3 V (UART RX, button, <100 kHz) | 5 V x 2/3 = 3.33 V; never for bidirectional |
| BSS138 FET shifter (4-ch modules) | bidirectional open-drain: I2C, 1-Wire | 10k pull-up each side; limited to ~400 kHz |
| 74LVC245 / 74LVC1T45 / 74AHCT125 | fast push-pull SPI, LEDs (74AHCT125 3.3 -> 5 V), parallel | one direction per gate, direction pin on '245 |
| TXS0108E | auto-direction, push-pull up to ~20–60 Mbps | poor with heavy pull-ups; not for I2C with strong pull-ups, check datasheet |
- Open-drain: line is pulled low by device, high by pull-up resistor. Needed for I2C, 1-Wire, shared interrupt lines. Never drive open-drain high with a push-pull output.
- I2C pull-up: Rmax = tr / (0.8473·Cb); Rmin = (Vcc − 0.4 V)/3 mA. tr = 1000 ns (100 kHz), 300 ns (400 kHz); Cb = bus capacitance (<= 400 pF). 3.3 V: Rmin ~ 1 k. 400 kHz, 100 pF: Rmax = 300 ns/(0.8473·100 pF) = 3.5 kΩ. Typical 4.7 k at 100 kHz, 2.2k–3.3k at 400 kHz. Breakout boards often already have 4.7k/10k: paralleled they lower R (3 boards of 10k = 3.3k).
- Floating inputs read random values and oscillate: always use a pull-up/pull-down (internal ESP32 ~45 kΩ, weak; use external 10k for noise/long wires). ESP32 GPIO34–39 have no internal pulls. Strapping pins (GPIO0/2/12/15 on ESP32): do not hold at wrong level at boot.

## 4. Driving loads
- GPIO: design for <= 10 mA per pin source/sink (ESP32 default drive ~20 mA, absolute max ~40 mA, check datasheet for total chip limit). An LED or an optocoupler LED can be driven directly; a relay coil, motor, buzzer >10 mA cannot.

### Low-side switch (load between +V and switch to GND)
| Part | Choice | Notes |
|---|---|---|
| NPN BJT (BC547 100 mA, 2N2222 800 mA) | Rb so that Ib >= Ic/10 | Ic 50 mA -> Ib 5 mA -> Rb = (3.3−0.7)/5 mA = 520 -> 470 Ω. Add 10k base-emitter pulldown |
| N-MOSFET logic-level | Rds(on) specified at Vgs <= 2.5–3.3 V | AO3400 (SOT-23, 30 V 5.7 A) good at 3.3 V; IRLZ44N (TO-220, 55 V) logic-level but spec'd at 4–5 V, marginal at 3.3 V; IRLB8721 etc. Do NOT use IRF540/IRFZ44 (needs 10 V) |
- Gate: 100–220 Ω series (limits ringing/inrush), 10k–100k gate-to-source pulldown (so load is OFF while MCU boots/floats).
- Source must connect to common GND with MCU.
- High-side (load to GND, switch to +V): P-MOSFET or high-side driver; harder, prefer low-side.

### Inductive loads
- Relay/solenoid/motor coil: flyback diode across coil, cathode to +V (1N4007 or 1N4148/1N5819 for small ones; 1N4007 is slow but fine for relays). Without it spike (hundreds of V) resets MCU or kills the transistor.
- DC motors: also 100 nF across motor terminals, bulk cap at supply.

### Relay modules
- Typical 1/2/4/8-ch module (SRD-05VDC ~70 mA per coil at 5 V): opto-isolated, ACTIVE-LOW (IN low = relay ON). Set pin HIGH at boot to stay off.
- JD-VCC jumper: with jumper, coil powered from VCC (shared with MCU). Remove jumper and feed JD-VCC from separate 5 V supply to isolate; MCU supplies VCC (opto side) only; keep GND linked to the opto side only as per module datasheet.
- 5 V relay module with 3.3 V MCU: opto side often works at 3.3 V but check; some modules need a transistor. Test coil click and measure.
- Contacts: rated per load type (10 A resistive, much less for inductive/DC). Use 1/2 of rating. DC arcing: rating is lower than AC.

### SSR
- SSR-AC (triac, e.g. Fotek): AC load only. DC-SSR: DC only. Zero-cross type turns on at 0 V crossing, best for resistive loads (heaters, lamps); random-fire for phase control/inductive. Leakage mA (small loads glow). Heatsink above ~2 A. Input typically 3–32 V DC at ~10 mA, check datasheet.

### H-bridge and motors
- L298N: ~2 V drop, large, inefficient. DRV8833 / TB6612FNG: efficient, ~1–1.2 A per channel. Pins: IN1/IN2 direction, PWM speed (EN or IN), STBY. Never turn on both high and low switch of the same leg (shoot-through); drivers have it covered, discrete bridges need dead time.
- Stepper: DRV8825/A4988 driver, set Vref current limit, never unplug motor while powered.

### Servo
- Hobby servo (SG90): 5 V, ~100 mA moving, stall 600+ mA. Separate 5 V supply, 470–1000 µF cap, GND common with MCU. Signal 3.3 V normally OK. Servo jitter/reset = shared supply.

## 5. Reading sensors
### ADC (ESP32)
- 12-bit: counts 0–4095. Vin = count/4095 · Vfs. 10-bit: 1023.
- ESP32 classic: ADC1 (GPIO32–39) usable with Wi-Fi; ADC2 NOT usable while Wi-Fi active. Non-linear near 0 and near full-scale; use esp_adc calibration. Attenuation: 0 dB (~1.1 V), 2.5 dB (~1.5), 6 dB (~2.2), 12/11 dB (~3.1–3.3 V full scale); check datasheet for the chip. Stay within 0.15–3.0 V for best accuracy.
- Average 16–64 samples, add 100 nF at the pin, source impedance <= 10 kΩ (or buffer).
- External ADC (ADS1115 16-bit I2C, address 0x48–0x4B) for precision.
- Higher voltages: divider. Vin 12 V -> 33k/10k gives 2.79 V. Vin = Vadc·(R1+R2)/R2. Use 1 % resistors; protect with 3.3 V clamp / series 1k.

### NTC thermistor
- Divider: NTC to GND, fixed R (equal to R25, e.g. 10k) to 3.3 V, ADC at midpoint. R_ntc = Rfixed · V/(Vcc − V).
- Beta: T(K) = 1/(1/T0 + ln(R/R0)/B), T0 = 298.15 K, B ~3950 (10k NTC "B3950"). Example: R = 5 kΩ: ln(0.5) = −0.693 -> 1/T = 0.003354 − 0.0001755 -> T = 314.6 K = 41.5 °C.
- Steinhart–Hart: 1/T = A + B·ln R + C·(ln R)³ (coeffs from datasheet or 3-point fit). Accuracy ±1–2 °C with Beta. Self-heating: keep current low.

### 4–20 mA loop and 0–10 V
- 4–20 mA: shunt resistor to GND, read volts. 150 Ω -> 0.6–3.0 V (fits 3.3 V ADC); 250 Ω -> 1–5 V (needs divider). Value = (I − 4 mA)/16 mA. <3.6 mA = broken wire/fault. Shunt power at 20 mA 150 Ω = 60 mW. Loop supply 12–24 V; clamp input; use loop-powered 2-wire/3-wire per transmitter datasheet.
- 0–10 V: divider 22k/10k -> 10 V gives 3.125 V; add 3.3 V Zener/TVS + 1k series. Industrial: use isolated module.

### Buttons and digital inputs
- Bounce lasts 1–20 ms. Hardware: 10k pull-up + 100 nF to GND (tau 1 ms; add Schmitt trigger for clean edge). Software: sample every 5–10 ms, accept change after 20–50 ms stable, or ignore edges for 50 ms. Interrupt on raw edge without debounce = multiple triggers.
- Dry contacts (switch, door contact, relay output): no voltage; wire between GPIO (pull-up) and GND. Long wire: external 1k–4.7k pull-up, RC, TVS.
- Optocoupler (PC817, 4N35) for isolated/24 V inputs: LED side with series R = (Vin − 1.2 V)/Iled (5–10 mA; 24 V -> ~2.2k, 0.5 W), transistor side to GPIO with pull-up. Output inverted (LOW when input on). Bidirectional opto (AC): diode/rectifier input. CTR (current transfer ratio) varies 50–600 %, check datasheet.

## 6. Protection
| Threat | Fix |
|---|---|
| Reverse polarity | Series Schottky (1N5819/SS14, drops 0.3–0.5 V) or P-FET in series on the high side (source toward load, gate to GND, Zener if Vin > Vgs max); or diode bridge |
| Overcurrent | Fuse (fast/slow, rated 1.5x load, >= voltage) or polyfuse (hold current I_h trips at ~2·I_h, slow reset). check datasheet |
| Surges/ESD on external lines | TVS diode to GND: pick standoff voltage >= max working: 5 V line SMBJ5.0A, 12 V SMBJ13A (or 15A), 24 V SMBJ28A; RS-485 SM712 |
| GPIO going off-board | 100 Ω–1 kΩ series resistor + clamp diodes/TVS (e.g. PESD) + RC if slow signal |
| Motor/relay kick | flyback diode/TVS |
| ESD handling | wrist strap, don't touch pins, store in anti-static bag, touch ground first |
- Hot-plug of power with big caps: inrush; use NTC/soft-start. Never hot-plug sensors on powered I2C.

### Mains safety (230 V AC India/EU, 120 V US)
- If unsure, don't. Use certified AC-DC modules (HLK-PM01, 5 V 600 mA; Mean Well) and pre-made enclosures. Fuse the live input, isolate mains from low voltage by a rated barrier.
- Creepage/clearance: >= 6 mm between mains and low voltage, slot milling in PCB; keep traces away; use enclosed terminals; earth any metal case.
- Never probe live mains with a grounded oscilloscope (earth-referenced probe on live = short). Use an isolated differential probe, or an isolation transformer, or don't probe. Power down and verify with multimeter before touching.
- Relay/SSR switches live; keep neutral/earth connected; one hand rule; no wet area.
- Prefer isolated modules for AC measure (ZMPT101B, PZEM-004T); do not wire mains to dev boards.

### RS-485 line protection and termination summary
- 120 Ω across A/B at BOTH ends only (not in the middle); bias resistors at one point only (typ 470–1k pull-up to VCC on one line and pull-down to GND on the other; total with termination must keep >= 200 mV idle differential, check transceiver datasheet). Twisted pair (Cat5 pair), daisy chain, no stubs > 0.5 m.
- Protection: TVS (SM712), optional 10 Ω series PTC/resistors, gas arrestor outdoors, isolated transceiver (ADM2587E, ISO1410) if different earth potentials (check datasheet). Common reference wire/shield at one end.

## 7. Bench tools
| Tool | How to use for diagnosis |
|---|---|
| Multimeter | Continuity (beep < ~50 Ω; POWER OFF): shorts VCC–GND, broken traces. DC volts: measure WITH load running (rail sag). Current: break the circuit, meter in series, red lead in A/mA jack; return lead to V jack after, otherwise leads in A jack across a supply = short. Diode mode for LED/diode polarity (forward drop 0.2–0.7 V Si/Schottky, 1.8–3 V LED). Resistance: remove from circuit/power off |
| Logic analyser (8ch USB, Saleae clone, sigrok/PulseView) | Capture UART/I2C/SPI/1-Wire/CAN decoders. Sample rate >= 4x highest bit rate, 10x better (I2C 400 kHz -> 4–10 MS/s). Connect GND first. Check: idle level, baud, ACK/NACK, CS timing, clock mode. Trigger on falling edge of CS/start |
| Oscilloscope | Needed for: ringing/overshoot, supply ripple/noise, rise time, analog signals, PWM, RS-485 differential waveform, brownout dips. Use 1x probe for ripple, ground spring (short GND lead), probe compensation. Bandwidth >= 5x signal frequency |
| USB-UART adapter (CP2102/CH340/FT232) | Serial console, flashing; 3.3 V mode. Cross TX/RX, share GND, do not connect 5 V VCC if board has own supply |
| USB-RS485 adapter | Test Modbus/BACnet from PC. Check A/B swap, termination switch, driver direction auto. Use a known-good slave first |
| Bench supply with current limit | Set 3.3 V/5 V and limit 100–200 mA on first power-up: if CC LED lights -> short. Current readout shows sleep, Wi-Fi, TX pulses |
| Thermal check | Finger test (>60 °C hurts = too hot: LDO, FET, resistor); IR thermometer / thermal camera; hot component = wrong polarity, short, or undersized regulator. Power off first when touching |

## 8. Reading a schematic
| Symbol | Looks like |
|---|---|
| Resistor | zigzag or rectangle; Rn |
| Capacitor | two parallel lines; curved/+ = polarized |
| Inductor | coil / humps; Ln |
| Diode | triangle + bar (bar = cathode) |
| LED | diode + arrows out |
| NPN/PNP | circle, arrow on emitter (out = NPN) |
| N-MOSFET | gate, drain, source; arrow in |
| Ground | horizontal lines / triangle; chassis vs signal GND |
- Net labels: same name = same wire even if not drawn connected. Power flags/symbols (+3V3, +5V, GND). Dot = junction; crossing without dot = no connection.
- Reference designators: R resistor, C capacitor, L inductor, D diode, Q transistor, U IC, J/P connector, SW switch, F fuse, Y crystal, K relay, TP test point.
- Trace a signal: connector pin (J1) -> series R / TVS / filter -> net label -> MCU pin name (GPIOxx) -> check strapping/ADC2/input-only/flash pins.
- Datasheet fast order: (1) features/part number suffix, (2) absolute max table (never exceed), (3) recommended operating conditions (design to this), (4) pinout + package, (5) typical application circuit (copy), (6) electrical characteristics (VIH/VIL, drive, current), (7) timing diagrams, (8) register map. Confirm units and conditions column ("typ" at 25 °C).

## 9. Component identification
### Resistors
| Colour | Digit | Multiplier |
|---|---|---|
| Black / Brown / Red / Orange / Yellow | 0 / 1 / 2 / 3 / 4 | x1 / x10 / x100 / x1k / x10k |
| Green / Blue / Violet / Grey / White | 5 / 6 / 7 / 8 / 9 | x100k / x1M / x10M / – / – |
- Gold = x0.1 and ±5 %, silver = x0.01 and ±10 %, brown = ±1 %. 4-band: d1 d2 mult tol. 5-band: d1 d2 d3 mult tol. Example brown-black-orange-gold = 10k ±5 %.
- SMD: 3 digits "103" = 10 x 10³ = 10k, "472" = 4.7k, "000" or 0R = jumper; 4 digits "1002" = 10k; "R" is decimal point: 4R7 = 4.7 Ω, R10 = 0.1 Ω. EIA-96 (2 digits + letter, e.g. 01C): look up chart.
### Capacitors
- Code = 2 digits + multiplier, in pF: 104 = 10 x 10⁴ pF = 100 nF; 103 = 10 nF; 102 = 1 nF; 105 = 1 µF; 224 = 220 nF; 473 = 47 nF; 101 = 100 pF; "22" = 22 pF. Letter after = tolerance (K = 10 %, J = 5 %, M = 20 %).
- Dielectric: X7R/X5R fine for decoupling; C0G/NP0 for timing/RF; Y5V loses capacity at voltage. Voltage rating >= 2x working.
### Polarity marks
| Part | Marks |
|---|---|
| Electrolytic | stripe/minus on cathode (−); longer leg +; wrong way = vents/explodes |
| SMD tantalum | bar/stripe marks ANODE (+) (opposite of diode!) |
| Diode | stripe = cathode |
| LED | longer leg/larger plate inside = anode; flat edge on lens = cathode; SMD: green dot/notch = cathode (varies, test with multimeter diode mode) |
| IC | notch/dot = pin 1, count counter-clockwise from top |
### Packages
| Package | Size / info |
|---|---|
| 0402 / 0603 / 0805 / 1206 | 1.0x0.5 / 1.6x0.8 / 2.0x1.25 / 3.2x1.6 mm; power ~1/16 / 1/10 / 1/8 / 1/4 W. 0603 = hand-solderable default |
| SOT-23 | 3-pin small transistor/FET/LDO; pin 1 position varies, check datasheet |
| SOT-223 | LDO (AMS1117), tab = output or ground per part |
| SOIC-8 (1.27 mm pitch), TSSOP, MSOP | easy-to-moderate IC packages |
| QFN / DFN | no leads, thermal pad underneath, needs hot air or paste; hard by hand |
| TO-92 / TO-220 | through-hole transistor / power (BC547 pinout differs from PN2222: check datasheet) |
### Common parts
| Part | What | Key numbers |
|---|---|---|
| AMS1117-3.3 | LDO | 1 A max (800 mA typ), dropout ~1.1 V, Vin <= 15 V, SOT-223 |
| AP2112K-3.3 | LDO | 600 mA, dropout ~0.25 V, Vin <= 6 V, SOT-23-5 |
| MP1584 module | buck | Vin 4.5–28 V, 3 A, adjustable, set Vout first |
| 2N2222 / PN2222 | NPN | 40 V, 600–800 mA, hFE ~100 |
| BC547 | NPN | 45 V, 100 mA, hFE 110–800 |
| AO3400 | N-FET SOT-23 | 30 V, 5.7 A, logic-level (Vgs 2.5 V ok) |
| IRLZ44N | N-FET TO-220 | 55 V, 47 A, logic-level (4.5–5 V) |
| 1N4007 | rectifier | 1 A, 1000 V, slow; flyback/reverse protection |
| 1N4148 | small signal | 100 V, 200 mA, fast |
| 1N5819 | Schottky | 1 A, 40 V, ~0.4 V drop (through-hole) |
| SS14 | Schottky SMD (SMA) | 1 A, 40 V, ~0.5 V drop |
