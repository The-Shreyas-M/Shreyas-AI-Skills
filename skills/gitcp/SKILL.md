---
name: gitcp
description: Commit and/or push with the correct GitHub account when the user has two accounts (personal + college). Use whenever the user asks to commit, push, "gitcp", publish a project to GitHub, or create a new GitHub repo. Detects the right account from the repo (remembered setting, remote owner), asks only when unsure, and pushes with that account's token without changing the globally active gh account.
---

# gitcp: commit & push to the right GitHub account

The user has two GitHub accounts on this machine. Each project must be pushed by the account that owns it. Git uses `gh auth git-credential` as its credential helper, which honours the `GH_TOKEN` env var, so we pick the account **per command** instead of flipping global state with `gh auth switch`.

## Accounts

| Key | Label    | gh login                 | user.name                | user.email                                         |
|-----|----------|--------------------------|--------------------------|----------------------------------------------------|
| `p` | personal | `The-Shreyas-M`          | `The-Shreyas-M`          | `179123411+The-Shreyas-M@users.noreply.github.com` |
| `c` | college  | `The-Shreyas-M-College`  | `The-Shreyas-M-College`  | `308621427+The-Shreyas-M-College@users.noreply.github.com` |

Token for an account: `gh auth token --user <login>`. If that fails, the account is not logged in: tell the user to run `gh auth login` and stop.

The global git identity is the college account, so **never rely on global `user.*`**; always set the repo-local identity.

## Step 1: Resolve the account (stop at the first rule that matches)

1. **Remembered:** `git config --local --get gitcp.account` returns a login in the table.
2. **Remote owner:** parse the owner from `git remote get-url origin` (`github.com/<owner>/<repo>`). If the owner equals an account's login, use that account.
3. **Otherwise ask** (use AskUserQuestion): options `personal (The-Shreyas-M)` and `college (The-Shreyas-M-College)`. Say what you saw (no remote, remote owned by someone else, etc.).

If rule 2 gives an account that differs from rule 1, the remembered value is stale: tell the user and ask which is right.

Whenever you resolve the account, state it in one line before acting: `Using college (The-Shreyas-M-College) because origin is github.com/The-Shreyas-M-College/foo`.

## Step 2: Configure the repo (local only)

```bash
git config --local user.name  "<user.name>"
git config --local user.email "<user.email>"
git config --local gitcp.account "<gh login>"
```

Never touch `--global` config and never run `gh auth switch`.

## Step 3: Verify access before doing anything

```bash
export GH_TOKEN="$(gh auth token --user <login>)"
gh api user --jq .login          # must print <login>
```

If a remote exists, confirm the account can write to it:

```bash
gh repo view <owner>/<repo> --json viewerPermission --jq .viewerPermission   # WRITE, MAINTAIN or ADMIN
```

- Remote owned by the **other** account: do not push. Ask whether to switch to that account or repoint the remote.
- Remote owned by neither (org or fork) and permission is not write-level: stop and report.
- No remote: go to **New repo** below.

(Windows PowerShell: `$env:GH_TOKEN = (gh auth token --user <login>)`, and `Remove-Item Env:GH_TOKEN` when done. In Bash, scope it per command, e.g. `GH_TOKEN=$(gh auth token --user X) git push`, rather than exporting for the whole session.)

## Step 4: Commit (only if asked, or if there are changes and the user said "commit")

1. `git status` and `git diff` (staged and unstaged). Recent style: `git log --oneline -5`.
2. Stage specific files. No blind `git add -A`. Skip `.env`, keys, tokens, credentials, large binaries; warn if they are present and ask.
3. Commit with the user's message, or a concise one matching the repo style. Follow any attribution rule from the session.
4. If a pre-commit hook fails, fix the cause and make a **new** commit. Never `--no-verify`, never amend unless asked.

## Step 5: Push (only if asked)

```bash
GH_TOKEN=$(gh auth token --user <login>) git push -u origin HEAD
```

Never force-push. If rejected as non-fast-forward, report it and ask (pull/rebase vs stop). Afterwards run `git status -sb` to confirm.

## New repo (no remote yet)

Ask for: repo name (default: folder name) and visibility (default **private**). Then:

```bash
GH_TOKEN=$(gh auth token --user <login>) gh repo create <login>/<name> --private --source=. --remote=origin
```

Commit first if there are no commits yet, then push with Step 5. Confirm before creating anything on GitHub; creating a public repo needs an explicit yes.

## Report

End with: account used (label + login), repo URL, branch, short commit hash, and anything skipped. If the account was newly remembered for this repo, say so.

## Quick reference

- Inspect: `gh auth status`, `git config --local --get gitcp.account`
- Change a repo's account: `git config --local gitcp.account <login>` then redo Step 2
- Rotate/refresh a token: `gh auth refresh --user <login>`
