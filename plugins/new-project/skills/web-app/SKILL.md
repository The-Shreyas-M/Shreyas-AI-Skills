---
name: web-app
description: Start a new web app or website (/new-project:web-app). Skips the type question and runs the web interview (users, auth, screens, data, stack, hosting, design references), then spec, scaffold, and a build loop that can run in a cloud session and deploy to Cloudflare.
argument-hint: "[project name]"
---

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
