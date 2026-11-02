# Phones, tablets, landscape: how to do it once

The phone phase took five days because it was done by eye on one device first. Do it in this order instead.

## 1. Rules to decide on day 1

1. **Layout by shape and height, not width.** Portrait layout (figure above the words) when `(max-aspect-ratio: 9/10)` or `(max-width: 760px) and (min-height: 561px)`. Wide layout otherwise, including a narrow phone on its side. One constant, written once in JS (`PORTRAIT`) and the same string in CSS. A width rule alone gave a 768 px iPad the desktop layout and a 740 px landscape phone the portrait one.
2. **The visible height is not `100vh`.** `100vh` ignores the browser's address bar; anything anchored to the bottom of a `100vh` box hangs under the screen. For short wide screens set `--vh = innerHeight/100 px` on the root and write every vh as `calc(var(--vh, 1vh) * N)` (fallback is the plain unit, so nothing else changes). In portrait, measure the real position of a fixed bottom element (the Journey button) and place things from it.
3. **Never tune with per-device numbers.** Measure and correct at runtime (below).
4. **Start at the top** on every load and reload (`history.scrollRestoration = 'manual'`); after a shape change (rotation) reload into the right layout, also at the top.
5. **Zoom**: lock the viewport at scale 1, block zoom gestures if the owner wants a fixed look, reset zoom on any screen change.

## 2. Measure-and-correct (instead of numbers)

- **Keep on screen**: every frame, for each group of figures and each popping prop, measure the rects of the visible images and slide the group just enough to sit inside the screen (margin about 2%). Groups wider than the screen: centre them if the star figure stays whole, else keep him whole and let a far prop crop. Marked groups can also be centred.
- **Copy fits the room**: shrink the text block with `transform: scale(s)` and widen it by 1/s so lines run longer, not taller; measure `scrollHeight`, not the box (a max-height hides overflow). Floors: about 0.82 for long copy (let his legs stand behind the words, never his face); landscape tries one column, then two.
- **Keep the head clear**: the face (top 40% of the figure, middle 56% of its width) must never be under the copy or a diagram; shrink the figure under a graphic that runs across the top (`max-height` from the graphic's measured bottom).
- **Tablets on their side**: slide the group clear of the copy; if it still cannot fit, lift it above the copy.
- A mover that cannot travel (no room) stays put; its effect lines carry the motion.

## 3. Touch scrolling when the address bar must stay put

- `touch-action: none` on the page while the smooth scroller is alive, so Chrome never scrolls natively (a native takeover, caused by a busy main thread making the touch non-cancelable, unlocked the bar and bypassed any cap).
- Lenis `syncTouch` for 1:1 finger scroll, cap the per-event delta, and a **watchdog** that caps speed (about 5 screens/s) whoever moves the page, with a test-only exemption (`?layoutcheck` on the dev server).
- **iOS-style glide**: on touch end compute the finger speed over the last ~100 ms, clamp it (about 3 screens/s), then each frame `v *= 0.998^dt_ms; y += v*dt`. A new touch stops it; a stopped finger gives no glide.

## 4. The test harness (build it first)

`scripts/layout-check.mjs` (Playwright core + a Chromium; adapt the selectors to your stage):

- 21 sizes: phones (SE, 12 mini, 14, 14 Pro Max, Pixel 5, S8, A55), a folded phone (280 px), Surface Duo, iPad Mini/Air/Pro, landscape phones **with and without** the address bar height, tablet landscape, laptop, desktop.
- For every chapter, sample 7 scroll positions; flag: figure cut by an edge (or within 1.2% of it), props/board off screen, copy under the Journey buttons, copy over the face, diagrams over the face, the progress line off screen, act cats under the buttons.
- `--shots` saves screenshots; build a contact sheet and LOOK at them: the numeric flags are heuristics (bounding boxes) and some are false alarms.
- Run three batches in parallel; takes ~10 minutes for everything.

`scripts/desktop-diff.mjs A B`: screenshots two servers (the live-code worktree and the branch) at desktop sizes and scroll points; compare with film grain averaged out (resize 8x with a box filter): only structural differences remain. `scripts/page-shots.mjs`: hero, act card, a long chapter and the ending on several sizes.

**Test the test.** The first full run was meaningless: a speed watchdog capped the harness's own scroll jumps, and the exemption failed because Python had written a backspace character into the regex. A test that never reaches the thing it checks reports "ok". Add a sanity check (print where the scroll really landed).

## 5. Rotation and observers

- Observers (IntersectionObserver) deliver batches: always use the last entry. Reading the first left a visible chapter marked "far" and not drawn: a random blank chapter on a real phone, found by a rotation fuzz test (rotate at ten scroll positions, assert a figure is drawn).
- Loader: do not let people in on a frame count; require a stable second with the avatar drawn, and restart the count if the 3D layer is rebuilt.

## 6. Checklist before merging phone work

- [ ] Full harness run: no new flags; screenshots of every flagged chapter viewed.
- [ ] Desktop diff clean (positions equal to half a pixel).
- [ ] Production build passes; deployed CSS read for dropped properties.
- [ ] Rotation test: load, scroll, rotate, expect reload and top.
- [ ] Real device pass by the owner, issues listed by chapter and device.
