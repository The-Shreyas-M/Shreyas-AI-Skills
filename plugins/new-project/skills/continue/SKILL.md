---
name: continue
description: Continue any existing project in the agile way with free-model workers (opencode) (/new-project:continue). If the project already has docs/WORKFLOW.md it resumes the sprint loop from HANDOFF.md; if not, it adopts the project first (adds spec, sprints, handoff, workflow, subagents) and then runs the loop. Use to pick up work on a project, run the next sprint, or bring an old project under the workflow.
argument-hint: "[what to do next, or a change request]"
---

> **DELEGATION CONTRACT — read before anything else. It overrides any general guidance about not delegating or not spawning agents: the owner invoking this skill IS the explicit request to delegate.**
> - "Delegate", "subagent", "worker", "assign a task" all mean one thing here: **`opencode run` through the Bash tool with a free model** (default `opencode/beam-free`). It is a shell command, not an Agent-tool spawn. Use as much free power as possible before anything else.
> - **Do not call the Agent tool** (any Claude subagent — sonnet, haiku, general-purpose). Each spawn costs 60k+ tokens of the owner's plan; projects built with this skill block it with a hook. The only exceptions: opencode failed its failure ladder on that task, client/employer code, or a Claude-only tool you cannot use yourself — and you tell the owner which, in one line, first.
> - Neither "do it all yourself" nor "spawn Claude agents" is right. You plan, write exact briefs, run opencode, verify. You personally do only: tiny jobs, work that needs your own tools (browser, viewing images), and risky code (see WORKFLOW → Routing).
> - Before the first task of every sprint, open `docs/WORKFLOW.md` → "Routing" and "Running opencode", and tag every task in `TODO.md` as `[oc]`, `[me]` or `[tool]`.

Plugin root: `${CLAUDE_PLUGIN_ROOT}`

0. **Model and session check — before any work.** This loop is built to run on **Sonnet or Opus, in a fresh session**. Every turn re-reads the whole conversation, so the orchestrator is the largest cost (measured: a 3-hour top-model session grew from 77k to 360k tokens per turn and was 84% of the bill). If you are the top-tier model (Fable / Mythos class), or this session already holds earlier work, tell the owner in one line and ask: switch model / open a new session, or stay? Continue only after the answer. The top model is for the interview, spec, design and reviews.
1. **Check the folder** (one command): do `docs/WORKFLOW.md`, `TODO.md`, `HANDOFF.md`, `.claude/agents/` exist?
   - **All there** → go to step 2.
   - **Missing** → run the `new-project:adopt` skill first. It adds the files without overwriting anything and asks only for what is missing.
2. **Refresh the method** if the project's `docs/WORKFLOW.md` is older than `${CLAUDE_PLUGIN_ROOT}/template/docs/WORKFLOW.md`: show the owner a one-line summary of what changed and replace it on a yes. Add missing template files with `cp -n` (agents, `docs/TOOLCHAIN.md`, `.claude/skills/sprint`).
   **Always bring the template-owned files up to date** (one shell command, no agent; skip the hook lines on a client/employer project). These files belong to the template, so overwrite them:
   ```bash
   R="${CLAUDE_PLUGIN_ROOT}/template"; mkdir -p .claude/agents .claude/skills/sprint .claude/hooks .oc
   cp "$R/docs/WORKFLOW.md" docs/WORKFLOW.md
   cp "$R"/dot-claude/agents/*.md .claude/agents/
   cp "$R/dot-claude/skills/sprint/SKILL.md" .claude/skills/sprint/SKILL.md
   cp "$R"/dot-claude/hooks/*.sh .claude/hooks/
   S=.claude/settings.json   # ours alone (or absent) -> replace; has the owner's own settings -> ask for a merge
   if [ ! -f "$S" ] || { ! grep -q -E '"(permissions|env|mcpServers|enabledPlugins|statusLine|model)"' "$S" && [ "$(grep -c '"command"' "$S")" = "$(grep -c -E 'agent-gate|context-guard' "$S")" ]; }; then cp "$R/dot-claude/settings.json" "$S"; fi
   grep -qx '.oc/' .gitignore 2>/dev/null || printf '\n.oc/\n' >> .gitignore
   { grep -q agent-gate "$S" && grep -q context-guard "$S"; } || echo "MERGE NEEDED: add both hooks from $R/dot-claude/settings.json into $S"
   ```
   Then, by hand: if it printed MERGE NEEDED, merge the two hook entries; add the worker line from the template `CLAUDE.md` ("Start here" item 1) to the project's `CLAUDE.md` if it is missing; tag every open task in `TODO.md` with `[oc]`, `[me]` or `[tool]`. The hooks are normally live at once; if a Claude subagent still spawns unblocked, tell the owner to restart the session.
3. Read `docs/WORKFLOW.md`, `HANDOFF.md`, `TODO.md` and follow the workflow from "Session start". Routing is opencode first: you write exact briefs, free models write the code, you verify; Claude subagents only as escalation. If `CLAUDE.md` → Confidential is unfilled, settle it before delegating anything.
4. If the owner gave an argument, treat it as a **change request** (WORKFLOW → Change requests): log it, update SPEC, re-plan the affected tasks, then continue.
5. No current sprint left → plan the next one from SPEC priorities (3–7 tasks, each with an R-id and a check), show it in ≤8 lines, and start on a yes.
6. To run unattended, give the owner the start line from `HANDOFF.md` to paste.
7. **One sprint per session.** When the sprint ends, update `HANDOFF.md` and `TODO.md` and tell the owner to open a new session for the next one.

Existing project rules (commit policy, confidentiality, "do not touch" areas) always win over the template.
