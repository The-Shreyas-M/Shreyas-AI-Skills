---
name: shorts-from-main-video
description: Turn a talking-head main video (phone recording of the creator explaining something) into punchy vertical YouTube Shorts / Reels / TikToks - b-roll on top, big face underneath, word-by-word yellow captions, hook title, progress bar, 1.1x speed, free calm-phonk music that ducks under the voice. Also gives the creator a filming guide so the footage edits well, and covers how to record screen b-roll and source license-free music. Use when the user wants Shorts from a video, asks how to record a video that will be easy to edit,.
---

# Shorts from a main video

Proven recipe (3 Shorts from one 2-minute phone video). Pipeline: **record -> transcribe -> pick lines -> b-roll -> render -> check -> post**. Everything runs locally with ffmpeg + faster-whisper. No paid editor.

## v2: best of both worlds (what changed)

Ours = story-driven edit of the creator's own video (b-roll + face split screen, music, hook titles). Adopted from the professional **Devini Claude Video Clipper** (MIT, installed separately as skill `clip-video`):
- `--check` boundary validator (warns on mid-sentence starts/ends and clips outside 15-60 s) and `scripts/find_phrase.py` for word-accurate times; custom `ranges` snap to whole words.
- `references/picking-moments.md`: hook types, story shape, ending traps, scoring (credited, MIT).
- `"face_crop": "auto"`: YuNet face detection (bundled model) frames the face; `face_headroom` tunes how wide.
- Per-part zoom (`"zoom": "open|push|punch|none"`; default open on part 1, then alternating punch/push), quiet whooshes on the opening and each cut (`"sfx": "light|none"`, synthetic MIT sounds), `.srt` written next to the video, token merging ("$500", "100%"), knobs `accent`, `caption_y`, `caption_size`, `uppercase`, bundled Montserrat ExtraBold fallback font.

**Which skill when:** creator's own scripted video + wants b-roll/music/titles -> this skill. A long video, podcast or someone's talk where the AI must FIND the best moments and auto-reframe faces -> `clip-video`. Orchestrated from any chat via `ai-video-studio`.

## 0. Setup (once) - all dependencies

| Need | Required? | Install |
|---|---|---|
| Python 3.9+ | yes | python.org |
| faster-whisper, numpy, imageio-ffmpeg, pillow | yes | `pip install -r requirements.txt` (in this skill folder) |
| ffmpeg **full build with libass** (captions) + sidechaincompress/loudnorm | yes | comes with `imageio-ffmpeg`; or a "full" build from gyan.dev / `brew install ffmpeg` and set env `FFMPEG` |
| Impact font (or any bold .ttf via `font_file`) | no | Windows has it; else Anton from Google Fonts |
| `opencv-python<5` (only for `face_crop: "auto"`) | no | `pip install "opencv-python<5"` |
| Node.js 18+ and `playwright-core` + Chromium | only to record website b-roll | `npm i playwright-core && npx playwright install chromium` |
| Skill `youtube` (titles, SEO, thumbnail briefs) | recommended | installed by this repo's `install.py` |
| Skill `playwright-cli` / a browser tool | for b-roll and for reading the Pixabay track page | `npx skills add https://github.com/microsoft/playwright-cli --skill playwright-cli` |

Verify everything: `python scripts/check_setup.py` (prints exactly what to install). Nothing here needs a GPU or paid account; transcription of a 2-minute video takes about a minute on CPU.

