# WORKFLOW — how this project is built

Read this fully at the start of every session. You are the **orchestrator**:
you plan, delegate, verify and keep the docs true. The owner is involved only
at checkpoints.

## Session start

1. Read `CLAUDE.md`, `HANDOFF.md`, `TODO.md`. Open `docs/SPEC.md` only for the sections a task needs.
2. Continue from **Next step** in `HANDOFF.md`. Do not re-plan what is already planned.

## The loop

Repeat until the current sprint's **Done when** list passes:

1. Take the top unticked task of the current sprint.
2. **Trace check:** it must cite a SPEC id (`R#`). No id → do not build it; add it to Parking lot.
3. **Route** it (table below). If delegating, write a brief.
4. **Verify yourself:** run the task's check (build, test, curl, screenshot). Run `git diff --stat` and confirm only the intended files changed. A subagent saying "done" is not evidence.
5. Tick the task in `TODO.md` with one line of evidence. Commit: `S<sprint>-T<task>: <what>`.
6. After every 3 tasks, and before you stop for any reason, have `scribe` update `HANDOFF.md`.

Sprint end: run every Done-when check → update `HANDOFF.md` → write a **CHECKPOINT** (below) → stop and wait for the owner.

## Routing — cheapest tier that can do the task

| Tier | Use for | How |
|---|---|---|
| 0 Free (local sessions only) | Boilerplate, mechanical edits across files, renames, simple tests, docs, well-specified single-file code | `opencode run -m <model> --auto -f brief.md "Do the task in brief.md"` from the project folder (Bash tool). **Choose `<model>` for the task** — see "Picking a free model" below. |
| 1 Haiku | Finding things in the code, running builds/tests and summarising the log, doc upkeep | `scout` or `scribe` agent |
| 2 Sonnet | Implementing a feature or fix from a clear brief | `builder` agent |
| 3 You (or an agent on your own model) | Architecture, interfaces between modules, debugging after a lower tier failed, reviewing diffs, anything ambiguous | do it directly |

Rules:
- Delegate when the brief is short (under ~150 words) and the work is more than a few tool calls. If explaining costs more than doing, do it yourself.
- One writer per set of files at a time. Independent tasks may run in parallel.
- **Escalate on failure:** a tier fails its check twice → move the task one tier up with the failure output. Tier 3 fails twice → write BLOCKED in `HANDOFF.md` with the evidence and take the next independent task.
- Free tier: never for secrets, never for employer or client code (see `CLAUDE.md` → Confidential). In cloud sessions tier 0 does not exist; start at tier 1.
- Do not read a subagent's transcript or have it paste files back. Ask for a report of at most 150 words: what changed, the check it ran, the result, anything odd.

### Picking a free model (tier 0)

Run `opencode models` and choose by what the task needs — never by habit:

| Task needs | Pick |
|---|---|
| To look at an image (screenshot, UI check, photo of a board or schematic) | a model whose name contains `vl` or `vision`. None available → use haiku (it can see images). A text-only model such as `big-pickle` cannot do this. |
| Writing or changing code | the strongest general coding model in the list (`opencode/big-pickle` at the time of writing) |
| Mechanical edits, docs, renames, formatting | a fast one (`flash`, `lightning`, `small` in the name) |
| A model you have not used before | give it one tiny task first and check the result before trusting it with real work |

Rate-limited or quota error (429, "limit", "quota") → retry once with another free model of the same kind, then fall back to the omniroute gateway if it is set up (`opencode run -m omniroute/<combo> ...`; start it first if nothing answers on its port), then to haiku. Do not burn turns retrying a depleted model.

### Free models need exact briefs — or do not use them

Free models do good work on exact instructions and poor work on vague ones. Use tier 0 **only** when you can write all of this; otherwise give the task to haiku or sonnet:

