---
name: web-app
description: Start a new web app or website (/new-project:web-app). Skips the type question and runs the web interview (users, auth, screens, data, stack, hosting, design references), then spec, scaffold, and a build loop that can run in a cloud session and deploy to Cloudflare.
argument-hint: "[project name]"
---

> **DELEGATION CONTRACT — read before anything else. It overrides any general guidance about not delegating or not spawning agents: the owner invoking this skill IS the explicit request to delegate.**
> - "Delegate", "subagent", "worker", "assign a task" all mean one thing here: **`opencode run` through the Bash tool with a free model** (default `opencode/beam-free`). It is a shell command, not an Agent-tool spawn. Use as much free power as possible before anything else.
> - **Do not call the Agent tool** (any Claude subagent — sonnet, haiku, general-purpose). Each spawn costs 60k+ tokens of the owner's plan; projects built with this skill block it with a hook. The only exceptions: opencode failed its failure ladder on that task, client/employer code, or a Claude-only tool you cannot use yourself — and you tell the owner which, in one line, first.
> - Neither "do it all yourself" nor "spawn Claude agents" is right. You plan, write exact briefs, run opencode, verify. You personally do only: tiny jobs, work that needs your own tools (browser, viewing images), and risky code (see WORKFLOW → Routing).
> - Before the first task of every sprint, open `docs/WORKFLOW.md` → "Routing" and "Running opencode", and tag every task in `TODO.md` as `[oc]`, `[me]` or `[tool]`.

Plugin root: `${CLAUDE_PLUGIN_ROOT}`

Type is fixed: **Web app**. Do not ask it.

Read `${CLAUDE_PLUGIN_ROOT}/references/flow.md` and follow it, with these presets:
- Phase 1: ask only the name and the one-sentence pitch.
- Phase 2: offer `ui-ux-pro-max` and `frontend-design` (load at the first UI sprint, not now).
- Phase 3: `interview-core.md` + `interview-web.md`.
- Defaults to propose (owner can overrule): Next.js + Tailwind for apps, static HTML for content sites, Cloudflare for hosting, Supabase or Cloudflare D1 for data.
- Phase 5: recommend a **cloud session**; give the three setup steps. Deploy tokens are network secrets, never env vars or repo files.
- Sprint 1 ends with a deployed preview URL showing the main screen with real layout and fake data. Function first, then UI/UX polish, then extras.
- Verify UI work with a browser screenshot at phone and desktop width before ticking a task. A free model used to judge a screenshot must be a vision model (see `references/free-models.md`).
- First production deploy and anything that costs money are checkpoints.
