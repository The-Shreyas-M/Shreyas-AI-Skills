# Chips reference

Rule: "check datasheet" = not verified here. Read the datasheet for the exact part before relying on it.

## Chip intake (ask / read BEFORE any design or firmware work)

| Item | Ask | Read from live board |
|---|---|---|
| Module marking | Exact string, e.g. `ESP32-S3-WROOM-1-N8R8` | `esptool.py chip_id`, `esptool.py flash_id` |
| Suffix decode | `N<x>` = flash MB, `R<x>` = PSRAM MB, `U` = external antenna connector (no PCB antenna), `H` = high-temp (flash) variant | boot log |
| Devkit | Name + revision (silkscreen), number of USB ports | - |
| USB bridge | CP2102(N) / CH340 / CH9102 / native USB-Serial-JTAG | Windows Device Manager VID:PID; `pio device list` |
| Flash | Size, mode (qio/dio/qout/dout/opi), speed | `flash_id` prints size; boot log `SPI Flash Size`, `SPI Mode` |
| PSRAM | Present? quad (R2/R4) or octal (R8/R16)? | boot log `psram`/`PSRAM` lines; `esp_psram_get_size()` |
| Crystal | 40 MHz (most), 26 MHz (some ESP8266/ESP32) | `esptool.py chip_id` prints `Crystal is 40MHz`; esptool `get_security_info` / `chip_id` also print features |
| Supply | Regulator part, its max current (AMS1117 ~800 mA, check part), USB vs battery | measure 3V3 under Wi-Fi TX |
| Antenna | PCB / U.FL external / none | module marking |

- `esptool.py chip_id` prints: chip type + revision, Features (e.g. `WiFi, BLE, Embedded Flash 8MB, Embedded PSRAM 8MB`), crystal, MAC. Newer esptool: `esptool chip-id` (hyphen form).
- Quad vs octal PSRAM changes which GPIOs are lost and the sdkconfig (`SPIRAM_MODE_OCT` vs `SPIRAM_MODE_QUAD`). Wrong mode = boot loop / PSRAM init failure in boot log.
- Boot log lines to find: `ESP-ROM:`, `rst:0x.. (reason)`, `boot:0x..` (strapping levels), `chip revision`, flash size line, `heap_init` / free heap.
- Always confirm the exact IDF target: `idf.py set-target esp32s3` must match the chip.

## Family comparison

| Chip | CPU / cores / max MHz | Wi-Fi | BLE / 802.15.4 | Native USB | GPIO | Touch | Use / choose when |
|---|---|---|---|---|---|---|---|
| ESP32 | Xtensa LX6, 2, 240 | Wi-Fi 4 (b/g/n) | BT classic + BLE 4.2 / no | no (needs bridge) | 34 usable (0-19,21-23,25-27,32-39) | 10 | cheapest all-rounder, BT classic audio, Ethernet RMII (internal MAC) |
| ESP32-S2 | Xtensa LX7, 1, 240 | Wi-Fi 4 | no BLE / no | USB OTG | 43 (0-21, 26-46) | 14 | Wi-Fi only + USB device, no BLE needed |
| ESP32-S3 | Xtensa LX7, 2, 240 | Wi-Fi 4 | BLE 5 / no | USB OTG + USB-Serial-JTAG | 45 (0-21, 26-48) | 14 | default for new work: PSRAM, camera/LCD, AI vector instr., USB |
| ESP32-C3 | RISC-V, 1, 160 | Wi-Fi 4 | BLE 5 / no | USB-Serial-JTAG | 22 (0-21) | no | cheap Wi-Fi+BLE nodes, low cost |
| ESP32-C6 | RISC-V HP 160 + LP core, 1+1 | Wi-Fi 6 (2.4 GHz) | BLE 5 / yes (Thread/Zigbee/Matter) | USB-Serial-JTAG | 31 (0-30) | no | Matter/Thread/Zigbee + Wi-Fi 6 |
| ESP32-H2 | RISC-V, 1, 96 | none | BLE 5 / yes | USB-Serial-JTAG | 28 (0-27) | no | Thread/Zigbee end device, no Wi-Fi |
| ESP32-C2 | RISC-V, 1, 120 (check datasheet) | Wi-Fi 4 | BLE 5 / no | no | check datasheet | no | lowest-cost Wi-Fi+BLE, small RAM/flash, limited features |
| ESP8266 (legacy) | Tensilica L106, 1, 80/160 | Wi-Fi 4 | no / no | no | ~17 (fewer usable) | no | legacy only; avoid for new designs; 1 ADC, 10-bit, 0-1.0 V range on bare chip (devkits add divider) |

