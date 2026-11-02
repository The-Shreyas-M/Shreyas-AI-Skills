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