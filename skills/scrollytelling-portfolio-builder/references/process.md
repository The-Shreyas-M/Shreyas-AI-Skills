# How "I Am Shreyas" was built: the process, in short

A scrollytelling life-portfolio: one tall page, a 3D hero with a wardrobe, six "acts" with 20 pinned scenes, eight hidden cats, a finale. Built between **20 Oct and 2 Nov 2026** (14 days, 157 commits; day-by-day in `LOGBOOK.md`), live at https://iamshreyas.pages.dev. Stack: Vite + React + TypeScript, GSAP (ScrollTrigger, drawSVG, morphSVG), Lenis, three.js / react-three-fiber (hero only), Cloudflare Pages + one KV counter.

## 1. The way of working

- **Words before pixels.** The first commit was a creative bible (`ideas/`): who the site is about, the story as acts and scenes, visual direction, tech pipeline, open questions. Copy was curated into one public file; raw private notes stayed out of the shipped code. Every later decision (build, cut, revert) was written back into `TODO.md` with an ID (A1..., C2...), so "drop B3, do A1 first" was a complete instruction.
- **One owner, one assistant, many small loops.** Build, look at it on a real screen, say what is wrong in plain words, fix, repeat. Anything that was tried and disliked was **reverted by commit, not argued about** (several effects were added and removed the same morning); the TODO records what was undone so nobody re-adds it.
- **Rules written down once** and kept: nothing invented (no fake stats), nothing private (no ages, dates, grades, e-mail), no off-site links mid-scroll, no audio, never remove an effect the owner likes, the repo stays private.
- **Everything has an owner tag** in the TODO: `[you]` needs a decision or an asset, `[me]` just do it, `[both]` build then approve.

## 2. The pipeline, in order

1. **Concept and avatar.** First try: a realistic avatar (MetaPerson export, a long Blender "look" pass). It never looked like the person, so the direction changed on day 1 to a **stylised 3D cartoon**: a Gemini concept image, a high-resolution 3D shape from it (Hunyuan3D, then Tripo), 6 ft proportions, **rigged in Mixamo**, built into one web GLB with Blender scripts (`tools/blender/`), with five outfits as swappable bodies plus colour masks. Details: `MIXAMO.md`.
2. **Pivot to 2D art for the acts (day 5).** Full 3D scenes were too heavy and too hard to control. Instead each scene is a **Gemini image set**: a background plate, the avatar in a pose (cut-out), props, cats. `GEMINI_PROMPTS.md` holds the method that kept faces consistent: one chat per group, a **"lock" paragraph** pasted first with the reference image (people / objects / backgrounds), then one prompt per message, and a fix-up line when the face drifts. Rules for the pictures: flat green background to key out, empty plates with the left 40% calm for text, no text or logos.
3. **Cut-out pipeline** (`tools/*.py`): key the green, remove spill and the generator's watermark, trim, slice strips into poses, write WebP. Backgrounds are resized to 1920 px and never keyed.
4. **One stage for every chapter.** `src/scenes/stageArt.ts` is the single source of truth: chapter id, beats (plate, figures, props, effects, overlays). One component (`ChapterStage`) draws any chapter from that data, so adding a scene means adding data, not code. All motion is on a 0..1 timeline scrubbed by scroll, finished at 70% of the pin, then the finished picture is held.
5. **Effects and life.** Skid marks, ink strokes, splinters, chalk, equations, a terminal, a morphing wire, a progress line per chapter in the act's own "language", eight cats with their own words, a like counter, a Journey button that scrolls for you at 1x to 5.5x.
6. **Polish decisions** (answered in batches, then ticked): overlays kept, finale redone twice, no project links, contact by LinkedIn only, no audio, no easter eggs beyond the cats, a retro/80s theme dropped, accessibility extras cancelled, copy frozen.
7. **Deploy and be found.** Cleaned the git history of 250 MB of raw files (`git filter-repo`, with a bundle backup first), private GitHub repo, Cloudflare Pages (auto-deploy from `main`), a KV namespace for the shared like counter, share image/tags, sitemap, JSON-LD, Search Console. Notes: `DEPLOY.md`.
8. **Speed.** Self-hosted fonts, long cache headers, early model fetch, far-away chapters frozen with `content-visibility`, a loading screen that downloads every picture and the model with an exact byte progress bar and does not let you in until the avatar has really drawn.
9. **Phones, the long part (last 5 days).** See section 3.

