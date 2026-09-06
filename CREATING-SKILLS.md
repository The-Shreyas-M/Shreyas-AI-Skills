# Creating a Skill

A skill is just a folder with a `SKILL.md` file. The [skills CLI](https://github.com/vercel-labs/skills) (`npx skills`) installs it anywhere. This guide walks you through scaffolding one, hosting it in this repo, and installing it on any machine.

## 1. What a skill looks like

```text
my-skill/
├── SKILL.md        # required — frontmatter + instructions
├── scripts/        # optional — helper scripts
└── references/     # optional — extra docs/data the skill can read
```

`SKILL.md` starts with YAML frontmatter (`name` + `description`), then the actual instructions:

```markdown
---
name: my-skill
description: What my skill does and when to use it
---

# My Skill

Instructions for the agent to follow when this skill is activated.

## When to Use

Describe the scenarios where this skill should be used.

## Steps

1. First do this
2. Then do that
```

Notes:

- `name` must be lowercase with hyphens (e.g. `frontend-design`).
- `description` is what tells the agent when to load the skill — make it specific.
- Everything below the frontmatter is the prompt the agent follows.

## 2. Scaffold a new skill

```bash
npx skills init my-skill
```

This creates a `SKILL.md` template in `my-skill/`. (You can also just create the folder + file by hand.)

## 3. Test it locally before pushing

```bash
npx skills add ./my-skill
```

This installs your local skill so the agent can use it immediately. Iterate on it, and when it works:

## 4. Add it to this repo

```bash
mkdir -p skills
git mv my-skill skills/my-skill   # or: move my-skill/ into skills/
git add skills/my-skill
git commit -m "Add my-skill skill"
git push
```

Skills go under `skills/<name>/` so this repo can host many skills at once.

## 5. Install it anywhere

From any machine (after the repo is public):

```bash
npx skills add https://github.com/The-Shreyas-M/Shreyas-AI-Skills --skill my-skill
```

The CLI pulls only the `my-skill` folder from this repo. Add `-g` to install globally (`~/.agents/skills`) and `-a opencode` to target a specific agent:

```bash
npx skills add https://github.com/The-Shreyas-M/Shreyas-AI-Skills --skill my-skill -g -a opencode
```

## 6. Update SKILLS-SETUP.md

If you want a skill listed as part of the standard setup, add its install command (in the same format) to [`SKILLS-SETUP.md`](SKILLS-SETUP.md) and commit both.

## Optional: register on skills.sh

The open ecosystem catalog at [skills.sh](https://skills.sh/) indexes public skills so `npx skills find` can discover them. Submit your skill there to share it beyond this repo.

## Useful commands

```bash
npx skills list                 # list installed skills
npx skills update               # update all installed skills
npx skills check                # check for updates
npx skills remove my-skill      # uninstall a skill
npx skills find [query]         # search the ecosystem
```