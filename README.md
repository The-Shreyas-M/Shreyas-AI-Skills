# Shreyas-AI-Skills

Skill setup + personal skill library for my CLI coding workflow (`opencode`).

- **📦 Install all the skills I use** → see [`SKILLS-SETUP.md`](SKILLS-SETUP.md) (one command per skill, agent-agnostic).
- **✨ Create your own skill** → see [`CREATING-SKILLS.md`](CREATING-SKILLS.md) (scaffold, host in this repo, install anywhere).

## Quick start

Install any skill one by one:

```bash
npx skills add https://github.com/The-Shreyas-M/Shreyas-AI-Skills --skill <skill-name>
```

Or install the skills I use daily (see `SKILLS-SETUP.md` for the full list and what each does):

```bash
npx skills add https://github.com/anthropics/skills --skill frontend-design
npx skills add https://github.com/browser-use/browser-use --skill browser-use
npx skills add https://github.com/microsoft/playwright-cli --skill playwright-cli
npx skills add https://github.com/The-Shreyas-M/Shreyas-AI-Skills --skill gitcp
```

My own skills in this repo:

| Skill | What |
|---|---|
| `gitcp` | commit and push with the right GitHub account (personal vs college) |
| `scrollytelling-portfolio-builder` | plan and build a scrollytelling life-portfolio site end to end: bible, Gemini prompt system, cut-out pipeline, data-driven stage, deploy, SEO, phone layouts with a screen-size test harness, docs and logbook (`npx skills add https://github.com/The-Shreyas-M/Shreyas-AI-Skills --skill scrollytelling-portfolio-builder`) |
| `one-file-launch-guide` | build one offline HTML launch guide (numbered steps, tick boxes, copy and download buttons, link sync) for Gumroad + YouTube + Shorts + posts, plus the single buyer file design (`npx skills add https://github.com/The-Shreyas-M/Shreyas-AI-Skills --skill one-file-launch-guide`) |
Requires Node.js ≥ 18. Verify with `npx skills list`.

## Plugins (namespaced commands)

`new-project`, `iot-engineer` and `ai-video` are Claude Code plugins in this repo. Install (once per machine):

```bash
claude plugin marketplace add The-Shreyas-M/Shreyas-AI-Skills
claude plugin install new-project@shreyas-skills --scope user
claude plugin install iot-engineer@shreyas-skills --scope user
claude plugin install ai-video@shreyas-skills --scope user
python ~/.claude/plugins/cache/shreyas-skills/ai-video/*/engines/install_engines.py   # engines into ~/.claude/tools/video
```

| Plugin | Commands |
|---|---|
| new-project | `/new-project:start` (asks type), `:iot-hardware`, `:web-app`, `:local-app`, `:adopt` (bring an existing repo under the workflow), `:continue` (resume or run the next sprint) |
| iot-engineer | `/iot-engineer:start`, `:prototype-designer`, `:breadboard-circuit-designer`, `:pcb-designer`, `:schematic-review`, `:firmware-esp-idf`, `:firmware-arduino`, `:board-bringup`, `:debug` |
| ai-video | `/ai-video:start` (asks what you have and want, routes), `:shorts` (Shorts from your own talking-head video), `:clip` (best moments of a long video or URL; engine is third-party Devini clip-video, MIT), `:faceless` (no-footage reels and launch videos), `:post` (AI Video Editor workspace: review, approve, schedule, post). Heavy engines live in `~/.claude/tools/video/`, installed by `engines/install_engines.py`. |

The workspace-replicate plugin and its registry live in a separate private repo.

Projects scaffolded by new-project carry their own `/sprint` skill and `docs/WORKFLOW.md`, so the build loop also works in cloud sessions.

## Repo layout

```
├── README.md          # you are here
├── SKILLS-SETUP.md    # one-shot install of the skills I use + what each does
├── CREATING-SKILLS.md # how to scaffold, host & install your own skills
└── skills/            # my own skills live here (see CREATING-SKILLS.md)
```

## Adding a skill to this repo

1. Read [`CREATING-SKILLS.md`](CREATING-SKILLS.md).
2. Create `skills/<name>/SKILL.md`.
3. Push — anyone can install it with a single `npx skills add ...--skill <name>` command.