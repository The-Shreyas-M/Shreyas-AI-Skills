# Faceless / no-footage videos

When the owner cannot record: give a script or a voiceover; Claude builds the video and queues it for review and posting.

## Tools (installed in `~/.claude/tools/`, not listed as skills, so no token cost until used)
- **claude-animation-skills** (artemnovitckii, MIT): six skills, each a folder `skills/<name>/` with SKILL.md + build script + template, rendered by HyperFrames/three.js/Playwright on this PC:
  - `graph`, `minimalistic-graphics`, `map-route`, `breakdown`: quick reels from a small JSON spec (`name.graph.json` -> `build.py` -> 1080x1920 mp4).
  - `stick-figure` and `zach-d-films`: full explainer reels (script, voiceover, word-timed captions, music/SFX made in code). They need a voiceover and word timings.
- **brag-slim** (latent-spaces, MIT): turns a project directory or a website URL into a ~20 s launch video with music and share copy (`brag-output/`). Use it to promote the owner's site, a product or an app.
- **HyperFrames** (heygen-com, Apache-2.0): HTML -> deterministic MP4 renderer used underneath (`npx hyperframes@0.8.34`). For custom motion graphics: `npx skills add heygen-com/hyperframes` (adds its authoring skills) only when the owner wants hand-built animations.
- Remotion is an optional alternative renderer (own licence terms for companies).

## Voiceover options (be honest with the owner)
1. **Owner records a voiceover** (phone voice memo is fine; quiet room, 1 s pauses, short lines). Best option: it is the owner's real voice. Word timings: `skills/shorts-from-main-video/scripts/transcribe.py` (faster-whisper) or the kit's `words.py` (needs `--voice` models).
2. **Owner's cloned voice**: made by the owner on a voice-cloning service of their choice with their OWN voice, exported as an audio file and dropped in `Raw Footage/`. Claude does not clone voices and never impersonates anyone else.
3. **Free built-in synthetic voice** (Kokoro, preset voices, not a clone): `bash kit/setup.sh --voice` (about 1 GB of models, optional). Fine for faceless explainers; say it is synthetic where platforms require disclosure.

## Windows notes (verified setup on this PC)
- The kit's installer expects macOS/Linux. A `python3` shim in `~/.claude/tools/shims` and `bash` (Git Bash) make `kit/setup.sh` work. `kit/.venv/bin/python` paths used by `--voice` differ on Windows (`Scripts/python.exe`): adapt before using the voice option.
- Rendering uses Playwright's Chromium (downloaded by setup) and HyperFrames via npx.

## Flow
Script (or voiceover) -> choose engine -> subagent builds in `work/<project>/` -> mp4 into `Exports/<project>/` -> frames checked -> owner approves -> choose accounts -> schedule (see `ai-video`). Add on-screen disclosure or description note "AI-generated animation / synthetic voice" when relevant. No fabricated facts or testimonials.
