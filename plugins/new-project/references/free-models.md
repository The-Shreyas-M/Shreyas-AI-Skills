# Free models — choose for the task, never by habit

Free tiers change weekly. **Always run `opencode models` first** and choose from what is listed now. The names below are what the list held on 2026-11-15.

## Rule

| The task needs | Choose | Why |
|---|---|---|
| To see an image (screenshot, UI check, board/schematic photo, chart) | a model with `vl` or `vision` in its name (then: `opencode/nemotron-3.5-super-vl-free`). None listed → haiku. | text-only models silently ignore or invent image content |
| Writing or changing code from a brief | the strongest general coding model (then: `opencode/big-pickle`) — **text only, not a vision model** | best quality of the free set |
| Mechanical edits, docs, tables, renames, formatting | a fast small one (`flash`, `lightning`, `small` in the name) | cheap on the shared free quota, quick |
| Long files or many files in one go | prefer a model advertised for long context; else split the task | free models truncate silently |
| A model not used before | one tiny probe task first; check the output | names say little about quality |

If unsure whether a model can see images: send it a small known image and ask what it shows. Wrong or vague answer → it is not a vision model.

## Invocation

```bash
cd <project> && opencode run -m <provider/model> --auto -f brief.md "Do the task in brief.md"
```

## When the free tier is depleted

Signs: HTTP 429, "Free usage limit reached", "quota", "Model is unavailable".

1. Try one other free model of the same kind from `opencode models`.
2. Try the omniroute gateway (cycles across its keyless pool by itself):
   ```bash
   omniroute serve --daemon --no-open --no-tray      # only if nothing answers on port 20128
   opencode run -m omniroute/auto/best-coding --auto -f brief.md "Do the task in brief.md"
   ```
   Built-in combos: `omniroute/auto/best-free`, `omniroute/auto/best-coding`, `omniroute/auto/coding:free`, and `omniroute/auto/best-vision` (the only one for images).
   Note: omniroute's zero-signup pool partly draws on the same free quota as opencode, so when one is exhausted the other often is too. Providers that need an account give real extra capacity — only the owner can add those.
3. Still failing → use haiku. Do not spend turns retrying a depleted model.

## Never

Secrets, credentials, or employer/client code to any free model or free gateway.

Free models only get the exact brief format in the project's `docs/WORKFLOW.md` ("Free models need exact briefs"). No exact brief → use haiku or sonnet.
