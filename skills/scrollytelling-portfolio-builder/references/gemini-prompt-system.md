# The image prompt system (Gemini, but any image model works)

Goal: dozens of images that look like one world and show the same person every time, cheap to cut out and drop into scenes. What worked is a **lock + one-at-a-time + exact file names + one tracking file**.

## 1. The `GEMINI_PROMPTS.md` file (the ONE file)

Sections, in this order, kept up to date as work proceeds:

1. **How to use** (one minute): new chat per group; first message = reference image + LOCK; then one prompt per message; save results under the exact file name into `art/gemini/`; if the face drifts send the FIX-UP; stop at the daily limit and continue from the first unticked item.
2. **The locks** (below).
3. **STILL TO GENERATE** (ordered by importance, most important first).
4. **ALREADY GENERATED** (each with a status: saved / used / not used yet; the prompt kept for redoing).
5. **ARCHIVED / optional** (extra poses, polish frames).
6. Special: favicon prompt.

Each prompt sits in its own code box (one click copies it), under a bold exact file name:
`**`p-camera-tripod.png`** ✅ saved as `p-camera-tripod.jpg`` then the prompt in a box.

## 2. File-name convention (the scripts depend on it)

- `a<act>-<name>.png` figures of the person (a1.. a6, `fin` for finale); names ending in `-kata`, `-dyno`, `-walk`... are **strips** (several poses in one image).
- `p-<name>` props; `cat-<name>` cats; `bg-<name>` backgrounds (never keyed).
- Optional `_f1`, `_f2` suffix = separate single frames of one sequence.

## 3. The locks (paste once at the start of a chat; replace the bracketed parts)

**LOCK A, people** (attach the reference image):
```
Use the attached reference image as the exact character: the same [man/woman/person], same face, [glasses], [hair], [facial hair], same [skin tone], [build], about [height] tall, in the same premium 3D cartoon style (smooth clay-like surfaces, soft studio shading, no realistic skin pores). Full body visible from head to feet, nothing cropped. Background: one perfectly flat solid bright green (#00B140) with no gradient, no floor, no shadow on the ground, no props touching the edges, no text, no watermark. Soft even lighting from the front. Output 2048 px on the long side. I will now send you one pose or scene at a time. Reply only with the image.
```

**LOCK B, single objects and animals**:
```
You will make one isolated object at a time in the same premium 3D cartoon style as the attached reference (smooth clay-like surfaces, soft studio shading, no realistic textures). Show the whole object, centred, with margin, on one perfectly flat solid bright green (#00B140) background, with no floor, no shadow, no text, no watermark, no real brand names or logos. Output 2048 px on the long side. I will send one object at a time. Reply only with the image.
```

**LOCK C, backgrounds**:
```
You will make one wide 16:9 cinematic background plate at a time, in the same stylised 3D cartoon look as the attached reference, dark and moody with soft depth of field. Completely empty of people. No text, no logos, no watermark. Keep the LEFT 40% of the frame calmer and darker (a headline sits there) and put the visual interest in the right 60%. Output 2560 x 1440. I will send one scene at a time. Reply only with the image.
```

**FIX-UP** (when face or body drifts):
```
Good, but keep the [person] exactly as in the reference image: same face, [glasses], [hair], [facial hair] and body proportions, in the same 3D cartoon style. Only the pose and clothes should differ. Keep the background a perfectly flat solid green (#00B140) with no shadow.
```

## 4. Prompt patterns that worked

- **Person pose**: one sentence of action + the outfit + the prop in hand: "kneeling at a workbench, soldering a small board, wearing a work apron".
- **Strip**: "a horizontal strip of 3 full-body side-view poses of [move], same person and outfit in all three, wide empty green gaps between them: (1) set up, (2) mid-move, (3) finish".
- **Walk cycle**: a 4-frame side-view strip; stack the frames as images and show one at a time.
- **Prop**: object description, "no brand names, no logo".
- **Cats**: one style for all, "every cat a different colour": a cute cat sitting upright, front view, head slightly tilted, big eyes, [coat].
- **Background**: place + light + mood; ask for the empty left 40%.
- Ask for scenes the owner actually does (their real hobbies), and describe their real outfit for each activity, or the outfit drifts.

## 5. Quality rules learned

- Keep a strip in a single generation (frames must match).
- If a prop looks cut off or merges with the green, regenerate it; do not fix in code.
- Match head size across frames of one move with a per-frame scale in the stage data, not by regenerating.
- Generated images carry a small sparkle watermark in the bottom-right corner: the key script clears the corner.
- Budgets: a still <= 250 KB, a strip <= 1.5 MB as WebP.
- Videos were tried and dropped: stacked still frames are lighter and more reliable.