`scripts/ffmpeg_path.py` finds ffmpeg (env `FFMPEG`, then PATH, then imageio's bundled full build, which has libass for captions). Plain `ffmpeg` on PATH is often a slim build with no `ass` filter: check `ffmpeg -filters | grep ass`.

## 1. Tell the creator how to film (give them `references/recording-guide.md`)

Share it BEFORE they record. The footage quality decides the edit quality. Short version:
- Window light in front of you, phone at eye level, landscape or portrait both work, head and shoulders, 1-2 m from the window.
- Read short lines, one idea per line, pause 1 second between lines (the edit cuts on pauses).
- Say the hook first, say numbers and one story of failure, end with the call to action.
- Record 2-3 takes and keep going after mistakes: repeat the line cleanly, the transcript picks the best.
- Give them a script split into numbered short lines if they ask for one (see recording guide).

## 2. Prepare the source

1. Copy the phone file into the work folder. If ffmpeg complains `Invalid color space`, remux with a bitstream filter:
   `ffmpeg -i in.mp4 -c copy -bsf:v h264_metadata=colour_primaries=1:transfer_characteristics=1:matrix_coefficients=1 fixed.mp4`
2. Transcribe: `python scripts/transcribe.py fixed.mp4 work/` -> prints numbered lines `L0, L1, ...` with timestamps and writes `work/tr.json`.
3. Read the transcript. Fix names the model spelled wrong via `fix_words` in the config (e.g. `"Kubernets": "Kubernetes"`).

## 2b. Hook-first rule (non-negotiable)
The first 1-3 seconds must contain the hook, both spoken and on screen (title text from frame 0). When clipping, MOVE the hook line (or the most surprising line) to the start; use a `ranges` splice with the hook first and the context after it. A Short that starts with context is a failed Short. After rendering, look at frames 0, 15 and 45 (0 s, 0.5 s, 1.5 s): the hook text and a moving visual must already be there.
Synthetic/known script? Do not use Whisper text for captions: use `scripts/align_script.py` (script words + Whisper timing, prints mismatches). Never reuse a music track across videos.

## 3. Pick the story of each Short (20-22 s each)

Each Short = 3 parts, ~6-8 s each, built from transcript lines:
1. **Hook** - the most surprising line + its b-roll. Title text on screen for the first 3 s ("MY FIRST AVATAR|FAILED").
2. **Proof/story** - 2-4 lines that show the thing (hidden cats, the failure, the number).
3. **Payoff + CTA** - the closing line, with a text overlay like "BUILT IN 14 DAYS" or "LINK IN DESCRIPTION".

Make 3 different angles from the same video (what / what-went-wrong / the-hard-part). Lines may be reused across Shorts. Pad with `ranges` (seconds) when a line needs custom trimming.

## 4. Get b-roll (top half of the frame)

Anything that moves and is on-topic: screen recordings of the site/app/product, covers or screenshots (still images get a slow zoom), outfit/feature close-ups. Screen-record in real time at 1920x1080:
- Playwright (headless Chromium with GPU) + CDP `Page.startScreencast` saved as numbered JPEGs, then ffmpeg concat with the real frame durations. Smooth scroll by integrating a velocity profile and setting scroll position every frame (an easing hold at the start, a fast section, a slow section). The mouse must be parked off-content or it looks like a laggy cursor.
- One long continuous "master" scroll take (60 s) is the best b-roll: cut sections from it with `broll_start`.
- Never let b-roll sit still for more than 2 s. If the site fights programmatic scroll (watchdogs, smooth-scroll libs), run a local dev build with a debug flag.
- Dark first frames look broken: pick `broll_start` where the content is visible.

## 5. Music (free, no licence trouble)

Use only tracks that are explicitly free for commercial use without attribution: **Pixabay Content License** (pixabay.com/music, search "phonk", filter genre) or YouTube Audio Library. Process used for the Shorts: calm/chill phonk, ~3 min track, started 12-75 s in (`music_start`) to skip the intro, `music_volume` 0.55, sidechain-ducked under the voice, 0.6 s fade in, 1.2 s fade out.
- Pixabay blocks plain downloads with 403. Open the track page in a browser and read the real mp3 URL from the page (`document.querySelector('audio').src` in the console), then download that.
- Check the licence text on the track page before posting; keep the page URL in your notes.
- Do NOT generate music with code (tried: it sounded bad and wasted time). The main long video gets NO music (voice only).

## 6. Render

Copy `references/config-example.json` next to the footage, edit, then:
```bash
python scripts/make_short.py config.json
```
Output: 1080x1920, 30 fps, h264/aac, about 15 Mbit/s, -14 LUFS, speed 1.1 (a bit faster = less boring; change `speed`).
Layout: black canvas, b-roll 1080x608 at y=110, face 1080x1000 at y=740, captions centred at y=830, title at the top, yellow progress bar at the bottom. `face_crop: [x, y, w, h]` frames the face (source pixels); `null` = whole frame. A part with no `broll` is a full-screen face beat (good for the last emotional line).
Work files go in `_work_<name>/` (delete after).

## 7. Check before saying done

- Pull 3-4 frames per Short (`ffmpeg -i s.mp4 -vf "select='eq(n,20)+eq(n,150)'..,tile"`) and LOOK: face bright and unaltered, captions not overlapping, title readable, b-roll visible and not black.
- `volumedetect`: mean about -16 dB, max under -1 dB.
- You cannot hear the audio: say so, and ask the creator to play each Short once before posting.
- Do not darken, grade or "improve" the face. A shadow/ring graphic must go BEHIND/around the face, never over it (an earlier version hid the face under a dark overlay and the creator rightly objected).

## 8. Post (give the creator this)

Shorts clipped from a main video must point to it: set **Related video** (Studio -> Details) to the main video, and put its link in the description. With `ai-video-studio`'s poster: `--related <main video>`, then `post.py related` for the Studio checklist.

One Short per day after the main video. Title = the hook in plain words ("My first avatar failed"). Description: one sentence + `#shorts` + 3 tags + link. Pin a comment with the main video / product link. Save titles and descriptions for all videos in one md file next to the videos.

## Gotchas that cost time before

- Windows ffmpeg `ass=` filter: absolute paths with `C:` break parsing. The script copies fonts next to the work dir and uses relative names with `cwd` set. Newline in ASS text is `\N` (written from Python as `r"\N"`).
- faster-whisper on newer PyAV: pass a numpy array, not a path (done in transcribe.py).
- Overlapping caption events render as garbled text: the script clips each caption's end to the next start.
- Concat of re-encoded beats must have identical fps/pix_fmt/audio rate (the script forces 30 fps, yuv420p, 48 kHz stereo).
