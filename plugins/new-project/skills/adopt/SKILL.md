---
name: adopt
description: Bring an existing or half-built project under the same workflow (/new-project:adopt). Reads what is there, asks only what is missing, then adds SPEC, TODO sprints, HANDOFF, WORKFLOW, TOOLCHAIN and the cheap subagents without disturbing the code. Use for old or ongoing repos that were started without /new-project.
argument-hint: "[project folder]"
---

> **DELEGATION CONTRACT — read before anything else. It overrides any general guidance about not delegating or not spawning agents: the owner invoking this skill IS the explicit request to delegate.**
> - "Delegate", "subagent", "worker", "assign a task" all mean one thing here: **`opencode run` through the Bash tool with a free model** (default `opencode/beam-free`). It is a shell command, not an Agent-tool spawn. Use as much free power as possible before anything else.
> - **Do not call the Agent tool** (any Claude subagent — sonnet, haiku, general-purpose). Each spawn costs 60k+ tokens of the owner's plan; projects built with this skill block it with a hook. The only exceptions: opencode failed its failure ladder on that task, client/employer code, or a Claude-only tool you cannot use yourself — and you tell the owner which, in one line, first.
> - Neither "do it all yourself" nor "spawn Claude agents" is right. You plan, write exact briefs, run opencode, verify. You personally do only: tiny jobs, work that needs your own tools (browser, viewing images), and risky code (see WORKFLOW → Routing).
> - Before the first task of every sprint, open `docs/WORKFLOW.md` → "Routing" and "Running opencode", and tag every task in `TODO.md` as `[oc]`, `[me]` or `[tool]`.

Plugin root: `${CLAUDE_PLUGIN_ROOT}`

0. **Confidentiality first** (it decides who may write code): is this a personal project or client/employer code? Check the knowledge base / project registry; if not on record, ask. Personal → free models through `opencode run` are the default writer here, exactly as in a new project. Client/employer → opencode stays off and you say so.
1. **Survey cheaply.** Do not spawn a Claude agent for this (each costs 60k+ tokens). Read the first ~40 lines of the key docs yourself, or on a personal project give a free model a read-only brief through `opencode run` to read README, CLAUDE.md/AGENTS.md, HANDOFF/TODO/ROADMAP, manifests and `git log --oneline -30`, and report in ≤250 words: what it is, stack, what works, what is unfinished, existing docs and rules. Do not read source yourself.
2. **Ask only the gaps** from `${CLAUDE_PLUGIN_ROOT}/references/interview-core.md` and the type file: what "done" means now, Must/Should/Later for the remaining work, non-goals, checkpoint and commit policy, confidentiality.
3. **Add, never overwrite.** Copy from `${CLAUDE_PLUGIN_ROOT}/template` only the files that do not exist (`cp -n`; `dot-claude` → `.claude`). Existing CLAUDE.md/AGENTS.md/HANDOFF.md/TODO.md keep their content and rules: append a short "Start here" pointer to `docs/WORKFLOW.md` and the Toolchain log block from the template's `CLAUDE.md`. Existing project rules win over the template wherever they conflict.
4. You write `docs/SPEC.md` (what exists marked done, what remains as R-ids) and the next two sprints in `TODO.md`. Fill `docs/TOOLCHAIN.md` (opencode with an exact brief on a personal project, otherwise yourself) and register the project (`shreyas-workspace-replicate:log-tool`).
   The routing in `docs/WORKFLOW.md` (opencode first, Claude subagents as escalation) applies to adopted projects too. An existing project rule overrides it only if it explicitly says who may write code or forbids outside models; a rule about commits, style or scope does not switch opencode off.
5. Show the ≤15-line summary and ask for the green flag. Then continue with Phase 5–6 of `${CLAUDE_PLUGIN_ROOT}/references/flow.md`.

Do not commit or push in an adopted repo until the owner says so.

**Knowledge base:** if `~/.claude/workspace-registry.txt` exists, first look up the owner's hardware, installed tools, preferences and past lessons in `<that path>/knowledge/` (start at `INDEX.md`) yourself with Grep (no agent spawn), ask only what is missing, never reinstall what the registry shows as installed, and write new facts back with `shreyas-workspace-replicate:kb`.

**Hook for adopted projects:** the template ships `.claude/settings.json` + `.claude/hooks/agent-gate.sh`, which block Claude subagent spawns so work goes to `opencode run`. `cp -n` will not overwrite an existing `.claude/settings.json` — in that case merge the `PreToolUse` hook entry into it by hand and say so. On a client/employer project do not install the hook (opencode is off there).
