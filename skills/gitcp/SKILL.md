---
name: gitcp
description: Commit and/or push with the correct GitHub account when the user has two accounts (personal + college). Use whenever the user asks to commit, push, "gitcp", publish a project to GitHub, or create a new GitHub repo. Asks which account the first time in a project and records it in .gitcp.md, then reuses it; pushes with that account's token without changing the globally active gh account.
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

## Step 1: Resolve the account via `.gitcp.md` (project root)

Each project keeps its confirmed account in `.gitcp.md` at the repo root (`git rev-parse --show-toplevel`). Format:

```markdown
# gitcp
account: The-Shreyas-M
confirmed: 2026-10-08
mirrors: https://github.com/<other-owner>/<repo>   # optional; one URL per line, or comma-separated
```

`mirrors:` lists **extra repos that must always get the same push** (for example a company repo plus the owner's own copy). Both must be reachable by the same account. Absent = one repo only.

1. **File exists:** read `account:`. It must be a login from the table, else treat the file as invalid and go to 2.
   - Sanity check: if `origin`'s owner is the *other* account, the file may be wrong. Show the mismatch and ask which is right before doing anything. If the user picks differently, update the file.
2. **File missing (or invalid): always ask once**, even if the remote owner looks obvious. Use AskUserQuestion with options `personal (The-Shreyas-M)` and `college (The-Shreyas-M-College)`. Say what you saw (remote owner, no remote, etc.) and mark the matching account "(Recommended)" when the remote owner is one of them.
3. **Write `.gitcp.md`** with the chosen login and today's date, and tell the user it was created. Keep it out of commits: append `.gitcp.md` to `.git/info/exclude` if not already there (local only; never stage it unless the user asks).

Never skip the ask on first use in a project. Once the file exists, don't ask again.

**Mirrors.** On first use, if `git remote get-url --push --all origin` already lists more than one URL, write every URL other than the fetch URL into `mirrors:` and tell the user. When the user says a project must be "maintained in both places", add the second repo to `mirrors:` (ask for its URL if not given; offer to create it under the resolved account, private, if it does not exist).

Before acting, state it in one line: `Using college (The-Shreyas-M-College) from .gitcp.md`.

## Step 2: Configure the repo (local only)

```bash
git config --local user.name  "<user.name>"
git config --local user.email "<user.email>"
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
- Every URL in `mirrors:` gets the same write-level check. One that fails → stop before pushing anywhere and report which.

(Windows PowerShell: `$env:GH_TOKEN = (gh auth token --user <login>)`, and `Remove-Item Env:GH_TOKEN` when done. In Bash, scope it per command, e.g. `GH_TOKEN=$(gh auth token --user X) git push`, rather than exporting for the whole session.)

## Step 4: Commit (only if asked, or if there are changes and the user said "commit")

0. Identity check: `git config user.name` must equal the resolved account's user.name. A mismatch (commits made outside this skill fall back to the global identity, which can be the other account) → redo Step 2 before committing, and tell the user which earlier commits carry the wrong author.
1. `git status` and `git diff` (staged and unstaged). Recent style: `git log --oneline -5`.
2. Stage specific files. No blind `git add -A`. Skip `.env`, keys, tokens, credentials, large binaries; warn if they are present and ask.
3. Commit with the user's message, or a concise one matching the repo style. Follow any attribution rule from the session.
4. If a pre-commit hook fails, fix the cause and make a **new** commit. Never `--no-verify`, never amend unless asked.

## Step 5: Push (only if asked)

```bash
GH_TOKEN=$(gh auth token --user <login>) git push -u origin HEAD
```

**With `mirrors:`** — make `origin` push to every repo, once (idempotent), then the same single push updates all of them:

```bash
F=$(git remote get-url origin)
git remote get-url --push --all origin | grep -qxF "$F" || git remote set-url --add --push origin "$F"
for m in <each mirror URL>; do git remote get-url --push --all origin | grep -qxF "$m" || git remote set-url --add --push origin "$m"; done
GH_TOKEN=$(gh auth token --user <login>) git push -u origin HEAD
# verify every copy, not just the last line git printed:
L=$(git rev-parse HEAD); for u in $(git remote get-url --push --all origin); do r=$(GH_TOKEN=$(gh auth token --user <login>) git ls-remote "$u" HEAD | cut -c1-40); [ "$r" = "$L" ] && echo "ok $u" || echo "BEHIND $u"; done
```

Any `BEHIND` line → report it and push that URL on its own (`git push <url> HEAD`); a mirror that rejects as non-fast-forward has diverged — stop and ask, never force.

Never force-push. If rejected as non-fast-forward, report it and ask (pull/rebase vs stop). Afterwards run `git status -sb` to confirm.

## New repo (no remote yet)

Ask for: repo name (default: folder name) and visibility (default **private**). Then:

```bash
GH_TOKEN=$(gh auth token --user <login>) gh repo create <login>/<name> --private --source=. --remote=origin
```

Commit first if there are no commits yet, then push with Step 5. Confirm before creating anything on GitHub; creating a public repo needs an explicit yes.

## Report

End with: account used (label + login), every repo URL pushed (one line each, with its ok/BEHIND result), branch, short commit hash, and anything skipped. If `.gitcp.md` was newly created, say so.

## Quick reference

- Inspect: `gh auth status`, `cat .gitcp.md`
- Change a repo's account: edit `account:` in `.gitcp.md`, then redo Step 2
- Rotate/refresh a token: `gh auth refresh --user <login>`
