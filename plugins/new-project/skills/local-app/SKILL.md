---
name: local-app
description: Start a new local app, script, automation or tool that runs on this machine (/new-project:local-app). Skips the type question and runs the local-tool interview (inputs, outputs, run pattern, credentials, packaging), then spec, scaffold and the local build loop.
argument-hint: "[project name]"
---

Plugin root: `${CLAUDE_PLUGIN_ROOT}`

Type is fixed: **Local app / tool**. Do not ask it.

Read `${CLAUDE_PLUGIN_ROOT}/references/flow.md` and follow it, with these presets:
- Phase 1: ask only the name and the one-sentence pitch.
- Phase 2: offer nothing by default; `ai-video` only if it is a video/content tool.
- Phase 3: `interview-core.md` + `interview-local.md` (video/content or anything unusual: `interview-other.md`). Get one real example input and the expected output.
- Defaults to propose: Python + venv + `requirements.txt` + `run.bat`/`run.sh`; credentials in a gitignored `.env`.
- Phase 5: **local**.
- Sprint 1 ends with the example input producing the expected output from one command.
