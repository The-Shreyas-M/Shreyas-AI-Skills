---
name: adopt
description: Bring an existing or half-built project under the same workflow (/new-project:adopt). Reads what is there, asks only what is missing, then adds SPEC, TODO sprints, HANDOFF, WORKFLOW, TOOLCHAIN and the cheap subagents without disturbing the code. Use for old or ongoing repos that were started without /new-project.
argument-hint: "[project folder]"
---

Plugin root: `${CLAUDE_PLUGIN_ROOT}`

1. **Survey cheaply.** Send a haiku agent to read README, CLAUDE.md/AGENTS.md, HANDOFF/TODO/ROADMAP, manifests and `git log --oneline -30`, and report in ≤250 words: what it is, stack, what works, what is unfinished, existing docs and rules. Do not read source yourself.
2. **Ask only the gaps** from `${CLAUDE_PLUGIN_ROOT}/references/interview-core.md` and the type file: what "done" means now, Must/Should/Later for the remaining work, non-goals, checkpoint and commit policy, confidentiality.
3. **Add, never overwrite.** Copy from `${CLAUDE_PLUGIN_ROOT}/template` only the files that do not exist (`cp -n`; `dot-claude` → `.claude`). Existing CLAUDE.md/AGENTS.md/HANDOFF.md/TODO.md keep their content and rules: append a short "Start here" pointer to `docs/WORKFLOW.md` and the Toolchain log block from the template's `CLAUDE.md`. Existing project rules win over the template wherever they conflict.
4. You write `docs/SPEC.md` (what exists marked done, what remains as R-ids) and the next two sprints in `TODO.md`. A `scribe` agent fills `docs/TOOLCHAIN.md` and registers the project (`shreyas-workspace-replicate:log-tool`).
5. Show the ≤15-line summary and ask for the green flag. Then continue with Phase 5–6 of `${CLAUDE_PLUGIN_ROOT}/references/flow.md`.

Do not commit or push in an adopted repo until the owner says so.

**Knowledge base:** if `~/.claude/workspace-registry.txt` exists, first look up the owner's hardware, installed tools, preferences and past lessons in `<that path>/knowledge/` (start at `INDEX.md`) with one haiku agent, ask only what is missing, never reinstall what the registry shows as installed, and write new facts back with `shreyas-workspace-replicate:kb`.
