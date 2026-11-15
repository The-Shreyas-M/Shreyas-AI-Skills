---
name: ai-video-studio
description: The AI Video Editor workspace (folder "AI Video Editor": Raw Footage, References, Exports, posting queue). Use in ANY chat when the user wants videos edited (long video, Shorts, Reels) from files they dropped in that folder, wants to review and approve the result, and then wants it posted or scheduled on YouTube/Shorts/Instagram. Handles delegation to a subagent or a second Claude Code session in that folder to keep tokens low, and a safe approve-then-post pipeline. Also sets the workspace up from scratch on a new machine.
---

# AI Video Studio

Workspace: its path is in `~/.claude/ai-video-editor.json` (key `workspace`; default `~/AI Video Editor`). Find it first; do not recreate if it exists. Everything the worker must follow is in that folder's **`CLAUDE.md`**; how the user uses it is in **`START-HERE.md`**; posting in **`posting/README.md`**.

## When invoked in a chat
1. Locate the folder. If it is missing, set it up: `python <skill>/scripts/setup_workspace.py` (creates folders, rules, posting module, posting venv; re-runnable).
2. Identify the videos (the user says a file name or "whatever is in Raw Footage"). Do not read or transcribe them yourself.
3. **Delegate the whole edit** (this is what keeps tokens low). Pick one:
   - Subagent: `Agent` tool, `general-purpose`, prompt = a brief of at most 10 lines: working folder, the file(s), desired output (e.g. "3 Shorts of 20-40 s + cleaned long cut"), style notes, "read CLAUDE.md in that folder and follow it; report at most 150 words: table file|length|title; do not post".
   - Separate session (user wants to watch/steer it): `start_session` with `cwd` = the folder, same brief.
   - Headless: `run-edit.ps1 "<brief>"` in the folder (runs `claude -p`).
   Forks of this chat are the expensive option: avoid.
4. Relay the report briefly: files, lengths, titles. Tell the user to watch `Exports/<project>/` and reply with notes (one at a time) or "approved". You do not post yet.
5. On notes: send ONE follow-up to the same worker (`SendMessage`) with only the change. Never re-run the whole job.
6. On "approved" + a destination ("YouTube Shorts, one a day at 7:30 pm"): delegate or run `post.py add ... --when ...`, `post.py approve <id>`, `post.py plan`, dry-run, show the plan, and only run `--execute` after the user says go. Instagram: warn it is unofficial; ALL Instagram reels are uploaded as Trial Reels (non-followers first, for discovery) and the poster halts if the account is not eligible. Other platforms: `post.py pack`.
6b. **Clipped Shorts**: when Shorts are cut from a main video, queue them with `--related <main video>` (main video uploaded first) so the description links it, then run `post.py related` and set YouTube's "Related video" field in Studio (API cannot; offer to do it in the owner's browser, with explicit OK).
7. Confirm what was done with channel name, times and links. Report failures verbatim; never retry an AMBIGUOUS job.

## Rules that never bend
- Never modify `Raw Footage/`. Never post without explicit approval after the user saw the final files. Never put passwords/tokens in chat; the user creates accounts and does the one-time YouTube login (`post.py auth`).
- `expected_channel` must match the channel the token controls (prevents posting to the wrong channel).
- Music: only free-for-commercial-use tracks with the source noted.
- You cannot hear audio; frames and levels are checked, then the user listens.

## Engines the worker uses (installed skills)
`shorts-from-main-video` (creator's own talking head + b-roll, music, hook titles), `clip-video` (long video, AI picks moments, face auto-reframe), `youtube` (titles, SEO), ffmpeg for plain edits.

## Dependencies
Python 3.10+, ffmpeg full build with libass (on PATH or imageio-ffmpeg), the two engine skills above (+ their venv: `clip-video/install.py`), Claude Code CLI (`claude`) for headless runs, Google Cloud project with YouTube Data API v3 + OAuth Desktop client (owner creates), optional `instagrapi`. Optional motion-graphics upgrade (not required): Remotion and HyperFrames, as in the third-party "AI Video Editing Setup Guide" (@decode.dani): add only if the owner wants animated graphics beyond captions/zooms.
