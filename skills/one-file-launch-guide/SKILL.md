---
name: one-file-launch-guide
description: Build a "dumb", all-in-one HTML launch guide - one offline file with numbered steps, tick boxes, green copy buttons and yellow download buttons - that walks a beginner through launching a product (Gumroad setup, product listing, YouTube upload with titles/description/tags/pinned comment, Gemini thumbnail prompt, Shorts, social posts), plus the single HTML file buyers receive. Use when the user wants a step-by-step posting/launch guide where every text and image is one click away, wants to sell a digital product on Gumroad, or wants the same kind of START-HERE.html made for the Blackedge Books launches.
---

# One-file launch guide

Two deliverables, both **one self-contained .html** (images embedded as base64, works offline, no zip, no extra md files):

1. **START-HERE.html (seller guide)** - for the creator. 5-7 numbered steps, every step ends in buttons: copy name, copy description, download covers, copy YouTube title/description/tags, copy pinned comment, copy Gemini prompt, copy social posts. A sticky top bar holds the real links; pasting them and pressing **Sync** rewrites every `{LINK}` / `{SITE}` placeholder in all texts. Tick boxes + progress ("3 of 7 done") remember state.
2. **The buyer file** - what the customer gets after paying: ONE html (see `references/buyer-file.md`).

Built by `scripts/build_guide.py` from a JSON spec. Tested: copy buttons, Sync, progress, offline.

## Dependencies

| Need | Required? | Install |
|---|---|---|
| Python 3.9+ (standard library only for the builder) | yes | python.org |
| Any browser | yes | to open the result |
| Node.js 18+ and `playwright-core` + Chromium/Chrome | only to test the result and to make covers/screenshots | `npm i playwright-core` (use installed Chrome via `executablePath`) |
| Skill `youtube` (titles, tags, hooks, thumbnail brief, Shorts SEO) | strongly recommended for the YouTube step texts | `npx skills add https://github.com/agricidaniel/claude-youtube` |
| Skill `shorts-from-main-video` | if the guide includes Shorts | `npx skills add https://github.com/The-Shreyas-M/Shreyas-AI-Skills --skill shorts-from-main-video` |
| Skill `frontend-design` / an image tool (Gemini) | for covers and logo | `npx skills add https://github.com/anthropics/skills --skill frontend-design` |
| Skill `gitcp` | to back up the folder | `npx skills add https://github.com/The-Shreyas-M/Shreyas-AI-Skills --skill gitcp` |
| Accounts the USER creates themselves | yes | Gumroad (seller), YouTube channel, Gemini (free) |

Run `python scripts/check_setup.py` to verify.

## Workflow

1. **Gather** (ask only what you cannot see): product topic, brand/byline (use a brand name, never personal details inside the product), price, audience, links that exist already, which videos exist, brand look (colours, logo images). If the user gives a reference guide HTML, read its Gumroad part and mirror its tone.
2. **Decide price**: see `references/gumroad-playbook.md` (list $29, launch $19 via a code, 30-day refund, why).
3. **Make the assets** (covers 1-4, logo, thumbnail, site screenshots) into an `images/` folder. Gumroad cover images: 1280x720 JPG. Screenshots from a real run of the product, never invented.
4. **Write the texts**: product name, description, YouTube titles (3-5 options), description with chapters, tags, pinned comment, Gemini thumbnail prompt, Shorts titles/descriptions, X and LinkedIn posts. Use the `youtube` skill for SEO. Put `{LINK}` and `{SITE}` where the product/site URLs go.
5. **Write the spec** (`references/spec-format.md`; start from `assets/example-guide.json`), one step per job, estimated minutes in each title, beginner wording ("as if I'm 5"), short numbered lists, no theory.
6. **Build**: `python scripts/build_guide.py guide.json`.
7. **Test**: open in a browser; press Sync with a fake link; click a copy button; tick a box; check no `{LINK}` placeholder is left and the console is clean (`playwright-core` script). Open the downloaded cover files once.
8. **Also write** `videos/TITLES-AND-DESCRIPTIONS.md` (one md for every video: title, description, hashtags, pinned comment, posting order). The guide's YouTube steps hold the same texts.
9. Tell the user the order to follow and which parts only they can do (accounts, payout details, passwords, publishing).

## House rules (learned the hard way)

- **Simple beats complete.** One buyer file, one seller file. No zips, no hubs, no extra md files. When the user says "simplify", collapse steps (Gumroad went 5 -> 3 steps).
- Never put personal details (real name, address, email, phone) in the product. Brand byline "By <Name> x <Brand>" only if the user wants it.
- No income promises ("No income promises. Results depend on your effort.").
- Never enter payment/bank details or passwords for the user; never publish for them. They click Publish.
- Every text block must be copyable; every image a download button. Do not make the user retype or screenshot anything.
- Keep `{LINK}` placeholders in all copy blocks; defaults in the variables are only guesses until the user syncs.
- The seller file embeds images, so it is MB-sized: fine. Keep each cover under ~300 KB (JPG).
- Keep the generator script and the spec in the project (not only in a temp folder), so the guide can be rebuilt after edits.