## 3. The phone phase (29 Oct to 2 Nov): what went wrong and how it was solved

The desktop look was approved and **locked**. Phone work lived on its own branch and was only merged after a pixel-level proof that desktop had not moved.

| Challenge | What was happening | How it was tackled |
|---|---|---|
| Layout tuned by eye for one phone | Fixed numbers (offsets, scales) worked on one screen and broke on every other | Stopped hand-tuning. **Measure and correct at runtime**: each frame, figures and props are slid just enough to sit on screen; groups that are too wide are centred or lifted; the copy block shrinks to fit the room under him |
| Width decided the layout | A 768 px tablet got the desktop layout squeezed into a tall screen; a narrow phone on its side got the portrait layout | Layout chosen by **screen shape and height**, not width (`src/layout/portrait.ts`) |
| Address bar | Chrome's bar moved, the page jumped, a black block appeared behind blurred buttons; fixed bits hung below the visible area | Touch scrolling taken over (`touch-action: none` + Lenis), bar stays put; a speed watchdog; everything measured from the real visible height (`--vh`); the minifier had silently dropped `backdrop-filter`, found by reading the deployed CSS |
| Scroll too fast, assets blank | A flick outran the pictures | Hard cap on speed, plus an iOS-style glide after the finger lifts (deceleration 0.998 per ms) so it still feels natural |
| Random blank chapter | An observer batch was read oldest-first, leaving a chapter marked "far away" and not drawn | Always read the newest report (a 4-line fix found by a rotation fuzz test) |
| Avatar late after the loader | The loader let people in after four drawn frames | Ready = a dozen frames **and** still there a second later; the count restarts if the 3D layer is rebuilt |
| Zoom and rotation | Browser zoom persisted across device modes; rotating left a stale layout | Viewport locked at scale 1, zoom reset on every screen change, zoom gestures blocked, **reload into the right layout** on shape change, always start at the top |
| "Is it really fine?" | Fixing one screen broke another, silently | A **test harness** (`tools/layout-check.mjs`): opens the site in headless Chrome at 21 screen sizes, scrolls every chapter, flags anything cut off or covering the face, saves screenshots. Its first run was wrong (a safeguard blocked its own scroll jumps): **a test needs its own test** |
| Desktop must not change | Shared code, two behaviours | `tools/desktop-diff.mjs` screenshots the live site and the branch at the same scroll points and compares them with film grain averaged out; only then merged |

## 4. What worked

- Data-driven scenes (one stage component, one data file).
- Real-device feedback every few hours, in plain words, with screenshots.
- Cheap reverts and a TODO that remembers decisions.
- Measuring instead of guessing, and a harness that produces pictures, not just numbers.
- Branches as safety: `desktop` frozen, `phone` free to break, merge only after proof.

## 5. What to do differently next time

- Decide the layout rule (shape, not width) and the "visible height" rule on day 1.
- Build the screen-size test harness before the first phone pass, not after the fifth.
- Keep one source folder of raw assets outside the repo from the start (and decide early what can be regenerated).
- Document the Mixamo/Blender steps while doing them; here they were reconstructed from scripts.

## 6. Where things are

`TODO.md` (state and decisions) · `LOGBOOK.md` (dated log) · `DEPLOY.md` (hosting) · `GEMINI_PROMPTS.md` (every image prompt) · `MIXAMO.md` (rig and animations) · `ideas/` (the bible) · `tools/` (art scripts, layout tests) · `src/scenes/stageArt.ts` (all scenes).
