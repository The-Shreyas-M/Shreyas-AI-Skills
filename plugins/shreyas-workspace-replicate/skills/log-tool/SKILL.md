---
name: log-tool
description: Record a newly installed or newly used tool, SDK, toolchain, driver, CLI, MCP server or skill in the workspace registry (/shreyas-workspace-replicate:log-tool), with which project needed it and why, then push. Project orchestrators call this every time something is installed, so a new machine can be rebuilt from the registry. Also registers a new project's stack.
argument-hint: "<tool or project> [why]"
---

This is a small bookkeeping job: give it to a haiku agent with the facts below filled in; check its diff; do not spend main-model tokens on the edit.

Facts to collect first (from the session, not guessed): tool name, exact version (`--version`), the exact install command that was run on this OS, what it is for, which project needed it, any post-install step or login, and whether it replaces something.

Steps for the agent:
1. Registry path: read `~/.claude/workspace-registry.txt` → `<repo>/plugins/shreyas-workspace-replicate/registry/`. Missing file → update only the project's `docs/TOOLCHAIN.md` and say so.
2. `git pull` in the repo.
3. `tools.yaml`: if an entry with this `id` exists, update `version_seen` and add the project to `used_by`; otherwise append a full entry in the existing format (`category`, `purpose`, `install` for this OS — other OSes `UNVERIFIED: <best guess>`, `post_install`, `login`, `used_by`, `status: active`, `added: <today>`, `source: "<project>, <today>"`).
4. Replacement: if this tool replaces another, set the old entry's `status: legacy` and `replaced_by: <new id>`. Never delete entries.
5. `projects.md`: add or update the project's block (type, status, stack, toolchain, runs).
6. Project repo: add the row to its `docs/TOOLCHAIN.md` (no commit there unless the project's rules allow it).
7. Commit only the registry files with message `registry: <tool> for <project>` and push with the `gitcp` skill.
8. Report ≤60 words: entries added/updated, push result.

Never write secrets, tokens, emails or account names into the registry. Record only that a login is needed.
