---
name: firmware-arduino
description: Arduino-framework and PlatformIO firmware for ESP32, ESP8266, AVR and RP2040 — quick prototypes, sensor sketches, library selection, platformio.ini setup, non-blocking code structure, and when to move to ESP-IDF. Use for Arduino IDE / arduino-cli / PlatformIO projects.
---

# Arduino / PlatformIO firmware

Pin and chip facts: see `references/chips.md`. Intake the exact module first.

## Arduino vs ESP-IDF

| Need | Pick |
|---|---|
| Prototype, one sensor, demo, existing Arduino library | Arduino (PlatformIO) |
| AVR / RP2040 / ESP8266 target | Arduino (only practical option) |
| Many modules, protocol stacks (Modbus+MQTT+OTA), reusable components | ESP-IDF |
| Fine control: partitions, power management, deep-sleep tuning, secure boot, flash encryption | ESP-IDF |
| Products with TLS-certificate bundle, esp_https_ota, eFuse, Ethernet W5500, 802.15.4 | ESP-IDF |
| Newest chips (C6/H2) | ESP-IDF, or Arduino core 3.x (see below) |

## PlatformIO layout

```
project/
  platformio.ini
  src/main.cpp            # setup()/loop() only, calls modules
  src/<module>.cpp
  include/config.h        # pins, timeouts, topics (no secrets in git)
  lib/<local_lib>/        # private libraries
  data/                   # LittleFS image: pio run -t uploadfs
  partitions.csv          # optional custom table
```

Minimal `platformio.ini` (ESP32-S3 devkit, 8 MB flash):

```ini
[env:esp32-s3-devkitc-1]
platform = espressif32
board = esp32-s3-devkitc-1
framework = arduino
monitor_speed = 115200
build_flags =
    -DARDUINO_USB_CDC_ON_BOOT=1   ; Serial over native USB port
    -DCORE_DEBUG_LEVEL=3
board_build.partitions = default_8MB.csv
board_build.flash_mode = qio
; N8R8 / octal PSRAM only:
; board_build.arduino.memory_type = qio_opi
lib_deps =
    knolleary/PubSubClient@^2.8
    bblanchon/ArduinoJson@^7.0.4
```

- Board id `esp32-s3-devkitc-1` has 8 MB flash, 320 KB RAM in PlatformIO (verified). Other flash sizes: set `board_upload.flash_size` and matching partitions file.
- `-DARDUINO_USB_CDC_ON_BOOT=1` is the equivalent of the Arduino IDE "USB CDC On Boot: Enabled": `Serial` then goes to USB CDC and `Serial0` is the hardware UART. Use it when the cable is in the S3 native USB port. If the cable is in the UART (bridge) port, leave it off.
- Pin library versions (`@^x.y.z` or exact `@x.y.z`). Never leave unpinned.
- Core version: the official PlatformIO `espressif32` platform ships Arduino core 2.x (ESP-IDF 4.4). Arduino core 3.x (ESP-IDF 5.x) historically needs the community `pioarduino` platform fork; check current PlatformIO announcements before choosing, it may have changed. C6/H2 need core 3.x.
- Commands: `pio run` build, `pio run -t upload` flash, `pio device monitor` serial, `pio run -t uploadfs` filesystem image, `pio device list` find port, `pio run -t clean`.
- Monitor filter for crashes: `monitor_filters = esp32_exception_decoder` (needs `build_type = debug` for useful symbols).

## arduino-cli equivalents

```
arduino-cli core update-index --additional-urls https://espressif.github.io/arduino-esp32/package_esp32_index.json
arduino-cli core install esp32:esp32 --additional-urls https://espressif.github.io/arduino-esp32/package_esp32_index.json
arduino-cli board details -b esp32:esp32:esp32s3        # lists option keys (CDCOnBoot, PSRAM, FlashSize, PartitionScheme)
arduino-cli compile --fqbn esp32:esp32:esp32s3:CDCOnBoot=cdc <sketchdir>
arduino-cli upload -p COM5 --fqbn esp32:esp32:esp32s3:CDCOnBoot=cdc <sketchdir>
arduino-cli lib install "ArduinoJson@7.0.4"
arduino-cli monitor -p COM5 -c baudrate=115200
```

