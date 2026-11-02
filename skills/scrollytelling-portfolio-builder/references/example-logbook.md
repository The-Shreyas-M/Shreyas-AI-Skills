# Logbook: "I Am Shreyas"

Built over **14 calendar days, 20 Oct to 2 Nov 2026** (first commit Tue 20 Oct 20:36, last commit Mon 2 Nov 23:22, local time). **157 commits** in the final history, on 13 of the 14 days (22 Oct had none). Commit times show late-night sessions on most days, and long all-day sessions on 25 Oct, 31 Oct and 2 Nov. Commit counts per day in brackets. Source: the git history and the project notes (`TODO.md`, `PROJECT_STATUS.md`).

At a glance

| Phase | Dates | What |
|---|---|---|
| 1. Idea and avatar | 20-23 Oct | Creative bible, wardrobe, the avatar (realistic attempt, then stylised cartoon, rigged, five outfits) |
| 2. Pivot and build | 24-26 Oct | Motion-graphics acts from Gemini art, one shared chapter stage, all 20 chapters, effects, cats, version 0.0.1 |
| 3. Decisions and polish | 27-29 Oct | Copy and content, decisions A1-A11, finale, accessibility and performance pass |
| 4. Ship | 30-31 Oct | Favicon, share image, 404, GitHub, Cloudflare, KV counter, SEO, loading screen |
| 5. Phones | 29 Oct - 2 Nov | Real-phone feedback loop, address-bar saga, test harness, shape-based layout, glide, merge and deploy |

## Day by day

**Tue 20 Oct (6 commits).** Started in the evening with a creative bible (`ideas/`) and a scrollable story skeleton. Wardrobe easter egg, testimonials, socials, two cats, a Blender bridge. Wardrobe reworked into 5 fixed looks. Avatar attempt 1: a MetaPerson export with a long Blender enhancement pass (brows, moustache, ringlet curls, neck). Late at night decided the realistic route would not work and switched research to a **stylised 3D cartoon**.

**Wed 21 Oct (6).** Avatar built the new way: Gemini concept image, Hunyuan3D-2.1 high-resolution shape, a Tripo model prepped for web (longer legs, 6 ft, forward facing). Project renamed "I Am Shreyas"; an 80s/CRT direction added (dropped completely later). Avatar rigged in Mixamo and exported as a skinned web GLB; animated avatar with the wardrobe working (real model, 5 looks, calm clips).

**Thu 22 Oct.** No commits (rest day).

**Fri 23 Oct (7).** Wardrobe polish: stop shirt colour bleeding onto face and hands, a Signature seam crack effect, readable Midnight look, per-look colour and accessories (glasses, watch, belt, shoes). Gemini-to-Tripo prompts for two new outfits; real Founder (blazer) and Explorer (hiking gear) bodies; outfit bodies keep their own heads.

**Sat 24 Oct (6).** Hand-off plan, then the **pivot**: the acts become motion graphics over Gemini 2D art. Foundation built in one go: custom cursor, eight cats, pinned stages, a motion kit, the cut-out pipeline. Act I built; Acts II-V cut-outs keyed; asset plan and design-reset notes.

**Sun 25 Oct (20), the big build day.** One Gemini prompts file (instructions, locks, what is done). 42 generated images plugged in at once; one shared chapter stage for all chapters; figures planted on their plates; the whole world mirrored for right-hand copy. Videos dropped; always-on scroll motion; effects (chalk, skid marks, ink, splinters, rings, equations); the avatar hops on click; testimonials one at a time with dots; a real like counter; confetti when all cats are found. Eight new backgrounds; sequences as stacked images (fixed a missing avatar). Then a long run of timing fixes: hike, dyno climb, cycling, tabla alignment, yoga on the terrace, gym platform, karate as one travelling bow-kata-strike-bow sequence with a board that breaks. One progress line per chapter; the chapter cut became a gradient hand-off.

