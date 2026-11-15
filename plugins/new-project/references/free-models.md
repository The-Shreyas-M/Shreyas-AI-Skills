# Free models — choose for the task, never by habit

Free tiers change weekly. **Always run `opencode models` first** and choose from what is listed now. The names below are what the list held on 2026-11-15.

## Rule

| The task needs | Choose | Why |
|---|---|---|
| To see an image (screenshot, UI check, board/schematic photo, chart) | **no fixed model — probe first** (see "Vision check"). Start with the model the owner has had good results with lately (`opencode/beam-free` at the time of writing), then others. None passes → haiku. | names do not reliably say which models can see; text-only models silently ignore or invent image content |
| Writing or changing code from a brief | the strongest general coding model (then: `opencode/big-pickle`) — **text only, not a vision model** | best quality of the free set |
| Mechanical edits, docs, tables, renames, formatting | a fast small one (`flash`, `lightning`, `small` in the name) | cheap on the shared free quota, quick |
| Long files or many files in one go | prefer a model advertised for long context; else split the task | free models truncate silently |
| A model not used before | one tiny probe task first; check the output | names say little about quality |

## Vision check (before any image task)

Do not assume from the name, and do not just ask "can you see images?" — models answer yes wrongly. Test it:

```bash
opencode run -m <model> -f <a small image whose content you know> "Describe this image in one line. If you received no image, reply exactly: NO IMAGE"
```

- Correct, specific description → it has vision; use it for this session's image tasks and note it in `HANDOFF.md` → Gotchas (`vision-capable free model: <name>, checked <date>`), so the next session does not re-probe.
- `NO IMAGE`, an error, or a vague/wrong description → not usable for images; try the next model.
- Re-probe when the note is more than a few days old or the model list changed.

## Invocation

```bash
cd <project> && opencode run -m <provider/model> --auto -f brief.md "Do the task in brief.md"
```

## When the free tier is depleted

Signs: HTTP 429, "Free usage limit reached", "quota", "Model is unavailable".

Default is always opencode's own no-sign-up models (`opencode/*`). Avoid routing through omniroute in normal work.

1. Try two or three other `opencode/*` free models of the same kind from `opencode models`.
2. Only when every suitable `opencode/*` model is depleted and the task really should stay free — the omniroute gateway (cycles across its keyless pool by itself):
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
