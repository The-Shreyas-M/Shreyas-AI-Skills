## IoT / hardware

- **Board and parts:** exact MCU/module (e.g. ESP32-S3 N8R8), devkit or custom PCB, and every sensor/actuator/transceiver with part numbers. What do you physically have on the desk right now?
- **Framework:** ESP-IDF (default for products) / Arduino-PlatformIO (quick prototypes) / other. IDF version.
- **Connectivity:** Wi-Fi, Ethernet, BLE, LoRa, cellular? Station or AP? Provisioning method?
- **Buses and protocols:** RS-485 (Modbus RTU / BACnet MS-TP), BACnet/IP, Modbus TCP, MQTT (broker? TLS? mutual TLS?), HTTP/REST, I2C, SPI, 1-Wire, IR, CAN. For each: master or slave, baud/address, how many devices.
- **Power:** USB, mains, battery? Sleep requirements and target battery life?
- **Pins:** any pins already fixed by the board? Strapping/USB/PSRAM pins to avoid?
- **Device behaviour:** what happens on boot, on network loss, on sensor failure, on power cut? Local control without cloud?
- **Config:** how does a field technician set it up — web page on the device, BLE app, serial, hard-coded?
- **Data:** what is measured or controlled, how often, where it goes, how long it is stored on the device?
- **Updates:** OTA needed? From where? Rollback?
- **Time:** needs real time? NTP, RTC chip, time zone?
- **Scale:** one device or a fleet? Unique identity and per-device credentials?
- **Bench:** what test gear do you have (USB-RS485 dongle, logic analyser, multimeter, second devkit)? What can only you test?
- **Deliverable:** firmware only, or also a dashboard/app/backend? Hand-over to a company?

