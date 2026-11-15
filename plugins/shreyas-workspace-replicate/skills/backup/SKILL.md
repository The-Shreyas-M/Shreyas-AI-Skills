---
name: backup
description: Force a complete record of this machine's workspace before switching laptops (/shreyas-workspace-replicate:backup) — rescans every installed tool and every project's toolchain, updates the registry, lists unpushed work and secret files that are not in git, and pushes the registry. Use before changing or wiping a machine, or periodically so nothing goes untracked.
---

Registry: the skills repo path is in `~/.claude/workspace-registry.txt`; the files are in `plugins/shreyas-workspace-replicate/registry/`. `git pull` first.

Run the scans as cheap parallel agents (haiku unless stated); you merge, check and report. Agents never print or record secrets, tokens, emails or account names.

## 1. Tools on this machine
Scan package managers, global npm/pip/pipx/cargo packages, SDKs and toolchains (ESP-IDF, Arduino cores, PlatformIO), editors and their extensions, drivers, CLIs, local AI runtimes and models, EDA and bench software. Compare with `tools.yaml`:
- new tool → add a full entry (`source: "backup scan <date>"`); ask the owner "what is this for?" in one batched question for any whose purpose is unclear;
- known tool → update `version_seen`;
- in the registry but no longer installed → keep the entry, add `note: not found on <date>`; never delete.
A sonnet agent does the YAML merge; validate that the file still parses.

## 2. Projects
For every folder in `~/Projects`: read `docs/TOOLCHAIN.md`, manifests and `git log -1`. Update its block in `projects.md` (add new projects, refresh status and last commit). Merge every tool named there into `tools.yaml` `used_by`. Ongoing projects without `docs/TOOLCHAIN.md` or the Toolchain log block get them (documentation files only; no commits in project repos).

## 3. Replaced technology
Where a project moved to a newer tool (e.g. an Arduino core replaced by ESP-IDF), mark the old tool `status: legacy`, set `replaced_by`, and keep it — setup will ask before installing it.

## 4. Claude side
Refresh `claude-setup.md`: marketplaces, plugins, personal skills, MCP server names and launch commands, hooks, global `CLAUDE.md` text, non-secret settings.

## 5. What would be lost — report, do not fix silently
- Repos with uncommitted changes, unpushed commits, unpushed branches, stashes, or no remote at all.
- Project folders that are not git repos.
- Files that matter but are deliberately not in git: `.env*`, `sdkconfig.local`, certificates and keys, `.gitcp.md`, local databases, large media, skill workspaces and memory folders under `~/.claude`. Record **names and locations only** in `machines.md` under "Carry over by hand".
Ask the owner what to commit/push; never push a project repo or copy a secret on your own.

## 6. Save
Update `machines.md` (date, machine label, counts, the carry-over list). Commit and push the registry with `gitcp`. Confirm the push by `git status -sb`.

## 7. Report (short)
Tools added / updated / missing; projects added / updated; items at risk from step 5; anything a scan could not determine. State plainly what was not checked.
