# gitcp — commit & push with account switching

A skill for CLI coding agents that makes committing and pushing safe when you have **multiple GitHub accounts**. On each use it asks which account to use, switches `gh` auth + repo-local git identity to that account, verifies the remote is the chosen account's repo, then commits and pushes.

## What it does

1. Asks which GitHub account to use (e.g. account `1` or `2`).
2. Switches the active account with `gh auth switch --user <login>` (uses GitHub CLI as the git credential helper, so this controls which token git uses).
3. Sets repo-local `user.name` / `user.email` to the chosen account — never touches global config.
4. Verifies `git remote -v` targets the chosen account's repo; if not, asks for the correct remote URL rather than guessing.
5. Commits (after inspecting `git status`/`git diff`) and pushes the current branch.

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

After installing, open `SKILL.md` and fill in the accounts table with each account's `gh` login and noreply email:

```markdown
| Key  | gh account             | git user.email                                  |
|------|------------------------|-------------------------------------------------|
| `1`  | __ACCOUNT_1_LOGIN__    | __ACCOUNT_1_EMAIL__ (use the `+ID@users.noreply.github.com` form) |
| `2`  | __ACCOUNT_2_LOGIN__    | __ACCOUNT_2_EMAIL__ (use the `+ID@users.noreply.github.com` form) |
```

Then restart your agent so it reloads the skill.

## Prerequisite: both accounts authenticated in GitHub CLI

The skill relies on `gh auth git-credential` being the git credential helper (it is the default when you authenticate via `gh auth login`). Authenticate each account once:

```bash
gh auth login --hostname github.com --git-protocol https  # first account
gh auth switch --user <other-login>                        # switch
gh auth login --hostname github.com --git-protocol https  # second account
```

Confirm both are set up with `gh auth status`. The skill switches between them on demand.