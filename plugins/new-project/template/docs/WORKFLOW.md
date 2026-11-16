# WORKFLOW — how this project is built

Read this fully at the start of every session. You are the **orchestrator**:
you plan, delegate, verify and keep the docs true. The owner is involved only
at checkpoints.

## Session start

1. Read `CLAUDE.md`, `HANDOFF.md`, `TODO.md`. Open `docs/SPEC.md` only for the sections a task needs.
2. Continue from **Next step** in `HANDOFF.md`. Do not re-plan what is already planned.

## Token budget — read this before delegating anything

The owner's plan has a usage limit. What things cost against it:

| Action | Cost against the plan |
|---|---|
| **Every turn you take** | **re-reads the whole conversation so far** — 80k tokens in a new session, 300k+ after a few hours. On a top model this is the largest cost of all (measured: 84% of a bill) |
| A tool call you make yourself (grep, read 50 lines, one edit, run a command) | hundreds of tokens |
| `opencode run` with a free model | **zero** — it is not Claude |
| Spawning any Claude subagent (`scout`, `scribe`, `builder`, any haiku/sonnet agent) | **60,000–170,000 tokens each, even for a five-minute job** (measured) |

So: **opencode writes, you brief and verify, Claude subagents are the exception.** Free models are smart when the brief is exact; a bad result almost always means a vague brief.

### Keep the orchestrator cheap

