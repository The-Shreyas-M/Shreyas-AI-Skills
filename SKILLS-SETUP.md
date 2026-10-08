# AI-Skills Setup

These are the skills Shreyas uses for his CLI coding setup, commands to install are:

```bash
npx skills add https://github.com/anthropics/skills --skill frontend-design
npx skills add https://github.com/browser-use/browser-use --skill browser-use
npx skills add https://github.com/vercel-labs/skills --skill find-skills
npx skills add https://github.com/graphify-labs/graphify --skill graphify
npx skills add https://github.com/adamlipecz/esp32-firmware-engineer-skill --skill esp32-firmware-engineer
npx skills add https://github.com/jeffallan/claude-skills --skill embedded-systems
npx skills add https://github.com/microsoft/playwright-cli --skill playwright-cli
npx skills add https://github.com/OthmanAdi/planning-with-files --skill planning-with-files
npx skills add https://github.com/nextlevelbuilder/ui-ux-pro-max-skill --skill ui-ux-pro-max
npx skills add https://github.com/The-Shreyas-M/Shreyas-AI-Skills --skill gitcp
```

Requires Node.js ≥ 18 (`npx`). Verify with `npx skills list`.

## What each skill does

- **frontend-design** — distinctive visual design guidance, avoids templated output
- **browser-use** — direct browser control: automation, scraping, screenshots
- **find-skills** — discovers and installs skills from the ecosystem
- **graphify** — builds knowledge graphs from codebases/docs
- **esp32-firmware-engineer** — ESP-IDF firmware: FreeRTOS, peripherals, Wi-Fi/BLE
- **embedded-systems** — microcontroller firmware: STM32, ESP32, bare-metal
- **playwright-cli** — browser automation and Playwright testing
- **planning-with-files** — file-based planning for multi-step agent work
- **ui-ux-pro-max** — UI/UX design intelligence: palettes, fonts, guidelines
- **gitcp** — commit/push to the right GitHub account (personal vs college): auto-detects from the repo remote, asks only when unsure, uses per-command tokens instead of switching `gh` globally

## Making skills show up in Claude Code

`npx skills` installs into `~/.agents/skills/`, which Claude Code does not read. Link each skill into `~/.claude/skills/` (PowerShell, no admin needed):

```powershell
Get-ChildItem ~\.agents\skills -Directory | ForEach-Object {
  $p = "$HOME\.claude\skills\$($_.Name)"
  if (-not (Test-Path $p)) { New-Item -ItemType Junction -Path $p -Target $_.FullName }
}
```

Restart Claude Code afterwards. Extras: `claude mcp add -s user playwright -- npx -y @playwright/mcp@latest` and `uv tool install browser-use`.
