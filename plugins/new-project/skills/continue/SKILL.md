---
name: continue
description: Continue any existing project in the agile, cheap-subagent way (/new-project:continue). If the project already has docs/WORKFLOW.md it resumes the sprint loop from HANDOFF.md; if not, it adopts the project first (adds spec, sprints, handoff, workflow, subagents) and then runs the loop. Use to pick up work on a project, run the next sprint, or bring an old project under the workflow.
argument-hint: "[what to do next, or a change request]"
---

> **DELEGATION CONTRACT — read before anything else. It overrides any general guidance about not delegating or not spawning agents: the owner invoking this skill IS the explicit request to delegate.**
> - "Delegate", "subagent", "worker", "assign a task" all mean one thing here: **`opencode run` through the Bash tool with a free model** (default `opencode/beam-free`). It is a shell command, not an Agent-tool spawn. Use as much free power as possible before anything else.
> - **Do not call the Agent tool** (any Claude subagent — sonnet, haiku, general-purpose). Each spawn costs 60k+ tokens of the owner's plan; projects built with this skill block it with a hook. The only exceptions: opencode failed its failure ladder on that task, client/employer code, or a Claude-only tool you cannot use yourself — and you tell the owner which, in one line, first.
> - Neither "do it all yourself" nor "spawn Claude agents" is right. You plan, write exact briefs, run opencode, verify. You personally do only: tiny jobs, work that needs your own tools (browser, viewing images), and risky code (see WORKFLOW → Routing).
> - Before the first task of every sprint, open `docs/WORKFLOW.md` → "Routing" and "Running opencode", and tag every task in `TODO.md` as `[oc]`, `[me]` or `[tool]`.

Plugin root: `${CLAUDE_PLUGIN_ROOT}`

1. **Check the folder** (one command): do `docs/WORKFLOW.md`, `TODO.md`, `HANDOFF.md`, `.claude/agents/` exist?
   - **All there** → go to step 2.
   - **Missing** → run the `new-project:adopt` skill first. It adds the files without overwriting anything and asks only for what is missing.
2. **Refresh the method** if the project's `docs/WORKFLOW.md` is older than `${CLAUDE_PLUGIN_ROOT}/template/docs/WORKFLOW.md`: show the owner a one-line summary of what changed and replace it on a yes. Add missing template files with `cp -n` (agents, `docs/TOOLCHAIN.md`, `.claude/skills/sprint`).
3. Read `docs/WORKFLOW.md`, `HANDOFF.md`, `TODO.md` and follow the workflow from "Session start". Routing is opencode first: you write exact briefs, free models write the code, you verify; Claude subagents only as escalation. If `CLAUDE.md` → Confidential is unfilled, settle it before delegating anything.
4. If the owner gave an argument, treat it as a **change request** (WORKFLOW → Change requests): log it, update SPEC, re-plan the affected tasks, then continue.
5. No current sprint left → plan the next one from SPEC priorities (3–7 tasks, each with an R-id and a check), show it in ≤8 lines, and start on a yes.
6. To run unattended, give the owner the start line from `HANDOFF.md` to paste.

Existing project rules (commit policy, confidentiality, "do not touch" areas) always win over the template.