Confirm option values with `board details`; do not guess them.

## Code structure rules

- No `delay()` in `loop()`. Use `millis()` timers and a state machine:
  `if (millis() - last >= PERIOD_MS) { last += PERIOD_MS; ... }` (subtraction form survives millis() rollover at ~49.7 days; use `uint32_t`).
- One module = one `.h` + `.cpp` pair (`wifi_mgr`, `mqtt_mgr`, `sensors`). `main.cpp` only calls `begin()` and `tick()`.
- All pins, timeouts, topics, buffer sizes in one `config.h`. Secrets in an untracked `secrets.h`.
- Log with tags: `Serial.printf("[MQTT] connect rc=%d\n", rc);`. Gate with a log-level macro.
- Wi-Fi / MQTT reconnect: non-blocking, exponential backoff (1 s, 2 s, 4 s ... cap 60 s), reset backoff on success. Never `while(WiFi.status()!=WL_CONNECTED) delay(500)` forever.
- Watchdog: ESP32 `esp_task_wdt_init` / `esp_task_wdt_add(NULL)` / `esp_task_wdt_reset()` (API signature differs between core 2.x and 3.x, check the core in use); ESP8266 `ESP.wdtFeed()`; AVR `avr/wdt.h`. Reboot on stuck state.
- Settings (Wi-Fi creds, thresholds) in `Preferences` (NVS) on ESP32, `EEPROM`/LittleFS on ESP8266/AVR. Do not write flash in a fast loop (wear).
- ISRs: short, no `Serial`, no `delay`, no heap allocation, no Wi-Fi/MQTT calls. Set a `volatile` flag, handle it in `loop()`. On ESP32 mark `IRAM_ATTR`. Shared multi-byte variables: protect with `portENTER_CRITICAL`/spinlock or `std::atomic`.
- Prefer fixed `char buf[N]` + `snprintf` to `String`.
- Check every return value (`WiFi.begin`, `client.connect`, file open, JSON deserialize).

## Solid libraries

| Library | Use for | Pitfall |
|---|---|---|
| PubSubClient | MQTT client, simple | Default packet size 256 B: `setBufferSize()`; `loop()` must run often; blocking connect; QoS 0/1 only |
| AsyncMqttClient | MQTT non-blocking | Needs AsyncTCP; callbacks run in async task, no blocking inside |
| ArduinoJson (v7) | JSON parse/build | v6 vs v7 API differ (`JsonDocument` vs `StaticJsonDocument`); allocate/clear docs outside hot loops |
| WiFiManager | captive-portal Wi-Fi setup | Blocks in `autoConnect` unless `setConfigPortalBlocking(false)`; check core compatibility |
| ModbusMaster | Modbus RTU master (AVR/ESP) | Must drive RS-485 DE/RE via `preTransmission`/`postTransmission` callbacks |
| modbus-esp8266 (emelianov) | Modbus RTU/TCP master/slave on ESP | Same DE/RE care; poll loop `task()` must be called |
| IRremoteESP8266 | IR send/receive/decode | Large RAM use for decode-all; enable only needed protocols |
| OneWire + DallasTemperature | DS18B20 | 85.0 C = power-on default/failed read; `-127` = disconnected; use `setWaitForConversion(false)` to avoid ~750 ms block; 4.7 kohm pull-up |
| Adafruit Unified Sensor + device libs (BME280, ADS1x15 ...) | I2C/SPI sensors | Check I2C address (0x76/0x77); default `Wire` pins differ per chip: call `Wire.begin(SDA,SCL)` |
| U8g2 | monochrome OLED/LCD | Full-buffer mode uses lots of RAM on AVR; use page mode |
| FastLED / Adafruit NeoPixel | WS2812 | Timing-sensitive; interrupts off during show; use RMT/I2S driver on ESP32 to avoid Wi-Fi glitches |
| ESPAsyncWebServer (mathieucarbou fork preferred) | web UI/REST | Original is unmaintained; do not block or free resources in handlers; needs AsyncTCP |
| ArduinoOTA | OTA over LAN | No auth by default: `setPassword()`; port 3232 on ESP32; mDNS/firewall issues |
| LittleFS | files on ESP flash | Must match partition table; format on first mount fail; SPIFFS is deprecated |

