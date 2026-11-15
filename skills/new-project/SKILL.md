---
name: new-project
description: Start any new project the right way (/new-project). Interviews the owner in depth, writes the spec, creates the repo scaffold (CLAUDE.md, SPEC, TODO, HANDOFF, WORKFLOW, cheap subagents), decides local vs cloud, then builds the project in small agile sprints as an orchestrator that delegates to free/cheap models. Use when the user types /new-project, says "start a new project", "kick off a project", or wants to set up a repo for agentic building.
argument-hint: "[project name]"
---

# /new-project — interview, scaffold, then build in sprints

You are the **orchestrator**. The owner talks to you during the interview and at
checkpoints only. Everything you create must be usable by a smaller model in a
fresh session, so write short, literal, complete files.

Do the phases in order. Do not write project code before Phase 5.

## Phase 1 — Open (one round)

Ask in one AskUserQuestion call (skip anything given in the arguments):
1. Project name (free text).
2. Type: **IoT / hardware** · **Web app** · **Local app or tool** · **Something else** (video/content, library, research…).
3. One sentence: what it does and for whom.

A project can be mixed (firmware + dashboard). Then treat it as IoT for
location, and run both question sets.

## Phase 2 — Offer skills (ask, never auto-load)

Show the matching rows and ask which to load (multi-select, include "None, start clean"):

| Type | Offer |
|---|---|
| IoT / hardware | `iot-engineer` |
| Web app | `ui-ux-pro-max`, `frontend-design` |
| Video / content | `ai-video` |
| Any, when it's time to push | `gitcp` (always used for commit/push, no need to ask) |

Load only what the owner picks, and only when its phase starts (design skills at
the first UI sprint, not during the interview).

## Phase 3 — Interview

Read `references/interview.md` and follow it. Rules:
- 3–4 questions per round, multiple choice with a recommended default wherever possible.
- Never ask what was already answered. Never ask what you can decide yourself and note as an assumption.
- Stop when every SPEC section can be filled. Usually 4–6 rounds.
- Push back on scope: for each feature ask "needed for v1?" — anything else goes to Later.

## Phase 4 — Scaffold (cheap)

1. Create the folder `~/Projects/<name>` (ask if a different place is wanted) and copy the template in one command — do not retype the files:
   ```bash
   S="$HOME/.claude/skills/new-project/template"; P="<project path>"
   mkdir -p "$P" && cp -r "$S/." "$P/" && mv "$P/dot-claude" "$P/.claude" && cd "$P" && git init -q
   ```
2. You write `docs/SPEC.md` yourself from the interview (this is the one file that needs your judgment). Give every requirement an id (`R1`, `R2`…) and a priority (Must / Should / Later).
3. You write Sprint 1–2 in `TODO.md` (3–7 tasks each, each task cites an R-id and has a check). Later sprints stay as one-line milestones — plan them when reached.
4. Delegate the rest to the `scribe` agent (haiku) with a brief that contains the facts: fill the `{{placeholders}}` in `CLAUDE.md`, `HANDOFF.md`, `docs/DECISIONS.md`; add a type-appropriate `.gitignore`; for hardware projects create `docs/WIRING.md` (iot-engineer format). Then check its diff.
5. Show the owner a ≤15-line summary: what v1 is, what is out of scope, sprint 1 tasks, stack, where it runs. Ask: **"Green flag to build?"** Apply corrections to SPEC first.

## Phase 5 — Where it runs

| Project | Run it | Why |
|---|---|---|
| Needs flashing, serial, USB, local devices | **Local** | cloud has no hardware |
| Web app (Cloudflare / Supabase) | **Cloud session** (ask; local is fine too) | builds, tests and deploys without the laptop |
| Local app / tool | **Local** | it must run on this machine |
| Firmware + web dashboard | **Local**; offer to split the dashboard into its own repo + cloud session |

Either way: make the first commit and push with the `gitcp` skill (it picks the right GitHub account) once the owner has given the green flag.

**If cloud:** tell the owner, in these words, kept short:
1. claude.ai/code → environment menu → **New environment**. Network: Limited, add the hosts the project deploys to (e.g. `api.cloudflare.com`, `*.supabase.co`).
2. Add deploy tokens as **network secrets** bound to those hosts (not env vars).
3. Start a session on the pushed repo and paste the start line from `HANDOFF.md`.

Cloud sessions do not have this machine's skills, opencode, or omniroute. That
is why the repo carries `docs/WORKFLOW.md` and `.claude/agents/` — they are the
whole method. In cloud the free tier is skipped and haiku is the cheapest tier.

## Phase 6 — Build loop

Follow `docs/WORKFLOW.md` in the project (it is the single source for the loop,
routing, checkpoints and change requests — do not restate it, read it).

To run unattended, give the owner this line to paste (a model cannot type slash commands):

```
/goal Every task in the current sprint of TODO.md is ticked with evidence and the sprint's Done-when checks pass in shown output, or a CHECKPOINT or BLOCKED entry for the owner is at the top of HANDOFF.md. Stop after 60 turns.
```

`/goal` = keep working until a condition is true → use it for building.
`/loop` = repeat on a timer → use it only for polling (CI, a long deploy, a soak test).
If `/goal` is unavailable in that session, the owner types: `Follow docs/WORKFLOW.md and run the loop until the next checkpoint.`

One goal per sprint. At the checkpoint the owner tests, gives feedback, and pastes the line again.

## Hard rules

- No feature without an R-id in SPEC. No "while I'm here" extras. Working → good UI/UX → only then extras the owner asks for.
- Ask the owner only at: sprint checkpoints, something you cannot test (hardware, real accounts, visual taste), spending money, first production deploy, deleting data, or a spec gap that blocks every remaining task.
- Reuse before writing: framework built-ins and well-known libraries first.
- Never send secrets or employer/client code to free models (opencode free tier, omniroute free providers).
