# Protocols (bench reference)

Format per block: what / use / wires+levels / key params / failure -> check. "check datasheet" = part-dependent.

## UART
- What: async serial, no clock. Use: console, GPS, modems, RS-485/RS-232 behind a transceiver.
- Wires: TX, RX, GND (cross TX<->RX). 3.3 V logic on ESP32 (RS-232 is ±12 V: needs MAX3232; 5 V TTL needs shifting).
- Params: 8N1 = 8 data, no parity, 1 stop (10 bits/byte, ~11.5 KB/s at 115200). Common bauds 9600, 115200. Both ends must match within ~2 %.
- Failure -> check:
  - Garbage characters -> baud/parity/stop mismatch.
  - Nothing -> TX/RX not crossed, missing common GND, wrong pins, wrong voltage level.
  - Garbage on ESP32 boot -> ROM bootloader prints at 74880 baud.
  - Dropped bytes at high baud -> FIFO/flow control, long wires; use RTS/CTS.

## I2C
- What: 2-wire bus, multi-device, addressed. Use: sensors, displays, expanders, RTC.
- Wires: SDA, SCL (open-drain), GND, pull-ups to VCC (one set only: 2.2k–10k). Levels 3.3 V (or 1.8/5 V per device; shift with BSS138).
- Params: 100 kHz standard, 400 kHz fast, 1 MHz fast+. 7-bit address (0x08–0x77); R/W is the 8th bit (datasheet "0x78" = 0x3C 7-bit). Max bus capacitance 400 pF. Pull-up: R = tr/(0.8473·Cb). Wire <= ~1 m at 100 kHz.
- Common addresses: SSD1306 0x3C/0x3D, BME280/BMP280 0x76/0x77, ADS1115 0x48–0x4B, DS3231 0x68, MPU6050 0x68/0x69, PCF8574 0x20–0x27, BH1750 0x23/0x5C.
- Failure -> check:
  - Scan finds nothing -> pins, pull-ups (measure SDA/SCL idle = 3.3 V), power, address, GND.
  - Two devices same address -> address pin/jumper, second bus, or TCA9548A mux.
  - Intermittent / slow edges -> pull-ups too weak (long wire, many boards) or too strong; look at scope.
  - Bus hung, SDA stuck low after reset -> clock SCL up to 9 times until SDA high, then STOP, re-init.
  - Clock stretching: device holds SCL low; master must support/timeouts (ESP32 timeout setting).
  - Many breakouts in parallel -> pull-ups paralleled to <1 k.

## SPI
- What: 4-wire synchronous full-duplex. Use: flash, displays, SD, W5500, LoRa radios, ADCs.
- Wires: SCLK, MOSI, MISO, CS (one per device), GND. Push-pull, 3.3 V.
- Modes: CPOL = idle clock level, CPHA = sample edge.
  | Mode | CPOL | CPHA | Idle clk | Data sampled |
  |---|---|---|---|---|
  | 0 | 0 | 0 | low | rising |
  | 1 | 0 | 1 | low | falling |
  | 2 | 1 | 0 | high | falling |
  | 3 | 1 | 1 | high | rising |
- Speed: device max in datasheet; ESP32 80 MHz IO_MUX pins / 40 MHz GPIO matrix. Jumper wires: start 1–4 MHz, <= 10 MHz and short (<20 cm).
- Failure -> check: all 0x00/0xFF reads -> wrong mode, CS not asserted, MISO floating, wrong pins; works slow, fails fast -> wire length/ringing; two devices -> only the selected CS low, others high; MISO of unselected devices must be tri-state; shared SD card breaks bus.

## 1-Wire
- What: single data wire + GND (+VCC unless parasite). Use: DS18B20 temperature, iButton.
- Wires: DATA with 4.7 kΩ pull-up to 3.3 V. DS18B20 3.0–5.5 V.
- Params: 64-bit unique ROM per device, bit-banged timing (use RMT on ESP32). 12-bit conversion takes up to 750 ms. Reads 85.0 °C = power-on value (not converted yet); −127/0xFF = no device/short.
- Failure -> check: no device -> pull-up missing, DATA/GND swapped (device heats), long cable (use 2.2k–3.3k or star <= 50 m), parasite power at long distance (use 3 wires).

