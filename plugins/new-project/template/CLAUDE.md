# {{PROJECT_NAME}}

{{ONE_SENTENCE_PITCH}}

**Type:** {{TYPE}} · **Stage:** {{prototype | demo | production}} · **Runs:** {{local | cloud session}}

## Start here (every session)

1. Read `docs/WORKFLOW.md` — the build method. Follow it exactly. **Workers are free models through `opencode run` (default `opencode/beam-free`); that is what "delegate" and "subagent" mean in this project. The Agent tool (Claude subagents) is blocked by a hook except for the three exceptions in WORKFLOW → Routing. Run sprints on Sonnet or Opus, one sprint per session.**
2. Read `HANDOFF.md`, then `TODO.md`. Continue from **Next step**.
3. `docs/SPEC.md` is the source of truth for what to build. Nothing outside it gets built.

## Stack

{{language, framework, hosting, database, key libraries — one line each}}

## Commands

| Do | Command |
|---|---|
| Install | `{{...}}` |
| Run / dev | `{{...}}` |
| Build | `{{...}}` |
| Test | `{{...}}` |
| Deploy / flash | `{{...}}` |

## Conventions

- {{folder layout in 3–5 bullets}}
- Commits: `S<sprint>-T<task>: <what>`. {{commit/push policy from the interview}}
- Commit and push with the `gitcp` skill when it is available (account is pinned in `.gitcp.md`).

## Confidential

{{"Personal project — free models allowed for tier-0 tasks." OR "Client/company code — never send to free models (opencode free tier, omniroute)."}}
Secrets live in {{where}}, never in the repo.

## Shared knowledge base

If `~/.claude/workspace-registry.txt` exists, look things up in the owner's knowledge base (`<that path>/knowledge/INDEX.md`) yourself with Grep (never an agent) **before asking the owner for context and before installing or setting up anything**. Ask or install only what is not found there; write new durable facts back (`shreyas-workspace-replicate:kb`).

## Toolchain log (mandatory)

- When any tool, SDK, toolchain, global package, driver, CLI, MCP server or skill is installed or first used for this project, add a row to `docs/TOOLCHAIN.md` in the same session: name, version, install command, why. Make the edit yourself (one line).
- If `~/.claude/workspace-registry.txt` exists, also record it in the workspace registry with the `shreyas-workspace-replicate:log-tool` skill, so a new machine can be set up from it. Nothing gets installed untracked.
- When the stack changes (a tool is replaced), mark the old row "replaced by <new>" instead of deleting it.

## Skills to load when relevant

{{skills the owner picked, and at which phase — or "none"}}
