# Architecture: a data-driven scroll stage

Stack: Vite + React + TypeScript, GSAP 3 (ScrollTrigger plus the free drawSVG and morphSVG plugins), Lenis, three.js / react-three-fiber for the hero only, Cloudflare Pages Functions for one KV counter.

## The one idea

**One component draws every chapter from a data file.** Adding a scene = adding data.

```ts
// stageArt.ts (single source of truth)
stageArt['karate'] = {
  anim: 0.88,                       // share of the pin the animation uses
  extras: [{ item: {src: board}, x: 87, y: 91, vis: [0, 0.667] }],   // props with their own time window
  beats: [{
    bg: 'dojo',                     // plate image
    at: { x: 48, y: 91 },           // where his feet stand, % of the plate
    fx: ['ink', 'splinters'],       // world effects
    over: ['bols'],                 // overlay graphics (terminal, chart ...)
    items: [{ frames: [...], scales: [...], range: [0,1], h: 46, star: true,
              move: [[0,0,0],[1,180,0]] }],   // keyframes [progress, x%, y%, rotation]
    phone: { nx: 0, ps: 0.7, center: false }, // layout hints for the portrait layout
  }],
}
```

A chapter can have several beats that cross-fade (a new plate and pose). A weight `w` gives a beat a longer share.

## Scroll and motion rules

- Each chapter is a tall section (e.g. 400vh; hero 520vh; +130vh when poses change) with a `position: sticky` stage.
- **All animation is on a 0..1 timeline scrubbed by scroll, finishing at ~70% of the pin; the rest holds the finished picture.** Chapter hand-offs are a fixed-length gradient out (about 27% of the chapter) and a dissolve in.
- **Only opacity, transform and stroke animate.** No filters on moving things, no blend modes over big areas, one static grain tile, static scanlines.
- Scroll-driven motion ignores the OS "reduce motion" flag on purpose if the owner's machine has animations off (it hid scenes); only **ambient** motion (loops, particles, mouse parallax) respects it.
- Frames of a sequence are stacked `<img>`s, one shown at a time (a canvas version came up blank on a real machine). Equal slots per frame; repeat a frame to hold it longer.
- Lenis smooth scroll, driven by the GSAP ticker; time-based ease-out (duration ~1.3, wheelMultiplier ~0.75) so notches glide and add up.
- Mirrored worlds: figures face right; for right-hand copy the whole plate is mirrored with `scaleX(-1)` and cats/props re-mirrored.
- Far chapters are frozen with `content-visibility: hidden` (class `is-far`, set by an IntersectionObserver with a wide margin; read the LAST entry).

## The pieces

| Piece | Where | Notes |
|---|---|---|
| Scene data | `scenes/stageArt.ts` | all chapters |
| Stage | `scenes/ChapterStage.tsx` | draws beats, items, extras, overlays, progress line, measures fit |
| Effects | `scenes/fx.tsx` | world effects and overlays registered by name |
| Scrub helper | `scenes/useScrub.ts` | builds a timeline per chapter |
| Sequences | `motion/Sequence.tsx` | stacked frames |
| Hero 3D | `three/` | Canvas, avatar GLB (Draco), wardrobe recolour masks, error boundary (the page must survive no WebGL) |
| Cursor, clicks, cats | `fx/` | cursor with words, click bursts (mouse only), 8 cats with words, confetti when all found |
| Journey | `fx/Journey.tsx` | auto-scroll 1x..5.5x; stops on wheel/touch/key |
| Likes | `functions/api/likes.ts` | KV binding named `LIKES` |
| Layout | `layout/` | shape detection, zoom, rotation reload, visible height |

## Per-chapter progress line ("language")

One thin line per chapter drawn across the bottom as you scroll, in a form that matches the act: circuit trace, dimension line, waveform, ridgeline, ink stroke, warm wave. Revealed with a growing clip, not dashes (dashes split on a stretched stroke).

## Things that are cheap here and expensive elsewhere

Adding a chapter, changing a pose, re-timing a move, mirroring a scene, swapping a plate. Things that are expensive: anything per-device by hand (see `phone-and-layout.md`).