## RS-485
- What: differential half-duplex multi-drop physical layer. Use: Modbus RTU, BACnet MS/TP, DMX, industrial sensors, 1200 m at <= 100 kbps.
- Wires: A, B (twisted pair), GND/reference (optional wire). Transceiver chip needed (MAX485, SP3485 3.3 V, MAX13487 auto-direction).
- Naming: A/B and D+/D− are inconsistent between vendors. A = D− and B = D+ in TIA-485; many vendors label opposite. If dead/garbled, swap A and B (safe).
- Half-duplex: DE (driver enable) and /RE (receiver enable) tied together: HIGH = transmit, LOW = receive. Switch to receive after the last stop bit has left the UART (wait for TX done), or use hardware auto-direction.
- Termination: 120 Ω across A/B at both physical ends only (never at nodes in middle, never on stubs). Bias resistors at ONE point (typ 470–750 Ω pull-up on B to VCC, pull-down on A to GND) so idle line is not floating (>= 200 mV idle).
- Topology: daisy-chain, no star, stubs < 0.5 m. Max 32 unit loads (1/8-UL transceivers allow up to 256 nodes). Cable: shielded twisted pair, 120 Ω impedance. Common ground reference connected (or isolated transceivers with a shield).
- Failure -> check: garbage -> A/B swap, baud/parity (8E1 vs 8N2), termination missing, direction timing; works with 1 slave not 5 -> bias/termination/stubs/addresses; all dead -> wrong DE/RE or supply; occasional errors -> ground loop, noise, termination, cable too long for baud.

## Modbus RTU
- What: master/slave request-response over RS-485 (or RS-232). Slave address 1–247 (0 broadcast, no reply).
- Frame: [addr 1B][function 1B][data N][CRC16 2B]. CRC-16/MODBUS: init 0xFFFF, poly 0xA001 (reflected of 0x8005), sent low byte first. Frame separator: silence >= 3.5 character times (at baud >= 19200, fixed 1.75 ms). 1 char = 11 bits (8E1 default or 8N2).
- Functions:
  | Code | Name | Data |
  |---|---|---|
  | 01 | Read coils | bit R/W |
  | 02 | Read discrete inputs | bit RO |
  | 03 | Read holding registers | 16-bit R/W, max 125 regs |
  | 04 | Read input registers | 16-bit RO, max 125 regs |
  | 05 | Write single coil | 0xFF00 = on, 0x0000 = off |
  | 06 | Write single register | |
  | 15 (0x0F) | Write multiple coils | |
  | 16 (0x10) | Write multiple registers | max 123 regs |
- Exception reply: function | 0x80, then code: 01 illegal function, 02 illegal data address (register not mapped), 03 illegal data value (bad quantity/value), 04 server (slave) device failure. Others: 05 ack, 06 busy, 0A/0B gateway.
- Register numbering: 0-based "protocol address" vs 1-based "register number". 4xxxx notation: holding register 40001 = address 0; 3xxxx input (30001 = 0), 1xxxx coil/discrete 0xxxx. Off-by-one is the top bug: if read returns neighbour value, try address ±1.
- Data types: 32-bit and float (IEEE 754) span 2 registers; word order differs by vendor: ABCD (big-endian), CDAB (word swap, common), BADC, DCBA. Test with a known value (e.g. 1.0 = 0x3F800000). Scaling: raw x factor (e.g. 0.1). Signed int16 = two's complement.
- Timeouts: response timeout 200–1000 ms; retry 2–3 times; gap between requests >= 3.5 char; poll one slave at a time. Default serial params in datasheet (9600 8N1/8E1).
- Failure -> check: timeout -> wrong address, baud/parity, A/B swap, DE/RE, termination; CRC errors -> noise, wrong baud; exception 02 -> register address range/offset; exception 04 -> device internal fault.