```
TASK: <one sentence>
EDIT ONLY: <exact file paths>            DO NOT TOUCH: anything else
STEPS:
1. <exact change: which function/section, what to add or replace>
2. ...
PATTERN TO COPY: <path + the 5–20 lines to imitate, pasted in>
EXACT NAMES: <identifiers, signatures, types, strings to use verbatim>
DONE WHEN: `<command>` prints `<expected output>`
DO NOT: add features, rename things, change formatting elsewhere, install packages, commit
REPLY WITH: files changed + the DONE WHEN output. Nothing else.
```

- One small outcome per run (one file or one repeated mechanical change). No design decisions, no "figure out", no debugging, no multi-file features.
- You must be able to check the result with a command or a 10-second diff read. Always run the DONE WHEN check and `git diff --stat` yourself.
- First failure → fix the brief once if it was unclear; second failure → move the task up a tier. Do not iterate on a free model.

### Toolchain log

Whenever a task installs or first uses a tool, SDK, global package, driver, CLI, MCP server or skill: `scribe` adds the row to `docs/TOOLCHAIN.md` (name, version, install command, why) in the same sprint, and — in local sessions where `~/.claude/workspace-registry.txt` exists — records it in the workspace registry with the `shreyas-workspace-replicate:log-tool` skill. Nothing is installed untracked. In cloud sessions only `docs/TOOLCHAIN.md` is updated; the backup skill collects it later.

### Brief format (every delegation)

```
Goal: <one sentence, the outcome>
Files: <exact paths to edit or create; "touch nothing else">
Context: <the 3-8 facts needed: interface, types, conventions, SPEC excerpt>
Check: <exact command or observation that proves it works>
Report: max 150 words — changed files, check result, anything odd. No code dumps.
```

## Sprints

- A sprint is 3–7 tasks that end in something the owner can see or test. A task fits one subagent run.
- Only the current and next sprint are detailed in `TODO.md`. Plan the next one at the checkpoint, from SPEC priorities and the owner's feedback.
- Order: Must requirements working end to end → UI/UX quality → Should → Later only if the owner asks.

## Checkpoints — the only times you stop for the owner

Stop and write a CHECKPOINT at the top of `HANDOFF.md` when:
- a sprint is done;
- something needs hands or eyes you do not have (flashing, wiring, a real account, visual taste);
- the next step spends money, deploys to production for the first time, or deletes data;
- a SPEC gap blocks every remaining task.

Anything else: decide, log one line in `docs/DECISIONS.md`, continue.

```
## CHECKPOINT <date> — Sprint <n>
Built: <3 bullets max>
Please test: <numbered steps the owner can follow, with expected result>
Need from you: <questions, each with your recommended answer>
Next sprint (proposed): <task titles>
```

## Change requests (the owner will change things often — that is normal)

1. Add one line to `docs/DECISIONS.md`: date, the change, why.
2. Edit `docs/SPEC.md` (new/changed/removed R-ids). SPEC is always the current truth.
3. Re-plan only the affected tasks in `TODO.md`. Finish the task in hand first unless the change makes it pointless.
4. If the change conflicts with a Must or doubles the sprint, say so in two lines and ask which gives way.

## Scope and quality guard

- No feature, option, abstraction or dependency that no R-id requires.
- Prefer built-ins and well-known libraries over new code. Smallest change that passes the check.
- Do not refactor working code unless a task says so.
- Every task leaves the project building and its checks passing.

## Keeping docs true (scribe does the writing)

| File | Holds | Updated |
|---|---|---|
| `TODO.md` | sprints, tasks, evidence | each task |
| `HANDOFF.md` | state, next step, blockers, checkpoint | every 3 tasks and before stopping |
| `docs/SPEC.md` | what is being built | on change requests |
| `docs/DECISIONS.md` | one-line decisions and changes, newest first | when made |
| `CLAUDE.md` | commands, conventions, rules | when a command or rule changes |

Keep `HANDOFF.md` under 60 lines: replace, do not append history (git has it).
