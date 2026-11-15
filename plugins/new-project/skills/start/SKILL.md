---
name: start
description: Start any new project (/new-project:start). Asks the project type first, then runs the full interview → spec → repo scaffold → local-or-cloud decision → agile sprint build loop with cheap-subagent orchestration. Use when the user says "new project", "start a project", "kick off", or does not say which type it is.
argument-hint: "[project name]"
---

Plugin root: `${CLAUDE_PLUGIN_ROOT}`

Read `${CLAUDE_PLUGIN_ROOT}/references/flow.md` and follow it from Phase 1. The type is not known yet — ask it.