## Modbus TCP
- Port 502. No CRC, no 3.5 char gap. MBAP header 7 bytes: transaction id (2), protocol id (2, = 0), length (2, bytes after this field = unit id + PDU), unit id (1; 0xFF or 1 for direct devices, slave id behind gateway). Then PDU (function + data) same as RTU.
- Failure -> check: connection refused -> port/firewall/IP; no reply behind RTU gateway -> wrong unit id; one connection limit on device; keep-alive.

## BACnet (MS/TP and IP)
- What: building automation. Data model: Device object with Objects (types: Analog Input/Output/Value AI/AO/AV, Binary Input/Output/Value BI/BO/BV, Multi-state MSI/MSO/MSV, Schedule, Trend). Object id = type + instance. Properties: Present_Value, Object_Name, Description, Units, Status_Flags, Out_Of_Service, Priority_Array (16 levels for commandable outputs, relinquish default).
- Device instance 0–4194302 unique across the whole BACnet internetwork (duplicates break Who-Is/I-Am).
- Discovery: Who-Is (broadcast) -> I-Am (reply). Read/Write Property, ReadPropertyMultiple, COV (change-of-value subscription, reduces polling; needs resubscribe before lifetime).
- MS/TP (RS-485): MAC 0–127 masters (0–254 on wire), unique per segment; Max_Master (default 127; set to highest used master MAC to speed up token cycle); token passing among masters; baud 9600/19200/38400/76800 (115200 on some), all devices same baud, 8N1. Same RS-485 wiring rules, up to 32 devices per segment (more with repeaters).
- BACnet/IP: UDP port 47808 (0xBAC0), broadcasts do not cross routers -> BBMD or foreign-device registration. Check: IP/subnet, broadcast reach, firewall, same port.
- Failure -> check: not discovered -> baud/MAC conflicts/device instance clash/Max_Master too low/termination; slow polling -> Max_Master too high, token cycle; writes ignored -> priority-array level overridden at higher priority, Out_Of_Service.

## CAN (TWAI)
- What: differential multi-master bus with arbitration. Use: vehicles, industrial, motor drives.
- Wires: CANH, CANL, GND. Transceiver REQUIRED (SN65HVD230 3.3 V, TJA1050/TJA1051 5 V; MCP2551 5 V): MCU TX/RX pins connect to transceiver, never to the bus directly. ESP32 TWAI controller: pins TX/RX to transceiver.
- Params: bitrate must match on all nodes (125/250/500 kbps, 1 Mbps). Rough max length: 1 Mbps 40 m, 500k 100 m, 125k 500 m. Classic frame: 11-bit (or 29-bit extended) id, 0–8 data bytes. Lower id = higher priority. 120 Ω termination at each end (60 Ω measured across CANH-CANL with power off).
- Failure -> check: bus-off/error passive -> bitrate mismatch, missing termination (measure 60 Ω), no ack (needs at least one other node), swapped CANH/L, no transceiver power. Receiver ack requires another working node on bus.

## MQTT
- What: publish/subscribe over TCP via broker. Use: telemetry, commands to cloud/Home Assistant.
- Port 1883 plain, 8883 TLS, WebSocket 9001/443 (broker-specific).
- QoS: 0 at most once (fire and forget), 1 at least once (duplicates possible, PUBACK), 2 exactly once (4-way handshake, rarely needed). Effective QoS = min(publisher, subscriber).
- Retain: broker stores last message per topic, delivers to new subscribers (use for status/config; clear by publishing empty retained). LWT (Last Will): message published by broker if client disconnects ungracefully (set topic "…/status" payload "offline", retain true; publish "online" retained after connect).
- Keepalive: seconds (30–120 typical); broker disconnects after 1.5x silence. Clean session true = no stored state; false = persistent session (queued QoS1/2 for client id). Client id unique: duplicate id kicks the other client in a loop.
- Topic design: lowercase, hierarchical, no leading `/`, no spaces, no wildcards in publish topics; `+` single level, `#` multi-level subscribe only. Example `site/device-id/sensor/temperature`. Put device id in topic, not payload only. Keep payload small (JSON or plain; < 1 KB on MCU; spec 256 MB). Add timestamp only if device has valid time.
- TLS: 8883 with CA cert (verify server); mutual TLS = client cert + key too (AWS IoT, etc.); needs correct system time (NTP), cert in PEM with trailing NUL for mbedTLS, SNI, RAM ~40–50 KB.
- Failure -> check: connect rc/ error -> credentials, client-id collision, port/TLS mismatch, time wrong (cert not yet valid), CA bundle missing; no messages -> topic typos, ACL, QoS/retain; reconnect loop -> keepalive too long, Wi-Fi sleep, broker limit.

