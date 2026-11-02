# The TODO and decision system

One file, `TODO.md`, is the project's memory. Anyone (or any session) can open it and know what is decided, done, undone, and next.

## Structure

```
# TODO: everything left for "<site>" (base version 0.0.1)
Written <date>. Every item has an ID so you can say "drop B3, scrap C2, do A1 first".
Tags: [you] needs your decision/asset, [me] I just do it, [both] I build, you approve.

## WHAT IS LEFT (<date>): start here      <- always first, rewritten after every big step
  Live now: <url>. Notes on deploy: DEPLOY.md.
  Waiting on you:   - [ ] ...
  For me to do next:- [ ] ...
  Done <dates>:     one paragraph

## A. Decisions (all answered <date>)       - [x] A1 <question>: <answer>
## B. Content and copy                      - [x] B2 [me] stock-word and em-dash gate ...
## C. Scenes and chapters (polish)          - [x] C2 (decision: ...; tried and UNDONE: ...)
## D. Interaction and UX
## E. Accessibility
## F. Performance and mobile
## G. SEO, sharing and polish
## H. Deploy
## I. Housekeeping
## J. Ideas parked or already rejected      (so nobody re-adds them)
## Next version (parked)
## P. Phone (its own branch) - from the real-device test
```

## Rules

- Tick with a short note: the decision and, when something was tried and removed, **"tried and UNDONE by the owner: ..."**.
- Never delete a rejected idea: move it to J with the reason.
- When a batch of questions is open, number them and get answers in one message; record "all answered <date>".
- Gates worth having as items: a **copy gate** (search all on-site text for stock words such as leverage, seamless, unlock, elevate, and for em dashes), a **privacy gate** (no ages, dates, grades, e-mail, politics in code, copy, alt text, page source, file names that ship), a **proof-lines check** (certificates read right).
- Keep ID tags honest: `[you]` items are the only ones that block; list them first under "Waiting on you".
- When the work is final: rewrite "WHAT IS LEFT" to the short list of things only the owner can do (indexing, profile links, real-device checks) and mark the rest done with dates.

## Companion docs

`ideas/README.md` (index of the bible), `PROJECT_STATUS.md` (how it works), `DEPLOY.md`, `GEMINI_PROMPTS.md`, `LOGBOOK.md`, `PROCESS.md`.
