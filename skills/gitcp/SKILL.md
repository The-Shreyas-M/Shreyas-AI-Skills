---
name: gitcp
description: Commit and push with multi-account GitHub identity selection. Use when the user asks to commit and/or push and has multiple GitHub accounts — asks which account to use, switches gh auth + git identity to that account, verifies the remote, then commits and pushes to the correct repo.
---

# Commit & push with account switching

The user has multiple GitHub accounts and the git credential helper is GitHub CLI (`gh auth git-credential`), so which account is used is controlled by `gh auth switch`. Use this skill whenever committing or pushing on the user's behalf so the right identity is used for the right repo.

## Configure your accounts

Fill in the accounts table below with each GitHub account's `gh` login and its noreply email. Keep this table in every copy of the skill (repo + installed).

| Key  | gh account             | git user.email                                  |
|------|------------------------|-------------------------------------------------|
| `1`  | __ACCOUNT_1_LOGIN__    | __ACCOUNT_1_EMAIL__ (use the `+ID@users.noreply.github.com` form) |
| `2`  | __ACCOUNT_2_LOGIN__    | __ACCOUNT_2_EMAIL__ (use the `+ID@users.noreply.github.com` form) |

Repos live under each account on GitHub. The remote must point at the account chosen; never push to a repo owned by a different account under the wrong identity.

## Steps (in order)

1. **Ask which account to use** with the `question` tool. Options are the accounts from the table (e.g. account `1` and account `2`). Default to account `1` if there is exactly one obvious owner for the current repo.

2. **Switch the active gh account** so git-credential resolves tokens for the right user:
   - `gh auth switch --user <chosen gh login>`
   - Verify with `gh auth status` that the intended account shows `Active account: true`.

3. **Set the repo-local git identity** to match the chosen account (do NOT change global config):
   - `git config user.name <gh login>`
   - `git config user.email <email from table>`

4. **Verify the remote targets the chosen account's repo.** Show `git remote -v`. If `origin` points at a repo not owned by the chosen account, ask the user for the correct remote URL for the chosen account before pushing. If unsure, stop and ask — never guess the repo URL.

5. **Commit** (only if the user asked to commit):
   - Inspect `git status` and `git diff` first; stage only intended files.
   - Commit message: use the user-provided message, or write a concise one matching the repo's recent style.
   - Never commit secrets; never `git add -A` blindly.

6. **Push** (only if the user asked to push):
   - Push the current branch to the verified remote, e.g. `git push origin HEAD`.
   - Confirm success with `git status` / remote ref output.

Conventions: never amend unless asked, never force-push, never touch global git config. After pushing, report the account used, the branch, and the short commit hash to the user.