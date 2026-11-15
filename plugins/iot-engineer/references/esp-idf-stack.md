# ESP-IDF stack — how to build it from scratch

A reusable component stack where a **product = app module + the modules it needs + ~20 lines of glue**.
`<px>` below is a short project prefix (2–3 letters). Baseline this was proven on: ESP32-S3 N8R8, ESP-IDF v5.5.x, plain C, Windows.

## 1. Repo layout

```
components/            one folder per module
  <px>_core/           CRC, uptime, shared-resource ownership (e.g. radio mode)
  <px>_rs485/ <px>_i2c/ <px>_eth/ <px>_lora/ ...   board buses — pins in Kconfig only
  modbus/              protocol family: <px>_modbus (common), _rtu, _tcp_client, _tcp_server, _rtu_server
  bacnet/              <px>_bacnet (core), _ip, _mstp
  <px>_nvs/ <px>_fs/ <px>_config/ <px>_time/ <px>_mqtt/ <px>_store/ <px>_ota/   services
  <px>_web/ <px>_web_<page>/   HTTP server + one component per page
  <px>_net/ <px>_app/  glue: uplink selection, standard startup
third_party/           upstream libraries, unmodified, version pinned
apps/
  template/            copy this to make a product
  buildcheck/          references EVERY module; must always build clean
  <product>/           real products and examples
tests/host/            PC tests of pure logic      tests/hil/   simulators and bench scripts
tools/                 build.ps1, idf.ps1, serial and NVS helpers
docs/                  ARCHITECTURE, COMPONENTS, NVS, WIRING, ROADMAP, one doc per module
AGENTS.md HANDOFF.md CLAUDE.md(one line: "read AGENTS.md")
```

## 2. Architecture rules

- A module depends on `<px>_core` + IDF only. **Feature modules never include each other.** Glue lives in `*_web`, `<px>_net`, `<px>_app` or the app.
- Modules talk through the default event loop, each under its own event base.
- **One owner per shared resource** (radio mode, Wi-Fi station, HTTP server, each SPI/UART bus). A bus component defines channels once; protocol modules *claim* a channel. Two modules claiming one pin = build error.
- Name a module after the protocol or function, not the product role.
- API style: `<px>_<mod>_<verb>()`, returns `esp_err_t`, uses `ESP_RETURN_ON_*`, `NULL` config = defaults.
- Everything tunable is a Kconfig option under `menu "<Project>: <name> (<px>_<name>)"`. Pins and chip options live in the app's `Kconfig.projbuild` + `sdkconfig.defaults`, never in code.
- Only one uplink active at a time (Ethernet, Wi-Fi or cellular). A setup AP stays up whenever nothing else is connected.
- Budget shared pools explicitly: sockets per module, task stacks, heap.

## 3. Component template

```
<px>_<name>/
  include/<px>_<name>.h   the ONLY public header — write it first, fully commented; it is the doc
  <px>_<name>.c           private implementation (IDF-facing)
  <px>_<name>_core.c      pure logic, NO IDF includes (parse/codec/state machine) → host-testable
  Kconfig                 menu with every tunable
  CMakeLists.txt          idf_component_register(SRCS ... INCLUDE_DIRS "include"
                                                 REQUIRES ... PRIV_REQUIRES <px>_core ...)
  www/                    only in *_web components; pages embedded gzip'd
```

Third-party code: vendor it unchanged into `third_party/` at a pinned version, write a thin `<px>_*` wrapper, and set `IDF_COMPONENT_MANAGER=0` in every app so builds never download. (For a quick personal project, `idf_component.yml` + the registry is fine — pin exact versions.)

## 4. App template

```
apps/<app>/
  CMakeLists.txt        EXTRA_COMPONENT_DIRS = components, components/modbus, components/bacnet, third_party
                        PROJECT_VER; load gitignored sdkconfig.local over sdkconfig.defaults;
                        IDF_COMPONENT_MANAGER=0; project()
  main/CMakeLists.txt  main/Kconfig.projbuild  main/main.c   (≈20 lines: <px>_app_start + module inits)
  partitions.csv        sdkconfig.defaults
```

`sdkconfig.local` holds bench-only overrides (laptop broker, test Wi-Fi). Never commit it.

## 5. Storage, config, OTA

