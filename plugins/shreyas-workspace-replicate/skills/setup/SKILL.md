---
name: setup
description: Rebuild the whole development workspace on a new or wiped machine (/shreyas-workspace-replicate:setup) — Windows, macOS or Linux. Reads the tool and project registry, asks full or selective install, installs toolchains, CLIs, Claude plugins/skills/MCP servers, walks through each login once, clones chosen projects and verifies everything. Use on a fresh machine or to add a missing category to this one.
argument-hint: "[full | selective | claude-only]"
---

Plugin root: `${CLAUDE_PLUGIN_ROOT}`

## 0. Find the registry
The registry is the folder `plugins/shreyas-workspace-replicate/registry/` inside the skills repo: `tools.yaml` (every tool), `projects.md` (every project's stack), `claude-setup.md` (Claude Code side), `machines.md` (setup history).

- `~/.claude/workspace-registry.txt` holds the local path of the skills repo. If it exists, `git pull` there and use it.
- If not: ask the owner for the skills repo URL (or read it from `claude plugin marketplace list`), clone it to `~/Projects/`, and write its path into `~/.claude/workspace-registry.txt`.
- Fallback for reading only: `${CLAUDE_PLUGIN_ROOT}/registry/`.

## 1. Look at the machine (haiku agent, read-only)
OS and version, CPU architecture, package manager (winget / brew / apt / dnf / pacman), shell, free disk, and for every `tools.yaml` entry whether it is already installed and at what version. Return one table. Nothing is installed in this step.

## 2. Ask (AskUserQuestion, at most two rounds)
1. Mode: **Full** (everything `active`) · **Selective** (choose categories) · **Claude only** (plugins, skills, MCP, settings).
2. Selective → multi-select of categories with tool counts: core, claude, embedded, web, python, video, ai-local, automation, eda, other.
3. For every tool with `status: legacy` or `replaced`: **do not install by default.** Ask one question listing each with its replacement ("PlatformIO — replaced by ESP-IDF; only old projects use it. Install?"). Never install both sides of a replacement without a yes.
4. Which projects to clone: ongoing ones (default), all, or none — from `projects.md`. Add the toolchains those projects need to the install set.
5. A short label for this machine (for `machines.md`).

## 3. Plan and approve
Show one table per category: tool, command for this OS, size/time if known. Rules:
- Take the command from `install.<os>`. A command starting with `UNVERIFIED:` must be checked first (`winget search`, `brew info`, `apt-cache policy`, or the tool's official install page) and corrected in `tools.yaml` afterwards.
- Prefer the system package manager; otherwise the vendor's official installer. Never run an install script from an unofficial source.
- Skip what step 1 found installed at an acceptable version.
- One approval per category before anything runs.

## 4. Install in this order
1. **core** — git, GitHub CLI, Node, Python, package runners.
2. **Logins** (step 5) that later steps need.
3. **claude** — follow `claude-setup.md`: add the marketplace(s), install plugins, copy personal skills, MCP servers, global `CLAUDE.md`, non-secret settings, hooks. Write `~/.claude/workspace-registry.txt`.
4. Remaining categories. Long installs (ESP-IDF, Docker, model downloads) run in the background; give each category to a haiku agent with the exact approved command list; it reports tool / version / ok or the error. Do not let an agent improvise commands.
5. Apply each tool's `post_install` (PATH, env var names, drivers, udev rules on Linux for serial ports, dialout group).
6. Clone the chosen projects into `~/Projects/` with the right account (the `gitcp` skill handles the two-account setup); then per project install its dependencies only if the owner asked for a ready-to-run state.

## 5. Logins — the owner does each one, once
List every entry whose `login` is not `none`, then walk through them one at a time: print the command, the owner completes it in the browser/terminal, you confirm with a harmless check (`gh auth status`, `wrangler whoami`).
- You never type, ask for, store or echo a password, token or key. Nothing secret goes into the registry or any repo.
- Typical set: GitHub (each account), Claude connectors via `/mcp`, Cloudflare (`wrangler login`), Supabase, any cloud or broker accounts the chosen projects use.
- Secrets that lived only on the old machine (`.env`, `sdkconfig.local`, certificates, SSH keys) are not in git: show the list of names the last backup recorded in `machines.md` and ask the owner to bring them over by their own secure means.

## 6. Verify
Per category run a smoke check and show a final table (tool, expected, found, ok): versions print; `idf.py --version` and, if embedded was chosen, one tiny build; `node -v`; `python --version`; `claude plugin list` shows the plugins; `opencode run` answers; a serial port is visible when a board is plugged in (ask the owner to plug one in).
List what failed with the exact error and the next action. Do not report success for anything not checked.

## 7. Record
Append to `registry/machines.md`: date, machine label, OS, mode, categories installed, failures, corrected commands. Commit and push the registry (`gitcp`). Fix any `tools.yaml` command that turned out wrong on this OS so the next setup is faster.
