---
name: continue
description: Continue any existing project in the agile, cheap-subagent way (/new-project:continue). If the project already has docs/WORKFLOW.md it resumes the sprint loop from HANDOFF.md; if not, it adopts the project first (adds spec, sprints, handoff, workflow, subagents) and then runs the loop. Use to pick up work on a project, run the next sprint, or bring an old project under the workflow.
argument-hint: "[what to do next, or a change request]"
---

Plugin root: `${CLAUDE_PLUGIN_ROOT}`

1. **Check the folder** (one command): do `docs/WORKFLOW.md`, `TODO.md`, `HANDOFF.md`, `.claude/agents/` exist?
   - **All there** → go to step 2.
   - **Missing** → run the `new-project:adopt` skill first. It adds the files without overwriting anything and asks only for what is missing.
2. **Refresh the method** if the project's `docs/WORKFLOW.md` is older than `${CLAUDE_PLUGIN_ROOT}/template/docs/WORKFLOW.md`: show the owner a one-line summary of what changed and replace it on a yes. Add missing template files with `cp -n` (agents, `docs/TOOLCHAIN.md`, `.claude/skills/sprint`).
3. Read `docs/WORKFLOW.md`, `HANDOFF.md`, `TODO.md` and follow the workflow from "Session start".
4. If the owner gave an argument, treat it as a **change request** (WORKFLOW → Change requests): log it, update SPEC, re-plan the affected tasks, then continue.
5. No current sprint left → plan the next one from SPEC priorities (3–7 tasks, each with an R-id and a check), show it in ≤8 lines, and start on a yes.
6. To run unattended, give the owner the start line from `HANDOFF.md` to paste.

Existing project rules (commit policy, confidentiality, "do not touch" areas) always win over the template.