## HTTP/REST and WebSocket on MCUs
- HTTP(S) request/response: use for infrequent configuration, OTA download, webhooks, REST APIs, local web UI served from device. Costly per request (TLS handshake ~ seconds, heap 40+ KB). Use persistent connection / reuse.
- WebSocket: persistent bidirectional over one TCP; use for live dashboards, low-latency control from browser. Needs ping/pong keepalive and reconnect logic.
- MQTT preferred for many devices/telemetry; HTTP for config/OTA; WebSocket for browser UI. Server-sent events as simple alternative.
- Failure -> check: -1 / timeout -> DNS, TLS cert/time, heap; 4xx/5xx -> API; mixed content/CORS from browser to device web server.

## BLE
- What: low-power short range (10–50 m typ). Roles: GAP: Peripheral (advertises, e.g. sensor) / Central (scans, connects, e.g. phone); GATT: Server (holds data) / Client. Broadcaster/Observer (no connection).
- GATT: Service (UUID: 16-bit standard, 128-bit custom) -> Characteristics (value + properties read/write/notify/indicate) -> Descriptors (CCCD 0x2902 enables notify).
- Advertising: interval 20 ms–10.24 s (shorter = faster discovery, more power); payload 31 bytes (extended adv more). Connection params: interval 7.5 ms–4 s.
- MTU: default 23 bytes (20 payload); negotiate up to 247–517; chunk larger data.
- Use: Wi-Fi provisioning (send SSID/password over BLE), phone config, beacons, sensors. ESP32: NimBLE stack (smaller RAM than Bluedroid). ESP32 (all except S2) supports BLE; Wi-Fi + BLE share the 2.4 GHz radio and heap.
- Failure -> check: not visible -> advertising not started, device already connected, MAC random/privacy; connect drops -> supervision timeout, RF coexistence, power; notify not arriving -> CCCD not enabled; Android caching stale GATT -> toggle Bluetooth.