- GPIO counts for S2/S3/C3/C6/H2 verified on ESP-IDF GPIO docs. Usable count is lower (flash/PSRAM/strapping/USB).
- ADC: classic ADC2 unusable while Wi-Fi is on (shared with Wi-Fi driver). Use ADC1 pins. Newer chips: ADC2 limited/conflicting with Wi-Fi too; prefer ADC1. ADC is non-linear: use calibration (`adc_cali`) and attenuation (ADC reads 0-~3.1 V at 12 dB; check datasheet).
- ADC1 pins: classic 32-39; S2/S3 GPIO1-10; C3 GPIO0-4; C6 GPIO0-6; H2 GPIO1-5. ADC2: classic 0,2,4,12-15,25-27; S2/S3 GPIO11-20; C3 GPIO5.

## Pin rules per chip

| Chip | Strapping pins | Do not use (flash/PSRAM) | Input-only | USB pins | Default UART0 (TX/RX) |
|---|---|---|---|---|---|
| ESP32 | 0, 2, 5, 12, 15 (12 = flash voltage: high on 3.3 V flash module = no boot; 0 low = download; 15 low = silent ROM log) | 6-11 (flash); 16, 17 on PSRAM modules (WROVER) | 34, 35, 36, 39 (verified: also 37, 38 listed as GPI in IDF docs; not on most modules). No internal pull-up/down | none | 1 / 3 |
| ESP32-S2 | 0, 45, 46 (+ check datasheet) | 26-32 (flash/PSRAM) | none | check datasheet (D-/D+ on GPIO19/20, check datasheet) | 43 / 44 (check datasheet) |
| ESP32-S3 | 0, 3, 45, 46 (0/46 verified in esptool docs; 3, 45: check datasheet) | 26-32; also 33-37 with octal flash/PSRAM (R8/R16 modules); 35-37 unusable on N16R8 | none | 19 (D-), 20 (D+) | 43 / 44 |
| ESP32-C3 | 2, 8, 9 (8, 9 verified; 2: check datasheet) | 12-17 (flash) | none | 18 (D-), 19 (D+) | 21 / 20 |
| ESP32-C6 | 4, 5, 8, 9, 15 (8, 9 verified; others from module datasheet) | 24-30 (flash) | none | 12, 13 | 16 / 17 |
| ESP32-H2 | 8, 9, 25 (chip datasheet v1.2; module sheet may list fewer, check datasheet) | 15-21 (flash) | none | 26 (D-?), 27 (check datasheet) | check datasheet |

- Common to all: GPIO0 (classic/S2/S3) or GPIO9 (C3/C6/H2) low at reset = ROM download mode. Never hang a load that pulls these at boot (relay, LED to GND, sensor output).
- Strapping pins are sampled at reset only; usable as GPIO afterwards, but external circuits must leave the right level at reset.
- Using USB pins as GPIO disables USB-Serial-JTAG (flashing then needs UART).
- Max current per GPIO: IDF drive strength steps nominally ~5 / 10 / 20 / 40 mA (`gpio_set_drive_capability`, default medium ~20 mA). Absolute max per pin and per chip: check datasheet. Drive LEDs/relays via transistor/MOSFET, not directly.
- ALL ESP32-family GPIO are 3.3 V logic and NOT 5 V tolerant. 5 V signal in: level shifter or divider. 5 V out to 3.3 V device: shifter.
- Boot messages: UART0 prints ROM log at 115200; classic GPIO15 low silences it.

## Memory and partition sizing

| Flash | Layout | Fits |
|---|---|---|
| 4 MB | Arduino `default.csv`: nvs 20 KB, otadata 8 KB, app0 0x140000 (1.25 MB), app1 1.25 MB, spiffs 0x160000 (1.375 MB) | OTA with app up to ~1.25 MB; Wi-Fi+MQTT+TLS+web server often 1.0-1.4 MB: tight |
| 4 MB, no OTA | `no_ota` / single factory ~2 MB | big app, no OTA (serial updates only) |
| 8 MB | two OTA slots 3 MB each + ~1.5 MB data (`default_8MB.csv`) | Wi-Fi + BLE + TLS + UI assets with OTA |
| 16 MB | two OTA slots 4-6 MB + large FFat/LittleFS (`default_16MB.csv`) | big web UI, audio, logs, models |

