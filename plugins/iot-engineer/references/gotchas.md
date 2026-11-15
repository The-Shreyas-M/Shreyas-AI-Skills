# Gotchas — symptom → cause → fix

Search this file by symptom before debugging. Add a line whenever a new root cause is found.

## ESP32-S3 pins and memory
- Peripheral on GPIO 35–37 dead on an N8R8 module → octal PSRAM owns GPIO 33–37 → move the pins, or build without `CONFIG_SPIRAM`.
- USB or a bus on GPIO 19/20 misbehaves → they are the native USB pins → avoid, or accept losing USB.
- Board enters download mode / will not boot → a button or load on GPIO0 (or other strapping pins 3, 45, 46) → never put a button on GPIO0.
- Stack overflow in a protocol task on larger requests → default stack too small → raise it via Kconfig (a BACnet WriteProperty needed 12 KB, not 6 KB).

## SPI Ethernet (W5500)
- Chip ID reads `0x00` → pins are the S3's native SPI2 pins, so IDF routes through IOMUX and it fails on this board → force the GPIO matrix with `SPICOMMON_BUSFLAG_GPIO_PINS`; run at 4 MHz; explicit reset and a few probes before the ID check.
- Thousands of "received frame was truncated", then task watchdog → an RX length header reads back corrupt and the driver walks garbage → patch a copy of the MAC driver: an impossible length discards all pending RX data in one step.
- Ethernet goes deaf after the first DHCP exchange → a missed falling edge leaves INT low forever → poll every 10 ms (INT GPIO = -1).
- W5500 and a second SPI chip (e.g. SX1262) on one bus fail randomly → the idle chip's CS floats → drive every CS and RESET high before starting the bus; init the radio before the network.

## Sockets, web UI
- Browser shows "Failed to fetch" intermittently → lwIP's 10 sockets are used up → `CONFIG_LWIP_MAX_SOCKETS=24` and a written per-module socket budget.

## Wi-Fi
- Scan fails or connect stalls → scans race with connect → one task owns all scans; mark "running" immediately; retry driver-busy every 250 ms up to 10 s; 15 s watchdog.
- Board freezes with no watchdog after AP bandwidth change → `esp_wifi_set_bandwidth(AP, HT20)` followed by AP→AP+STA switch → do not do that sequence.
- AP drops when the station connects → one radio, one channel: the AP follows the station's channel → expected; tell the user.
- Bad credentials saved → saved on connect → save a network only after it gets an IP.
- No DHCP OFFER on one network but fine on a hotspot → network-side (seen on a campus network with 802.11n; 11b-only worked) → cause not established; compare with a devkit on the same network before blaming the PCB.

## RS-485 / Modbus
- Master cannot drive the bus → TX/RX swapped in config → confirm against the PCB, not the assumption.
- Auto-direction transceiver → there is no DE pin; set it to -1.
- Only some reads answered on real meters → inter-frame gap too short. Measured: 15 ms → 23 %, 50 ms → 90 %, 100 ms → 100 %. Sweep it; do not guess.
- Whole bus cascades offline after one slow slave → a late reply was accepted as the next slave's answer → discard any reply whose slave id is not the one just addressed.
- One dead slave slows everything → every poll waits for its timeout → mark offline after 3 failed rounds, retry every 30 s.
- Log flooded with errors → esp-modbus logs each unanswered request → mute that tag and count failures instead.
- Wrong values, right registers → word order → support ABCD / CDAB / BADC / DCBA per point.
- Device rejects reads → block spans unimplemented addresses → merge only contiguous requested registers (max 125 registers / 2000 bits); never read addresses nobody asked for.
- Values show 0 before first poll → publish as out-of-service until the first good read.
- Board resets when the PC opens the port → DTR/RTS toggles → set `rts=False; dtr=False` before `open()` (patch simulators too).

## BACnet
- Upstream lwip/bsd/esp32 ports do not fit ESP-IDF → write your own datalink port files for lwIP UDP and the UART.
- MS/TP timing unreliable → needs `CONFIG_FREERTOS_HZ=1000`.
- ~400 KB of RAM gone → default `MAX_TSM_TRANSACTIONS` → set to 1 on a device.
- Object names corrupt → the stack keeps the pointer → names need static storage.
- Large integers wrong → Present_Value is a 32-bit REAL; integers above 16,777,216 lose precision.
- Points frozen at 0 → a type switch handled only the default object type → handle every mapped type; add a host test per type.
- Client reading 190 points in a burst gets 55–132 replies → small lwIP UDP queue → the client must poll sequentially (100 %).

## LoRa (SX126x)
- Radio silent → wrong TCXO voltage stops the oscillator; or BUSY/DIO1 pins unknown → get them from the schematic; keep the module compile-only until then.
- No RF → DIO2 may be the RF switch control → enable it.
- Long-symbol links unreliable → low-data-rate optimisation must be on when a symbol is ≥16 ms.
- −106 dBm with boards side by side → antenna missing or wrong band.

## Cellular
- Modem never powers → PWRKEY/RESET polarity (a transistor inverts it) → read the schematic.
- Cannot reach the device → carrier NAT; no inbound connections, so no push OTA over cellular.

## MQTT / TLS / time
- TLS handshake fails at boot → clock not set → NTP before MQTT.
- TLS fails against a broker addressed by IP → mbedTLS matches the DNS form → the certificate needs the address as both `IP:` and `DNS:` SAN.
- NTP never syncs → UDP 123 blocked → fall back to the HTTP `Date` header; set `CONFIG_LWIP_SNTP_MAX_SERVERS=3`.
- Clock jumps backwards after reboot → guard with a stored sequence and a maximum back-step; freeze schedules and hold telemetry while the clock is invalid.
- Reconnect storms → back off 5 → 60 s. Client id = MAC.
- Broker unreachable on campus/office network → network blocks unregistered devices → bench with a laptop broker via gitignored `sdkconfig.local`.

## OTA / flash
- After OTA tests, a fresh flash still boots old code → otadata still selects the other slot → flash the full `@flash_args` set.
- New IDF firmware must OTA onto units running older (e.g. Arduino) firmware → keep the partition table identical; if the old bootloader has rollback on, mark the image valid at boot.
- "Serial noise" / cannot flash → cable, power, or a faulty GPIO0 path → try another cable/port; use serial OTA through the console.

## Build and tooling (Windows)
- New Kconfig symbol undeclared in the build → stale `sdkconfig` → delete `apps/<app>/sdkconfig`, rebuild. Also confirm the symbol is actually defined in a `Kconfig` that the app loads.
- Component declared only in a vendored library's `idf_component.yml` is missing at link time → component manager is off → add it in the wrapper's `CMakeLists.txt`.
- Host tests fail to start in Git Bash → long temp path → set a short `TMPDIR`.
- Writing C or HTML through shell heredocs breaks on quotes → write files with the editor tool, not the shell.
- pymodbus API errors in bench scripts → pin pymodbus 3.6.x.

## Working with AI agents
- A cheap model's docs passed a grep for identifiers but the prose was wrong → read delegated docs once; grep is not review.
- A status file said "fixed" but the fix had been reverted → trust the newest status file and the code, then verify with a build.
- A module "done" with pins unknown → mark "Not configured", compile-only, and add a `PENDING.md` row.
