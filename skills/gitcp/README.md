# gitcp — commit & push with account switching

A skill for CLI coding agents that makes committing and pushing safe when you have **multiple GitHub accounts**. On each use it asks which account to use, switches `gh` auth + repo-local git identity to that account, verifies the remote is the chosen account's repo, then commits and pushes.

## What it does

1. Works out which account owns the repo: remembered `gitcp.account` setting, then the remote's owner; asks only if neither tells it.
2. Sets repo-local `user.name` / `user.email` (never global config) and remembers the account for next time.
3. Pushes using that account's token per command (`GH_TOKEN=$(gh auth token --user X)`), so the globally active `gh` account never changes.
4. Checks you have write access to the remote, refuses to push to the other account's repo, and can create a new repo under the right account (private by default).
5. Commits specific files after inspecting `git status`/`git diff`, then pushes.

Safeguards: no amend unless asked, no force-push, no blind `git add -A`, no committing secrets.

## Install

Requires Node.js ≥ 18 and the [skills CLI](https://github.com/vercel-labs/skills).

Install for all agents (default `~/.agents/skills`):

```bash
npx skills add https://github.com/The-Shreyas-M/Shreyas-AI-Skills --skill gitcp -g
```

Install for a specific agent:

```bash
npx skills add https://github.com/The-Shreyas-M/Shreyas-AI-Skills --skill gitcp -g -a opencode
```

Install only in the current project:

```bash
npx skills add https://github.com/The-Shreyas-M/Shreyas-AI-Skills --skill gitcp
```

Verify: `npx skills list`.

## Configure your accounts

Edit the accounts table at the top of `SKILL.md` with each account's `gh` login, name and `ID+login@users.noreply.github.com` email (find the ID with `gh api users/<login> --jq .id`). Restart your agent afterwards.

## Prerequisite: both accounts authenticated in GitHub CLI

The skill relies on `gh auth git-credential` being the git credential helper (it is the default when you authenticate via `gh auth login`). Authenticate each account once:

```bash
gh auth login --hostname github.com --git-protocol https  # first account
gh auth switch --user <other-login>                        # switch
gh auth login --hostname github.com --git-protocol https  # second account
```

Confirm both are set up with `gh auth status`. The skill picks between them per command.