# Free models — the workers

The full rules (routing, the tested command, the exact brief, the failure ladder) are in the project's `docs/WORKFLOW.md` → "Routing — opencode first". This file is the short version for use before a project exists.

## Default

**`opencode/beam-free` for everything** — code, docs, searches and images (it has vision). It is the owner's best overall free model. Stay on it until it fails the same brief twice or is rate-limited; only then run `opencode models` and try another (`opencode/big-pickle` is good for code but text-only).

## Command (tested shape)

```bash
mkdir -p .oc
timeout 600 opencode run -m opencode/beam-free --auto "Do the task described in the file .oc/<task>.md. Follow it exactly." </dev/null > .oc/<task>.log 2>&1; tail -c 600 .oc/<task>.log
```

- Message first; `</dev/null` required; output to a log file. `-f <file>` before the message hangs — attach an image with `-f <image>` after the message.
- Write the brief with the file-writing tool, in the exact-brief format from `docs/WORKFLOW.md`.
- Set the Bash tool timeout to 600000 ms for larger briefs, or run in the background.

## Images

Before trusting a model other than beam with an image, probe it once:

```bash
opencode run -m <model> "Describe this image in one line. If you received no image, reply exactly: NO IMAGE" -f <a small image whose content you know> </dev/null
```

A correct, specific description = it can see. Otherwise look at the image yourself.

## When the free tier is depleted

Signs: HTTP 429, "limit", "quota", "Model is unavailable".

1. Two or three other `opencode/*` models.
2. Only if all are depleted: the omniroute gateway — `omniroute serve --daemon --no-open --no-tray` if nothing answers on port 20128, then `-m omniroute/auto/best-coding` (`omniroute/auto/best-vision` for images). Its zero-sign-up pool partly shares opencode's quota.
3. Only then a Claude subagent (record the reason in `.oc/ALLOW_CLAUDE_AGENT`), or do it yourself.

## Never

Secrets, credentials, or employer/client code to any free model or free gateway.
