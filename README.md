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
| `shorts-from-main-video` | (v2: boundary check, face auto-framing, zoom, SFX, SRT, moment-picking guide) turn a talking-head main video into vertical Shorts (b-roll on top, face below, word-by-word captions, hook title, 1.1x speed, ducked free phonk music); includes a filming guide, transcript and render scripts, and a dependency checker (`npx skills add https://github.com/The-Shreyas-M/Shreyas-AI-Skills --skill shorts-from-main-video`) |
| `one-file-launch-guide` | build one offline HTML launch guide (numbered steps, tick boxes, copy and download buttons, link sync) for Gumroad + YouTube + Shorts + posts, plus the single buyer file design (`npx skills add https://github.com/The-Shreyas-M/Shreyas-AI-Skills --skill one-file-launch-guide`) |
| `clip-video` | third-party (Devini Community Edition 1.0, MIT, based on Plextrang/Claude-Video-Clipper): long video or YouTube URL to vertical shorts; AI picks the moments, face-tracked 9:16 reframing, word captions, zooms, SFX. Run `python install.py` inside the skill folder once (`npx skills add https://github.com/The-Shreyas-M/Shreyas-AI-Skills --skill clip-video`) |
| `ai-video-studio` | the "AI Video Editor" workspace for any chat: drop videos in a folder, a subagent edits them (using shorts-from-main-video / clip-video), you approve, then a safe ledger-based poster schedules them on YouTube (official API) / Instagram (optional) / manual packs; `scripts/setup_workspace.py` rebuilds the folder on a new PC (`npx skills add https://github.com/The-Shreyas-M/Shreyas-AI-Skills --skill ai-video-studio`) |

Requires Node.js ≥ 18. Verify with `npx skills list`.

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