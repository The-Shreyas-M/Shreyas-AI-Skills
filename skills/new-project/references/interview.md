# Interview question bank

Ask the **Core** set for every project, then the set for the project type.
Group into rounds of 3–4. Offer a recommended default for each choice. Skip
anything already known. If the owner says "you decide", decide, and record it
under Assumptions in SPEC.

## Core (all projects)

**Purpose**
- Who uses it, and what are they doing today instead?
- What is the one thing it must do well? What does "it works" look like in a 2-minute demo?
- Is this for you, a client/company, college, or a product to sell? (Decides polish, licensing, which GitHub account, and whether code may be sent to free models.)

**Scope**
- List every feature you imagine. For each: Must for v1 / Should / Later.
- What is explicitly NOT part of this? (Write at least three non-goals.)
- Is there an existing project, repo or product to copy the behaviour or look of?

**Constraints**
- Deadline or demo date? Hours per week you can give to checkpoints?
- Budget: any paid services allowed, or free tiers only?
- Anything already decided and not open for debate (stack, hosting, parts, libraries)?
- Secrets/accounts needed (API keys, cloud accounts)? Who creates them?

**Quality bar**
- Prototype, demo-ready, or production? Who maintains it after you?
- Tests: none / smoke checks / real test suite?
- Any security or privacy sensitivity (logins, personal data, payments)?

**Working style**
- When should I stop and ask you: end of each sprint (default), or only at version milestones?
- Commit policy: commit per task and push at each checkpoint (default), or no push until you say?
- Will the code be handed to someone else (company, teammate)? If yes, what docs do they need?

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

## Web app

- **Users and auth:** public, login required, roles? Sign-in method (email link, Google, none)?
- **Pages/flows:** walk me through each screen from landing to done. Which is the main one?
- **Data:** what is stored, who owns it, rough size? Database (Supabase / Cloudflare D1 / none)?
- **Stack:** Next.js + Tailwind (default for apps) / React + Vite / static HTML (default for content sites)? Any reason to differ?
- **Hosting:** Cloudflare (default) — Pages/Workers? Custom domain?
- **Design:** reference sites you like, brand colours/fonts, light/dark, tone. Mobile-first or desktop-first?
- **Content:** who writes text/images? Do you have them now?
- **Integrations:** payments, email, AI APIs, maps, analytics, third-party APIs?
- **Realtime / offline / SEO:** any of these required?
- **Admin:** do you need an admin view or is editing files enough?
- **Launch:** who must approve before it goes public?

## Local app / tool

- **Runs where:** this Windows machine only, or others too? CLI, desktop window, local web UI, background service?
- **Language:** Python (default) / Node / other? Any required libraries?
- **Inputs/outputs:** files, folders, APIs, browser automation, devices? Example input and expected output.
- **Run pattern:** on demand, scheduled, always on? How is it started (double-click `run.bat`, command)?
- **Accounts/credentials** it must use, and where they are kept (never in the repo).
- **Failure:** what should happen when a step fails — retry, skip, stop and notify?
- **Packaging:** just a venv + run script (default), or an installer/exe?

## Video / content

- What footage or script exists, target platform and length, style reference, posting schedule. Then hand over to the `ai-video` skill — it has its own interview.

## Something else

Ask: what is the deliverable (file, service, document, model)? How will you
judge it finished? What does it take as input? Then use the closest set above.

## Closing round (always)

- "Anything you are worried about or that went wrong on a similar project?"
- Read back v1 in five bullets plus the non-goals. Ask what is wrong or missing.