## Wi-Fi
- Most ESP32 are 2.4 GHz only (802.11 b/g/n, WPA2/WPA3); ESP32-C5/C61 add 5 GHz (check datasheet). Hidden/5 GHz-only SSID not connectable on 2.4 GHz devices; band-steering routers: use separate 2.4 SSID.
- RSSI (dBm, closer to 0 is stronger): > −50 excellent, −50..−60 good, −60..−70 fair, −70..−80 weak (drops, retries), < −80 unreliable.
- Channels 1/6/11 non-overlapping (2.4 GHz). AP+STA mode: the AP runs on the same channel as the STA connection; channel changes drop clients. Max AP clients ~4–10.
- DHCP gives IP, gateway, DNS; static IP outside DHCP pool; reserve in router to be stable. mDNS gives `name.local` (Android older versions don't resolve .local). Power save modem-sleep raises latency (disable for control).
- Failure -> check: auth fail -> password, WPA3-only, 5 GHz SSID; no IP -> DHCP exhausted, MAC filter; keeps disconnecting -> RSSI, brownout (TX peaks), router channel width 40 MHz -> 20 MHz, sleep; DNS fails -> set 8.8.8.8/1.1.1.1.

## LoRa and LoRaWAN
- LoRa: physical chirp spread spectrum, SX1276/SX1262 radio over SPI. LoRaWAN: network protocol (gateway, network server, OTAA/ABP keys, classes A/B/C). Plain LoRa = point-to-point, you define the protocol. LoRaWAN needs gateway coverage (e.g. TTN).
- Trade-off: higher SF (7–12) = longer range, lower rate, longer airtime, more power; wider BW (125/250/500 kHz) = faster, less range; CR 4/5–4/8 = more error protection, slower. Bitrate = SF·(BW/2^SF)·CR. SF7/125 kHz/4-5 = 5.5 kbps; SF12/125 kHz/4-5 = 293 bps. Sensitivity ~ −123 dBm (SF7) to −137 dBm (SF12) at 125 kHz.
- Link budget: Ptx + Gtx + Grx − path loss − cable loss >= sensitivity + fade margin (10–20 dB). Antenna must be connected before TX (PA damage). Use correct antenna band (433/868/915).
- Regional bands: India 865–867 MHz; EU 868 MHz (g1 band 1 % duty cycle, 14 dBm ERP); US 915 MHz (902–928, dwell/hop rules); 433 MHz ISM in some regions. Duty-cycle and power limits: check local regulation. TTN fair use ~30 s uplink airtime per day per device (check current policy).
- Payload 51–222 bytes (depends on SF/region). Class A: receive windows only after uplink (lowest power).
- Failure -> check: no join -> wrong frequency plan/region, wrong keys (byte order), gateway not in range, SF/DR mismatch; short range -> antenna, SF, location; collisions -> random delay, ALOHA.

## Ethernet on MCUs
| Option | Interface | Notes |
|---|---|---|
| W5500 | SPI (up to ~33 MHz practical, check datasheet) | hardware TCP/IP, 8 sockets, 32 KB buffer; works with any MCU; ESP-IDF has driver (esp_eth spi); needs INT and reset pins; ~1–2 MB/s through SPI |
| LAN8720 / RMII PHY | RMII (MAC on ESP32 classic, ESP32-P4) | needs 50 MHz reference clock (from external oscillator or ESP32 APLL output on GPIO0/16/17, check board); ~10/100 Mbps full; uses many pins (GPIO 19,21/22,25,26,27 RMII fixed) |
- Wires: RJ45 with magnetics (use MagJack module). Status LEDs for link/activity. Use correct PHY address and reset pin.
- Failure -> check: no link LED -> cable, magnetics, power; link but no IP -> DHCP, PHY clock (RMII), strapping pins on GPIO0; W5500 reads 0x00 version -> SPI wiring/mode 0, reset pin; unstable -> power (3.3 V peaks ~150 mA).

## Cellular (LTE-M, NB-IoT, LTE Cat 1, 2G)
- Modules: SIM800/SIM7600/SIM7000, Quectel EC200/BG95. Interfaces: UART AT commands; PPP (module acts as modem, ESP-IDF PPP netif gives sockets) vs AT socket/MQTT commands (module handles TCP/MQTT, less MCU RAM).
- Config: APN from operator (e.g. internet), SIM PIN, band support per region (2G/LTE bands: check datasheet), correct antenna, signal CSQ (AT+CSQ: 0–31, > 10 usable; 99 = unknown).
- Power: supply 3.4–4.2 V (typ 4.0 V) and peak up to 2 A during TX (2G); dedicated buck / 18650, 470–1000 µF near module, thick short traces. Do not power from devkit 3.3 V or USB-only 500 mA. Power-key/PWRKEY timing, check datasheet.
- Failure -> check: no network -> SIM inserted/active, PIN, APN, antenna, band; resets when attaching -> power brownout (2 A peak); AT no response -> baud autobaud (send AT), TX/RX, level (1.8 V modules need shifter), PWRKEY.

## IR (infrared remote)
- Carrier 38 kHz (receivers TSOP38238, VS1838B; RC5 uses 36 kHz). Receiver output is demodulated and active-low (idle high). Transmit: LED + transistor, PWM 38 kHz at 33 % duty (LEDC/RMT), 100–220 mA pulse current via transistor.
- NEC: leader 9 ms mark + 4.5 ms space; 32 bits (address, ~address, command, ~command), LSB first; bit = 560 µs mark + 560 µs space (0) or 1690 µs space (1); repeat code 9 ms + 2.25 ms + 560 µs. RC5: Manchester, 14 bits, 889 µs half-bit.
- Unknown protocol: capture raw mark/space durations (RMT/IRremote) and replay raw array. Failure -> check: no signal -> sunlight/fluorescent interference, wrong pin/polarity, receiver power; poor range -> LED current, aim, repeat.

## PWM, servo, addressable LEDs
- PWM: LEDC on ESP32: frequency and resolution trade (bits = log2(80 MHz/f)). LED/dimming 1–5 kHz, motor drive 20 kHz (inaudible), buzzer = tone frequency.
- Hobby servo: 50 Hz (20 ms period), pulse 1.0 ms = 0°, 1.5 ms = center, 2.0 ms = max; many accept 0.5–2.5 ms. Servo 5 V, separate supply.
- WS2812 / SK6812 (NeoPixel): single-wire, 800 kHz bit rate (1.25 µs/bit), T0H 0.4 µs, T1H 0.8 µs, reset low >= 50 µs (280 µs for newer), 24 bits per LED (GRB order). Drive with RMT or SPI. Powered by 5 V; data from 3.3 V is out of spec (VIH = 0.7·VDD = 3.5 V): use 74AHCT125 level shifter, 330–470 Ω series on data, 1000 µF across supply, common GND, 60 mA per LED max at full white (plan 20 mA).
- APA102 / SK9822: 2-wire SPI-like (clock+data), no timing pain.

## NTP and time
- UDP 123. Servers: pool.ntp.org, time.google.com, regional (in.pool.ntp.org). SNTP in ESP-IDF: esp_sntp; sync after Wi-Fi connects, resync hourly–daily. Time zone as POSIX TZ string (IST = "IST-5:30", no DST).
- Without a battery RTC the clock is invalid until sync (year < 2024 means not synced). TLS cert checks and logs need valid time. DS3231 RTC (I2C 0x68, ±2 ppm) for offline. Store UTC, convert for display.
- Failure -> check: no sync -> UDP 123 blocked, DNS, captive portal; wrong hour -> TZ string.

## Which protocol for which job
| Job | Protocol | Distance | Speed | Nodes | Power | Cost |
|---|---|---|---|---|---|---|
| Board-to-board console / GPS | UART | < 15 m (TTL ~1 m) | 9.6k–1M | 2 | low | free |
| On-board sensors | I2C | < 1 m | 100–400 kHz | ~8–112 | low | free |
| Displays, flash, radios | SPI | < 20 cm | 1–80 MHz | few (1 CS each) | low | free |
| Temperature chain | 1-Wire | < 100 m | 16 kbps | many | low | very low |
| Industrial field wiring | RS-485 (+Modbus RTU/BACnet MS/TP) | 1200 m | 9.6k–115k (up to 10 Mbps short) | 32 (256) | medium | low |
| Industrial IP network | Modbus TCP / BACnet IP | LAN | 100 Mbps | many | high | low |
| Vehicles, motors | CAN | 40 m–1 km | 125k–1 Mbps | ~100 | medium | low-medium |
| Telemetry to cloud | MQTT over Wi-Fi/Eth/cellular | internet | n/a | thousands | Wi-Fi high | low |
| Phone config, wearables | BLE | 10–50 m | 100 kbps–1 Mbps | few connections | very low | low |
| Wi-Fi LAN devices | Wi-Fi | 30–100 m | Mbps | router-limited | high | low |
| Remote battery sensors | LoRa / LoRaWAN | 2–15 km | 0.3–50 kbps | thousands per gateway | very low | medium (gateway) |
| Wired reliability | Ethernet (W5500/RMII) | 100 m | 10/100 Mbps | switch | medium | medium |
| No Wi-Fi sites | Cellular LTE-M/NB-IoT | anywhere with coverage | kbps–Mbps | n/a | high peaks | recurring SIM fee |
| Remote appliance control | IR | 5–10 m line of sight | ~1 kbps | 1 | low | very low |
