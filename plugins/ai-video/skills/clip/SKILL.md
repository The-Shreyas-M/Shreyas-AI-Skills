---
name: clip
description: Cut vertical Shorts/Reels from a long video, podcast or YouTube URL (/ai-video:clip) - transcribe, pick self-contained moments, auto face-reframe to 9:16, optional captions, zooms and sound effects.
argument-hint: "[video file or URL, number of clips]"
---

# /ai-video:clip

1. Engine: `~/.claude/tools/video/clip-video/` (third-party, Devini Community Edition, MIT; keep `LICENSE` and notices). If missing: `python "${CLAUDE_PLUGIN_ROOT}/engines/install_engines.py"`, then `python install.py` inside that folder once (creates its own `.venv`).
2. **Read `~/.claude/tools/video/clip-video/SKILL.md` and follow it.** "The repo root" there means `~/.claude/tools/video/clip-video`: `cd` there and use `python run.py ...`.
3. Picking moments is your judgement (its `references/picking-moments.md`); cutting and rendering is mechanical: give that to the worker (opencode first).
4. The rules of `/ai-video:start` apply: hook first, review gate, account gate.
5. Done -> `/ai-video:post` for approval and scheduling. Never post from here.

The owner's own scripted talking-head video with b-roll and music -> `/ai-video:shorts` instead.
