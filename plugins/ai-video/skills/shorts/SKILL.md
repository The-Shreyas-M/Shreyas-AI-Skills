---
name: shorts
description: Turn the owner's own talking-head video into punchy vertical Shorts/Reels/TikToks (/ai-video:shorts) - b-roll on top, face underneath, word-by-word captions, hook title, progress bar, free music that ducks under the voice. Also the filming guide so footage edits well.
argument-hint: "[video file and how many Shorts]"
---

# /ai-video:shorts

1. Engine: `~/.claude/tools/video/shorts-from-main-video/`. If missing: `python "${CLAUDE_PLUGIN_ROOT}/engines/install_engines.py"`.
2. **Read `~/.claude/tools/video/shorts-from-main-video/SKILL.md` and follow it** (setup, filming guide, picking the story, b-roll, music, render, checks). Run its scripts from that folder.
3. The rules of `/ai-video:start` apply: hook first, worker does the rendering (opencode first), review gate, account gate.
4. Done -> hand over to `/ai-video:post` for approval and scheduling. Never post from here.

Long video, podcast or someone else's talk where the AI must FIND the moments -> `/ai-video:clip` instead.