## TLS on Arduino-ESP32

- Use `WiFiClientSecure`. `client.setCACert(root_ca_pem)` to validate; `setInsecure()` only for tests, never ship.
- System time must be set BEFORE connecting or certificate validation fails: `configTime(0, 0, "pool.ntp.org")` then wait until `time(nullptr) > 1700000000`.
- Root CAs expire/rotate: pin the root CA, not the leaf; plan OTA updates for it.
- mTLS: `setCertificate()` / `setPrivateKey()`. TLS needs large contiguous RAM: log `ESP.getMaxAllocHeap()` before connecting.
- PubSubClient over TLS: `PubSubClient mqtt(secureClient)`, port 8883.

## OTA options

| Option | Notes |
|---|---|
| ArduinoOTA | LAN push from IDE/`pio run -t upload --upload-port <ip>` (`upload_protocol = espota`); set password |
| `HTTPUpdate` / `httpUpdate.update(client, url)` | pull from HTTPS server; needs two OTA slots in partitions; verify TLS |
| Web upload (`Update.h`) | browser upload page; authenticate it |
| Rollback | Arduino support limited; use ESP-IDF `esp_ota_mark_app_valid_cancel_rollback` if rollback needed |

## Common pitfalls

- `String` concatenation in loops fragments the heap: reserve (`s.reserve(n)`) or use `char[]`.
- ADC2 pins unusable while Wi-Fi is on (classic ESP32): use ADC1 pins.
- Brownout / reset loops on USB power: bad cable, weak port; add bulk capacitor, check `Brownout detector` in log.
- Wrong board or partition scheme selected: sketch too big, OTA fails, PSRAM not found. Match the chip, flash size and PSRAM type.
- Native-USB boards (S2/S3/C3/C6/H2): `Serial` prints nothing without CDC-on-boot (`ARDUINO_USB_CDC_ON_BOOT=1`); port renumbers on reset, reconnect the monitor.
- `millis()` math: use `uint32_t` and subtraction, never `now > last + period`.
- 5 V sensors/modules on 3.3 V pins: not 5 V tolerant. Use level shifter or 3.3 V parts.
- Strapping pins (GPIO0/2/12/15 on classic, GPIO0/3/45/46 on S3) driven by peripherals at boot prevent boot.
- Pin numbers: Arduino `D` labels differ from GPIO numbers on some boards; use GPIO numbers from the pinout.
- Mixing core 2.x and 3.x code: LEDC (`ledcSetup/ledcAttachPin` vs `ledcAttach`) and WDT APIs changed.

## Migrating a sketch to ESP-IDF (checklist)

- Create the project with `idf.py create-project`; add Arduino as a component only as a temporary bridge, then remove it.
- Replace `setup()/loop()` with `app_main()` plus FreeRTOS tasks (`xTaskCreate`), one per module.
- Map `Serial.printf` to `ESP_LOGI/W/E(TAG, ...)`; keep the same tag names.
- Replace `millis()` timers with `esp_timer` or `vTaskDelay`/`xTaskDelayUntil`.
- Replace `Preferences` with `nvs_flash` + `nvs_*` calls.
- Replace `WiFi.*` with `esp_netif` + `esp_wifi` + event loop; replace `PubSubClient` with `esp-mqtt`; `WiFiClientSecure` with `esp-tls` / cert bundle.
- Replace `HTTPUpdate` with `esp_https_ota`; define the OTA partition table in `partitions.csv`.
- Replace `LittleFS` with `esp_littlefs` component; replace Arduino `Wire/SPI` with `i2c_master`/`spi_master` drivers.
- Pull third-party libraries from the ESP Component Registry (`idf.py add-dependency`), or port source as components.
- Move settings to `sdkconfig.defaults` (flash size, PSRAM mode, partition table, log levels); rebuild from clean.

**Knowledge base:** if `~/.claude/workspace-registry.txt` exists, first look up the owner's hardware, installed tools, preferences and past lessons in `<that path>/knowledge/` (start at `INDEX.md`) yourself with Grep (no agent spawn), ask only what is missing, never reinstall what the registry shows as installed, and write new facts back with `shreyas-workspace-replicate:kb`.