- Always put nvs, otadata, phy_init, two app slots; app slot size must be 64 KB aligned. Never change partition table via OTA (needs serial flash).
- Need PSRAM when: camera frames, LCD framebuffers, large JSON/audio buffers, many TLS connections, ML models. Internal SRAM (~320 KB classic/S3 data RAM, ~400 KB S3 total SRAM; check datasheet) is shared with Wi-Fi/BLE stacks.
- Typical free internal heap after Wi-Fi + TLS client + MQTT: roughly 100-200 KB on classic/S3 (approximate, not verified: measure with `esp_get_free_heap_size()` and `heap_caps_get_largest_free_block()`). One TLS session needs tens of KB contiguous (mbedTLS record buffers 16 KB in + 16 KB out by default; can be reduced). Watch the largest free block, not just total.
- C3/C2/H2 have less RAM (C3 ~400 KB total SRAM; check datasheet): Wi-Fi + BLE + TLS together is tight.

## Power figures (order of magnitude; exact values: check datasheet)

| State | Typical |
|---|---|
| Wi-Fi TX burst peak | 250-400 mA at chip level (incl. spikes); design supply for >= 500 mA |
| Wi-Fi RX / active idle | ~80-120 mA (CPU on) |
| Modem-sleep (Wi-Fi associated, DTIM) | ~15-40 mA |
| Light-sleep | ~0.3-1 mA |
| Deep-sleep | ~5-20 uA chip only (RTC timer); devkits 1-10 mA because of LED, bridge, regulator quiescent |

- 3V3 rail must source >= 500 mA (Espressif hardware design guideline recommendation) and stay above brown-out threshold (~2.5-3.0 V depending on setting) during 300 mA / microsecond-scale TX bursts.
- Bulk: 10 uF + 0.1 uF at module 3V3 pin; add >= 100 uF low-ESR near module for weak supplies, long USB cables, batteries (design practice). Thin USB cable + PC port = brown-out resets (`Brownout detector was triggered`).
- Regulators: AMS1117 dropout ~1.1 V; Li-ion 3.3 V rail needs LDO with low dropout or buck-boost. Check LDO quiescent current for sleep products.

## Other boards

| Board | MCU | Logic | Flash method | Choose instead of ESP32 when |
|---|---|---|---|---|
| Arduino Uno / Nano | ATmega328P, 16 MHz, 32 KB flash, 2 KB SRAM, 1 KB EEPROM | 5 V (I/O 5 V) | USB bridge + Optiboot, `avrdude` / Arduino IDE | 5 V shields/sensors, hard real-time, simplicity; no Wi-Fi; tiny RAM |
| Raspberry Pi Pico / Pico W | RP2040 dual Cortex-M0+ 133 MHz, 264 KB SRAM, 2 MB flash (Pico) | 3.3 V | hold BOOTSEL, drag-drop `.uf2`; SWD optional | PIO state machines (odd protocols), predictable timing, cheap; Pico W adds Wi-Fi 4 + BT (CYW43439) |
| Raspberry Pi 5 | Linux SBC (Arm Cortex-A76 quad) | 3.3 V GPIO, not 5 V tolerant | SD/NVMe image; no firmware flashing | Linux/camera/AI/DB/many services; not deep-sleep or battery; use `gpiod`/`lgpio` (RPi.GPIO does not work on Pi 5) |
| STM32 Blue Pill | STM32F103C8T6, Cortex-M3 72 MHz, 64 KB flash (many boards 128), 20 KB RAM | 3.3 V (some pins 5 V tolerant, check datasheet) | ST-Link SWD (best), or UART bootloader (BOOT0), USB DFU needs bootloader; clones vary | industrial I/O, CAN, deterministic timing, many timers; no radio |

## Picking a chip

- New Wi-Fi + BLE product with unknown needs: ESP32-S3 (PSRAM option, USB, most RAM).
- Lowest cost Wi-Fi/BLE node: ESP32-C3.
- Matter / Thread / Zigbee: ESP32-C6 (with Wi-Fi) or H2 (no Wi-Fi).
- Bluetooth classic (A2DP/SPP) or internal Ethernet MAC: classic ESP32 (S3/C3 have BLE only).
- Camera, display, audio, ML: ESP32-S3 with octal PSRAM (R8).
- 5 V I/O or hard real-time or no radio: Uno/Nano or STM32.
- Custom timing protocol via PIO: RP2040.
- Linux, many services, big storage: Raspberry Pi 5.
- Battery product: check deep-sleep current of the whole board, not the chip; avoid devkits.