- **Settings → NVS**, through one wrapper, one namespace per module. Every key declared in a table (`name, type, default`); undeclared or wrong-type access is refused; a boot audit logs stray keys. Never reuse or retype a key. `docs/NVS.md` is the record.
- **Documents → files** on LittleFS (big JSON such as a register map): validate → write temp → atomic rename → apply. A bad file never replaces a good one.
- Turn off IDF's own NVS users (`CONFIG_ESP_WIFI_NVS_ENABLED=n`, `CONFIG_ESP_PHY_CALIBRATION_AND_DATA_STORAGE=n`) so an NVS image is portable between units.
- Fixed per-product settings (broker, TLS, radio) go in Kconfig and are shown read-only in the UI.
- **Partitions:** if units already in the field must be updated over the air, keep the partition table byte-identical to what they run. Typical 8 MB: nvs, otadata, two app slots, a data partition for LittleFS, coredump.
- **OTA checks before writing:** image magic, chip id, app image (not a full-flash image), same `project_name`, fits the slot. Switch slot only after IDF's SHA-256 check passes. If the bootloader in the field has rollback enabled, mark the image valid at boot.
- After any OTA during development, flash the **full** `@flash_args` set (it includes `ota_data_initial.bin`), or the old slot keeps booting.

## 6. Build, flash, test (Windows)

- `tools/idf.ps1`: sets `IDF_PATH`, dot-sources `export.ps1`, `cd`s to the app, runs `idf.py`.
- `tools/build.ps1 <app>`: runs the build and prints only lines matching
  `error:|undefined reference|warning: |CMake Error|Project build complete|region .* overflowed`, then `build exit code: N`. This filter is what keeps build logs out of the context window.
- Run: `powershell -ExecutionPolicy Bypass -File tools\build.ps1 <app>` — 3–5 min, use a 900000 ms timeout or run in the background.
- New Kconfig symbol "not found" → delete `apps/<app>/sdkconfig` and rebuild.
- **Host tests:** `tests/host/run.sh` compiles each `test_*.c` with host `gcc` + the module's pure `.c` files + small stubs (`stubs/host_compat.h`). Run in Git Bash with a short `TMPDIR`. Every module with logic gets one.
- **Flash:** from the app's `build/`: `python -m esptool --chip esp32s3 -p COMxx -b 921600 write_flash @flash_args`.
- **Serial without resetting the board:** set `rts=False; dtr=False` before opening the port.
- Tools worth writing early: one-shot console command sender, serial logger (no reset), serial OTA (size → baud switch → CRC'd blocks with ACK/NAK) for boards whose download mode is unusable, NVS image read/write, a mock `/api` server so the web UI is testable with no board.
- NVS provisioning image: `nvs_partition_gen.py generate unit.csv unit.bin 0x5000`.
- A serial console on the test app (`status`, `points`, `mode wifi|ethernet|cellular`, `wifi scan|join`, `restart`) pays for itself on day two.

## 7. What to use for what

| Need | Use |
|---|---|
| Wi-Fi STA/AP, captive portal | IDF `esp_wifi` + IDF example `dns_server` |
| HTTP server / REST | IDF `esp_http_server` |
| Ethernet W5500 | IDF `esp_eth` (see gotchas: SPI pins, INT, RX recovery) |
| Cellular PPP | `espressif/esp_modem` |
| MQTT (TLS, mTLS, v5) | IDF esp-mqtt + esp-tls |
| Time | IDF `esp_netif_sntp`; HTTP `Date` fallback; optional I2C RTC |
| OTA | IDF `app_update` (+ `esp_https_ota` for pull) |
| Modbus RTU/TCP master and slave | `espressif/esp-modbus` |
| BACnet/IP, MS/TP | bacnet-stack (vendored) + own datalink port for lwIP/UART |
| LoRa SX126x | Semtech `sx126x_driver` |
| Buttons, LEDs | `espressif/button`, `espressif/led_indicator`, `led_strip` |
| Filesystem | `joltwallet/littlefs` |
| Settings | IDF `nvs_flash` behind the wrapper |
| Arduino/PlatformIO prototypes | PubSubClient, WiFiClientSecure, IRremoteESP8266, ModbusRTU |

Check the current version and API in the component's docs before use — do not trust remembered signatures.

## 8. Build order for a new stack

1. `tools/` build scripts + `apps/template` + `apps/buildcheck` + `<px>_core`. Prove: clean build, blink, log.
2. Storage: `<px>_nvs`, `<px>_fs`, `<px>_config`.
3. Buses the product needs (`rs485`, `i2c`, SPI devices) — each with a tiny test app.
4. Link: Wi-Fi + setup AP, then Ethernet/cellular, then `<px>_net` uplink selection.
5. `<px>_time`, then `<px>_mqtt` (TLS needs valid time first).
6. `<px>_web` + pages, `<px>_ota`.
7. Protocol families (Modbus, BACnet…) against simulators, then real devices.
8. `<px>_app` standard startup, then product apps as glue.
9. `AGENTS.md`: a "needs X → use module Y" table, the copy-the-template recipe, non-negotiable rules, and a "before you say done" checklist — so a smaller model can assemble products.