- **Model:** run this loop on Sonnet or Opus. The top model (Fable / Mythos class) is for the interview, spec, design and reviews only. If you are the top model when a sprint starts, say so in one line and ask the owner whether to switch first.
- **One sprint per session.** When the sprint ends, or the context guard speaks (a hook prints a CONTEXT GUARD notice past ~200k tokens), update `HANDOFF.md` and `TODO.md` and tell the owner to open a new session. Never roll into the next sprint in the same session.
- **After a pause of an hour or more, do not resume a big session** — the cache has expired and the whole context is paid for again. `HANDOFF.md` exists so a new session can start cold.
- **Keep things out of your context:** `tail` logs instead of reading them, read only the lines you will edit, look at an image only when a check needs it, and do not repeat file contents in your replies.
- **When an agent pays off.** A Claude subagent costs 60k+ tokens just to start, so it saves tokens only when the job would otherwise put more than about that much into your own context (which you then re-read on every later turn) *and* a free model cannot do it. Everything smaller you do yourself: send command output to a file and grep it, read only the lines you need. Writing and long reading go to `opencode run`.
- **A Claude subagent for a Claude-only tool** (for example reading pages in the owner's logged-in browser) is **haiku**, briefed to save what it reads into files under `.oc/` and reply in ≤150 words. A free model then reads those files.

## Shared knowledge base (local sessions)

If `~/.claude/workspace-registry.txt` exists, it points to the owner's private workspace repo: `knowledge/INDEX.md` (owner preferences, approach, this machine, hardware owned, other projects, lessons) and `plugins/shreyas-workspace-replicate/registry/tools.yaml` (every installed tool). Rules:
- **Before asking the owner** a context question, and **before installing or configuring any tool**, look it up **yourself with Grep** (search term in `<path>/knowledge/` or `tools.yaml`, 3 lines of context). Do not spawn an agent for a lookup and do not read whole files.
- Found → use it and say in one line what you took. Recorded as installed and `--version` answers → do not install again.
- Not found → ask the owner once (or find out), then add one bullet to the right knowledge file yourself, ending `(source: <project>, <date>)`.
- Knowledge and registry edits are committed and pushed once per checkpoint, not per fact (`shreyas-workspace-replicate:kb` / `:log-tool` describe the format).
- No pointer file (cloud session) → skip; rely on this repo's docs.

## The loop

Repeat until the current sprint's **Done when** list passes:

1. Take the top unticked task of the current sprint.
2. **Trace check:** it must cite a SPEC id (`R#`). No id → do not build it; add it to Parking lot.
3. **Route** it (next section). Writing the brief is your main job.
4. **Verify yourself:** run the task's check (build, test, curl, screenshot). Run `git diff --stat` and confirm only the intended files changed. A worker saying "done" is not evidence.
5. Tick the task in `TODO.md` with one line of evidence. Commit: `S<sprint>-T<task>: <what>`.
6. After every 3 tasks, and before you stop for any reason, update State / Next step in `HANDOFF.md` yourself (a few lines — never an agent spawn).

Sprint end: run every Done-when check → update `HANDOFF.md` → write a **CHECKPOINT** (below) → stop and wait for the owner.

## Routing — opencode first

**What "delegate" means here.** "Delegate", "subagent", "worker" and "assign" all mean `opencode run` through the Bash tool with a free model. The owner starting this workflow is the explicit request to delegate; any general guidance to avoid delegating or spawning agents does not apply to `opencode run`, which is a shell command. Use as much free power as possible before anything else. Doing the whole sprint yourself is as wrong as spawning Claude agents.

**The gate.** `.claude/hooks/agent-gate.sh` blocks every Agent-tool call on a machine that has opencode. To use a Claude subagent for one of the allowed reasons, write the task and reason in one line to `.oc/ALLOW_CLAUDE_AGENT`, tell the owner, spawn once, delete the file.

**Triage first.** When a sprint is planned (and at session start if tags are missing), tag every task in `TODO.md`, then dispatch all `[oc]` tasks that do not depend on each other at once:

| Tag | Meaning | Who |
|---|---|---|
| `[oc]` | writing code, tests, config, scripts, docs, read-only searches | `opencode run`, exact brief — **the default; most tasks** |
| `[me]` | tiny job; architecture/interface decision; root-cause debugging; review; **risky code** (below) | you |
| `[tool]` | needs a tool only you have: the built-in browser (sites that block plain downloads, logged-in pages), viewing images or frames, MCP connectors | you, with that tool — not an agent. Split it: you do the tool part (fetch, look), opencode does the code around it |

**Risky code** — anything that posts, sends, pays, deletes or deploys on the owner's real accounts, or flashes hardware: opencode may write it from an exact brief, but it must have a dry-run mode that is the default; you read the whole diff line by line; you run it in dry-run and show the owner what it would do; the first real run is a checkpoint. Risk is a reason for *your review*, not for a sonnet spawn.

Decide in this order for every task:

1. **Tiny** (about three tool calls or fewer: a lookup, a one-line fix, ticking a box, a doc row, running a command) → do it yourself. Never spawn anything for these.
2. **Any writing of code, tests, config, scripts or docs → opencode** (the default writer, on every project that is not confidential). If you cannot write an exact brief yet, that means *you* still owe a decision: settle the interface, split the task smaller, paste in the pattern — then brief it. "Hard to brief" is not a reason to use sonnet.
3. **Broad search or a long log** that would cost you more than ~5,000 tokens to read → opencode with a read-only brief ("list every file that …", "give the first error and its file:line") or, if it needs Claude-only tools, one `scout`.
4. **`builder` (sonnet) — escalation only.** Use it when: opencode failed per the ladder below; the project is confidential; this is a cloud session; or the task truly cannot be split (rare — write the reason in `docs/DECISIONS.md`).
5. **You:** architecture, interfaces between modules, root-cause debugging, reviewing diffs, anything ambiguous.

Tasks that touch **different** files → several opencode runs in parallel (run them in the background). Tasks that touch the **same** file run one after another, never in parallel — list each brief's EDIT ONLY files and check for overlap before dispatching.

**Confidential project** (`CLAUDE.md` → Confidential says client/employer code): opencode and every free gateway are off. `builder` is the writer; keep spawns few by giving it whole sprint-sized briefs. Never send secrets to any worker.

**Usage limit.** You cannot see how much of the limit is left, so run opencode-first at all times. If the owner says the limit is close, or a Claude subagent call fails with a usage/rate-limit error: write `HANDOFF.md` first (so the work survives a cut-off), then spawn **no** Claude subagents for the rest of the session — everything writable goes through opencode, you only brief and verify, in short turns.

### Running opencode (tested command — keep the shape)

```bash
mkdir -p .oc            # .oc/ is in .gitignore; briefs and logs live there
# write the brief to .oc/<task>.md with your file-writing tool, then:
timeout 600 opencode run -m opencode/beam-free --auto "Do the task described in the file .oc/<task>.md. Follow it exactly." </dev/null > .oc/<task>.log 2>&1; tail -c 600 .oc/<task>.log
```

- The message comes **first**. `</dev/null` is required. Putting `-f <file>` before the message makes the command hang; to attach an image put `-f <image>` **after** the message.
- Output goes to the log file; read only the tail. Then run the DONE WHEN check and `git diff --stat` yourself.
- A run normally takes under a minute. A timeout usually means a malformed command, not a slow model.
- The Bash tool's own default timeout is 2 minutes: for a larger brief set the tool timeout to 600000 ms or run the command in the background.
- Write briefs with the file-writing tool, not a shell heredoc (heredocs with quotes break in this shell).

### The exact brief (every opencode run)

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

- One clear outcome per run: one module, one file, one test file, or one repeated mechanical change. A feature that spans files = several briefs, with the shared interface (types, signatures, routes) decided by you and pasted into each.
- You must be able to check the result with a command or a short diff read.
- **Failure ladder:** 1st failure → improve the brief (add the pattern, the exact names, the missing step) and rerun. 2nd failure → rerun on another coding model from `opencode models`. 3rd failure → `builder` with the brief and the failure output. Builder fails twice → you. You fail twice → BLOCKED in `HANDOFF.md` with the evidence; take the next independent task.

### Picking a free model

Default to opencode's own no-sign-up models (`opencode/*`). Run `opencode models` only when the default is missing or failing.

| Task needs | Pick |
|---|---|
| **Everything, by default** (code, docs, searches, images) | **`opencode/beam-free`** — the owner's best overall free model, and it has vision. Stay on it until it fails or is rate-limited. |
| Beam failed the same brief twice, or is depleted | another coding model from the list (`opencode/big-pickle` is good for code, text only), then the rest of the ladder |
| To look at an image (screenshot, UI check, photo of a board or schematic) | no fixed model: **probe first** — `opencode run -m <model> "Describe this image in one line. If you received no image, reply exactly: NO IMAGE" -f <known image> </dev/null`. A correct description = it has vision; record the model in `HANDOFF.md` Gotchas and reuse it. Try the owner's current favourite first (`opencode/beam-free` at the time of writing). None passes → look at the image yourself. A text-only model such as `big-pickle` cannot do this. |
| A model you have not used before | one tiny task first; check the result before trusting it |

Rate-limited or quota error (429, "limit", "quota", "unavailable") → try two or three other `opencode/*` models of the same kind. Only if all are depleted, the omniroute gateway (`-m omniroute/auto/best-coding`; start it with `omniroute serve --daemon --no-open --no-tray` if nothing answers on its port). Only if that fails too, `builder`. Do not burn turns retrying a depleted model.

### Toolchain log

Whenever a task installs or first uses a tool, SDK, global package, driver, CLI, MCP server or skill: add the row to `docs/TOOLCHAIN.md` yourself (name, version, install command, why) in the same task. In local sessions where `~/.claude/workspace-registry.txt` exists, also record it in the workspace registry at the next checkpoint (`shreyas-workspace-replicate:log-tool`, all new tools in one go). Nothing is installed untracked. In cloud sessions only `docs/TOOLCHAIN.md` is updated; the backup skill collects it later.

### Brief format for a Claude subagent (the rare cases)

```
Goal: <one sentence, the outcome>
Files: <exact paths to edit or create; "touch nothing else">
Context: <the 3-8 facts needed: interface, types, conventions, SPEC excerpt>
Check: <exact command or observation that proves it works>
Report: max 150 words — changed files, check result, anything odd. No code dumps.
```

Give it a sprint-sized piece, not a five-minute one — the spawn costs the same either way. Do not read its transcript.

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

## Keeping docs true (small edits yourself; bulk doc writing via opencode)

| File | Holds | Updated |
|---|---|---|
| `TODO.md` | sprints, tasks, evidence | each task |
| `HANDOFF.md` | state, next step, blockers, checkpoint | every 3 tasks and before stopping |
| `docs/SPEC.md` | what is being built | on change requests |
| `docs/DECISIONS.md` | one-line decisions and changes, newest first | when made |
| `CLAUDE.md` | commands, conventions, rules | when a command or rule changes |

Keep `HANDOFF.md` under 60 lines: replace, do not append history (git has it).