**Mon 26 Oct (15).** Equal frame slots for every sequence; six act-card cats, climbing cat, sleeping cat; two cats on the Wild act card; karate and tabla timing; Words chapter graphic; cursor fixes; longer gradient slides. **Base version 0.0.1 tagged (17:01).** TODO.md written with IDs for everything left; housekeeping.

**Tue 27 Oct (13).** Content and copy pass (B), then trials of extra effects (C2, C5, C6): added, judged, **reverted the same morning** (decision kept in the TODO). Family PC beat, the beige box hops when clicked.

**Wed 28 Oct (9).** Decisions A1-A11 answered in a batch. Finale redone twice to the owner's idea (white dots return and gather, a white gradient slide into the Earth finale). Interaction checks (D) ticked, a hover effect tried and reverted. Stronger text pool behind copy and screen-reader descriptions (E).

**Thu 29 Oct (11).** Performance and robustness (F): freeze far chapters, WebGL error boundary, vendor chunks, robots.txt, unused media removed. First **phone passes 1-4** from screenshots: text clear of the Journey button, figures above the copy, karate board and strokes placed, equations behind him, a stray third shoe removed from the Teardown cut-out.

**Fri 30 Oct (5).** Desktop: frosted Journey buttons, the karate board springs in and out from its feet. Share image and tags, touch icon, custom 404, no-JS line; favicon from a Gemini avatar head.

**Sat 31 Oct (37), ship day and the longest.** Branches `desktop`/`phone`; avatar master `.blend` kept as one copy. History cleaned (250 MB of raw files removed with `git filter-repo`, bundle backup first); private GitHub repo; Cloudflare Pages; KV namespace for the like counter; DEPLOY.md. SEO (canonical, sitemap, JSON-LD), Search Console verification. Speed: caching headers, self-hosted fonts, early avatar fetch; a loading screen with a face and a real byte-accurate progress bar that waits for every picture and the model. First **real-phone test** (janky, no tap burst wanted, nothing selectable); phone fixes: still fade instead of a moving mask, lighter pixel ratio, an `?fps` meter. Then the **address-bar saga**: a scroll-speed cap, a locked bar, the progress line that was hiding below the screen (a later CSS rule overrode the phone rule), blurred buttons that never blurred on the live site (the minifier dropped `backdrop-filter`). Loading screen lines cycling on the compositor so they never freeze.

**Sun 1 Nov (2).** Touch scrolling locked against Chrome taking over, with a speed watchdog; keyboard wave and design tangle moved off his face. Built the **layout test harness**: headless Chrome at many screen sizes.

**Mon 2 Nov (20).** Every screen size failed at first. Fixes: layout chosen by shape not width, copy shrinks to fit, landscape layout, a per-frame fit that keeps figures and props on screen, a campfire group centred, rotation reloads into the right layout, zoom reset and blocked, the bike drifts gently, tablets on their side, everything measured in the visible height for short screens, a blank-chapter bug fixed (an observer read the wrong report), compact landscape loading screen. Desktop checked pixel by pixel against the live site; **`phone` merged into `main` and deployed** (first time, then again). Evening: iOS-style touch glide, the loader waits until the avatar has really drawn, always start at the top, the Words chapter reworked (bigger copy, his legs behind the words, never his face), final merge and deploy. Then the project was cleaned up and documented (this file, `PROCESS.md`, `MIXAMO.md`, a reusable skill).

## Numbers

- 14 calendar days; 157 commits (37 on 31 Oct and 20 each on 25 Oct and 2 Nov were the busiest days).
- 20 chapters in 6 acts; 8 cats; 5 outfits; about 90 images and one avatar model (4 MB) on the site, 8.3 MB loaded behind the loading screen.
- Phone-layout test: 21 screen sizes (phones, a fold, tablets, landscape, desktop).
- Biggest single lessons: measure instead of guess; test the test; keep desktop provably unchanged.
