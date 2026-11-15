
# /new-project — interview, scaffold, then build in sprints

You are the **orchestrator**. The owner talks to you during the interview and at
checkpoints only. Everything you create must be usable by a smaller model in a
fresh session, so write short, literal, complete files.

Do the phases in order. Do not write project code before Phase 5.

## Phase 0 — Knowledge base first (every sub-skill, before any question)

If `~/.claude/workspace-registry.txt` exists, the owner has a private shared knowledge base at `<that path>/knowledge/` (start at `INDEX.md`) and a tool registry. Use it by default:

1. As soon as the type and pitch are known, look it up **yourself with Grep** (targeted terms in `knowledge/*.md` and the registry `tools.yaml`, a few lines of context — no agent spawn, no whole-file reads). Only if the sweep is large, hand one agent a numbered list of the interview questions for this type plus: "which of these does the knowledge base already answer? what tools for this stack are already installed (grep the registry, confirm with `--version`)? which parts/boards does the owner already have? any past lesson relevant to this kind of project?" It answers per question in one line with the source file, or `NOT IN KB`. Do not read the knowledge files into your own context.
2. In the interview, **do not ask what the knowledge base answered**. Show those answers once as a short "On record — correct me if wrong" list, and ask only the `NOT IN KB` questions.
3. Never install or set up something the registry shows as installed and that still answers `--version`.
4. Write back what you learn (`shreyas-workspace-replicate:kb` for facts, `:log-tool` for tools): new preferences, parts bought, decisions that outlive this project, lessons at each checkpoint.

No pointer file (cloud session, another machine) → skip this phase and interview normally.

## Phase 1 — Open (one round)

`<root>` below = the plugin root path the sub-skill that sent you here printed.
If that sub-skill already fixed the type (`iot-hardware`, `web-app`, `local-app`), do not ask it again.

Ask in one AskUserQuestion call (skip anything already given):
1. Project name (free text).
2. Type: **IoT / hardware** · **Web app** · **Local app or tool** · **Something else** (video/content, library, research…).
3. One sentence: what it does and for whom.

A project can be mixed (firmware + dashboard). Then treat it as IoT for
location, and run both question sets.

## Phase 2 — Offer skills (ask, never auto-load)

Show the matching rows and ask which to load (multi-select, include "None, start clean"):

| Type | Offer |
|---|---|
| IoT / hardware | `iot-engineer:start` now; later, as the work reaches them: `iot-engineer:prototype-designer`, `:breadboard-circuit-designer`, `:pcb-designer`, `:firmware-esp-idf`, `:firmware-arduino`, `:debug` |
| Web app | `ui-ux-pro-max`, `frontend-design` |
| Video / content | `ai-video` |
| Any, when it's time to push | `gitcp` (always used for commit/push, no need to ask) |

Load only what the owner picks, and only when its phase starts (design skills at
the first UI sprint, not during the interview).

## Phase 3 — Interview

Read `<root>/references/interview-core.md` and the one file for the type:
`interview-iot.md`, `interview-web.md`, `interview-local.md` or `interview-other.md`
(mixed project → both). For IoT also ask the chip intake in the iot-engineer
plugin's `references/chips.md` if that plugin is installed. Rules:
- 3–4 questions per round, multiple choice with a recommended default wherever possible.
- Never ask what was already answered. Never ask what you can decide yourself and note as an assumption.
- Stop when every SPEC section can be filled. Usually 4–6 rounds.
- Push back on scope: for each feature ask "needed for v1?" — anything else goes to Later.

## Phase 4 — Scaffold (cheap)

1. Create the folder `~/Projects/<name>` (ask if a different place is wanted) and copy the template in one command — do not retype the files:
   ```bash
   S="<root>/template"; P="<project path>"
   mkdir -p "$P" && cp -r "$S/." "$P/" && mv "$P/dot-claude" "$P/.claude" && cd "$P" && git init -q
   ```
2. You write `docs/SPEC.md` yourself from the interview (this is the one file that needs your judgment). Give every requirement an id (`R1`, `R2`…) and a priority (Must / Should / Later).
3. You write Sprint 1–2 in `TODO.md` (3–7 tasks each, each task cites an R-id and has a check). Later sprints stay as one-line milestones — plan them when reached.
4. Delegate the rest with a brief that contains the facts — to a free model through `opencode run` on a personal project (exact brief and tested command in the template's `docs/WORKFLOW.md`), or to the `scribe` agent only if the project is confidential: fill the `{{placeholders}}` in `CLAUDE.md`, `HANDOFF.md`, `docs/DECISIONS.md`; add a type-appropriate `.gitignore`; for hardware projects create `docs/WIRING.md` (iot-engineer format); fill `docs/TOOLCHAIN.md` with every tool the stack needs. Then check its diff.
   Also have it register the project: if `~/.claude/workspace-registry.txt` exists, run the `shreyas-workspace-replicate:log-tool` skill for the new project and its tools.
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
If `/goal` is unavailable in that session, the owner types `/sprint` (a skill the scaffold puts in the repo, so it also works in cloud sessions).

One goal per sprint. At the checkpoint the owner tests, gives feedback, and pastes the line again.

## Hard rules

- **opencode first.** On every non-confidential project the default writer of code, tests, config and docs is a free model through `opencode run` with an exact brief. Every Claude subagent spawn (haiku or sonnet) costs 60k+ tokens of the owner's plan, so those are escalation only: after opencode fails its ladder, on confidential code, or in cloud sessions. Tiny jobs you do yourself.
- **Confidentiality is a required interview answer** (personal / client-employer). Write it into `CLAUDE.md` → Confidential; never leave the placeholder. Unanswered → ask before any delegation. Personal → opencode is on.

- No feature without an R-id in SPEC. No "while I'm here" extras. Working → good UI/UX → only then extras the owner asks for.
- Ask the owner only at: sprint checkpoints, something you cannot test (hardware, real accounts, visual taste), spending money, first production deploy, deleting data, or a spec gap that blocks every remaining task.
- Reuse before writing: framework built-ins and well-known libraries first.
- Never send secrets or employer/client code to free models (opencode free tier, omniroute free providers).
- Before spawning a free model, pick it for the task with `<root>/references/free-models.md` — never a random or habitual pick.
- Nothing gets installed untracked: every tool, SDK, global package, driver, CLI, MCP server or skill installed for the project goes into `docs/TOOLCHAIN.md` and the workspace registry in the same session (cheap subagent does the edit).
