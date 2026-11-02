---
name: scrollytelling-portfolio-builder
description: Plan and build a scrollytelling life-portfolio website (one tall page, pinned scenes, an illustrated or 3D avatar, hidden cats/easter eggs, a Journey auto-scroll button) from scratch with an AI image pipeline (Gemini prompts with consistency "locks", green-screen cut-outs), a data-driven scene stage (React, GSAP ScrollTrigger, Lenis), Cloudflare Pages deploy, SEO, a loading screen, and phone/tablet/landscape layouts that are proven by a screen-size test harness. Use when the user wants a story-driven personal or portfolio site, a "website like I Am Shreyas", or asks for the process, TODO system, prompt files, logbook and test tools from that build.
---

# Scrollytelling portfolio builder

A repeatable way to build a cinematic, scroll-driven personal site in about two weeks of evenings. It comes from a real build (14 days, 157 commits, 20 chapters in 6 acts, 8 hidden cats, one avatar). Read `references/process.md` first for the story of that build; this file is the playbook.

## When to use

- The user wants a story-told-by-scrolling site about a person (portfolio, life story, studio, band).
- The user wants the whole workflow: bible, art prompts, cut-outs, scenes, deploy, phone support, docs.
- The user asks for the TODO / prompts / logbook / test conventions from that project.

Do not use it for a normal multi-page marketing site.

## Operating rules (set these with the owner on day 1, write them in the TODO)

1. **Words before pixels.** Write a creative bible first (who, story as acts and scenes, visual direction, privacy). Curate public copy into one file; raw private notes never ship (repo stays private).
2. **IDs for everything.** Keep one `TODO.md` with lettered sections and item IDs (A1, C2...) and tags `[you]` `[me]` `[both]`. Decisions are written back with the date and what was reverted. See `references/todo-and-decisions.md`.
3. **Revert, do not argue.** Try an effect, show it, keep or revert the commit, record the verdict. Never remove an effect the owner likes; never add one they did not ask for.
4. **Nothing invented.** No fake stats, no private facts (ages, dates, grades, e-mail), no off-site links mid-scroll, no audio unless asked.
5. **Real device, plain words.** After each batch, the owner looks on a real phone and describes what is off. Ask for screenshots. Fix, re-test, repeat.
6. **Lock the approved look.** Once desktop is approved, work for phones on a branch and merge only after the desktop-diff proof (phase 9).
7. **Confirm before outward or irreversible actions** (deploys to production, deleting raw assets, history rewrites). Make a backup first.

## Workflow

### Phase 0: interview (ask, do not assume)
Who is the site about? Acts and chapters (aim 4-8 acts, 15-25 chapters)? The look (palette, type, grain)? Avatar: stylised 3D cartoon (recommended) vs realistic (do not: it never looked like the person)? Which things must never appear? Hosting account? Whether a domain exists.

### Phase 1: bible and rules
Create `ideas/` (about, public copy, story and acts, visual direction, avatar, tech pipeline, open questions, testimonials/socials) and `TODO.md`. Commit "ideas bible + skeleton" as the first commit.

### Phase 2: avatar (if the site has one)
Gemini concept image of the person in the chosen style, then a 3D shape from it (Hunyuan3D / Tripo), prepare for rigging (A-pose, about 50k triangles), auto-rig and animate in Mixamo, build one web GLB in Blender scripts (idle loop plus named clips; swappable outfit bodies with recolour masks). Record every Mixamo animation name and setting in a `MIXAMO.md` while doing it (download "with skin"). The hero is the only place that needs three.js.

### Phase 3: the image prompt system
See `references/gemini-prompt-system.md`. One chat per group (people, props, backgrounds, cats), a LOCK paragraph pasted first with the reference image, one prompt per message, a FIX-UP line for drift, exact file names, flat green background for everything to be cut out, empty backgrounds with the left 40% calm for the headline. Keep every prompt in one `GEMINI_PROMPTS.md` with done/to-do status.

### Phase 4: asset pipeline
`scripts/key_cutouts.py` (key green, remove spill and watermark, trim, slice strips, write WebP), `scripts/prep_bgs.py` (resize backgrounds to 1920 wide). Output only to `public/media/<group>/`. Decide early which raw files can be regenerated and keep them outside the repo.

### Phase 5: the stage (architecture)
See `references/architecture.md`. One component draws every chapter from a data file (`stageArt.ts`: chapter id, beats, plate, figures, props, effects, overlays). Pinned sticky sections, all motion on a 0..1 scroll-scrubbed timeline that finishes at about 70% of the pin and then holds. Opacity, transform and stroke only. Lenis smooth scroll driven by the GSAP ticker.

### Phase 6: life
Effects per chapter (skid marks, ink, chalk, splinters, a terminal, morphing lines), one progress line per chapter drawn in the act's own language, cursor with words, cats with their own words and a confetti finish, a like counter (Cloudflare KV function), a Journey button (auto-scroll at several speeds).

### Phase 7: decision rounds
Batch the open questions in the TODO, get answers, tick them with dates, revert what was disliked. Freeze copy.

### Phase 8: ship
See `references/deploy-and-seo.md`: history cleanup with a bundle backup, private GitHub repo, Cloudflare Pages (auto-deploy from `main`), KV binding, share image and tags, sitemap, JSON-LD, 404, favicon, caching headers, self-hosted fonts, a loading screen with real byte progress that waits for the 3D avatar, far-chapter freezing.

### Phase 9: phones, tablets, landscape (the part that took longest)
See `references/phone-and-layout.md`. Decide the layout by **screen shape and height, not width**; measure the visible height (address bars); fit things by **measuring at runtime**, not with per-device numbers; take over touch scrolling if the address bar must stay put and add an iOS-style glide; reload into the right layout on rotation and start at the top. Build the test harness (`scripts/layout-check.mjs`, `desktop-diff.mjs`, `page-shots.mjs`) before the first phone pass, and test the tests.

### Phase 10: freeze and document
Update the TODO to "what is left", write `PROCESS.md` (how it was built, challenges, solutions), `LOGBOOK.md` (dated, from git history: `git log --reverse --format='%ad|%s' --date=format:'%Y-%m-%d %H:%M'`), `MIXAMO.md`, and clean the folders: keep the images and models the site uses (find them by crawling the running site and comparing with `public/`), delete everything that can be downloaded or regenerated.

## Pitfalls that already cost hours

- A minifier can silently drop `backdrop-filter` when the `-webkit-` version sits in the same rule: read the deployed CSS.
- A later CSS rule of equal specificity overrides a media-query rule: check computed values, not source.
- `100vh` is the height without the address bar: anything anchored to the bottom of a `100vh` box hangs below the screen.
- IntersectionObserver can deliver several entries at once: use the last, never `entries[0]`.
- Width breakpoints break tablets and landscape phones.
- A JavaScript safeguard can block your own test's scroll jumps: add a test-only exemption and verify it works (a stray control character from a Python escape once defeated it).
- Headless screenshots must have the film grain averaged out before comparing.
- Do not let the loading screen finish on a frame count alone: require a stable second.

## Files

- `references/process.md`: the build story and challenge table.
- `references/todo-and-decisions.md`, `gemini-prompt-system.md`, `architecture.md`, `phone-and-layout.md`, `deploy-and-seo.md`, `logbook-template.md`.
- `scripts/`: the test harness and asset scripts (adapt selectors to your project; see `scripts/README.md`).
