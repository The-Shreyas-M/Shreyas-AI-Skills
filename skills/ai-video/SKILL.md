---
name: ai-video
description: The ONE command for all video work (/ai-video). Edit recordings into long videos, Shorts or Reels; make faceless animated reels from a script or voiceover; make a launch video of a project or site; schedule and post to YouTube/Instagram; build the launch guide. Asks what you have and what you want, then loads only the module needed.
---

# /ai-video: the single entry point

Keep tokens low: this file is the only video skill that is always listed. The modules below are NOT preloaded; **Read only the one you need** (its SKILL.md path is in the table). Do heavy work inside a subagent or a session started in the workspace folder; the main chat passes a short brief and receives a short report.

## Step 1: find out what the user has and wants (skip what they already said)
If the user gave arguments, infer both answers. Otherwise ask with ONE `AskUserQuestion` (two questions):
1. **What do you have?** raw video(s) of me talking / only a voiceover or a script (no footage) / a project or website to promote / already-edited videos / nothing yet.
2. **What do you want?** Shorts or Reels / a cleaned long video / a faceless animated reel / a launch (promo) video / schedule and post / a launch guide for a product.

## Step 2: route (Read the module file, then follow it)
| Situation | Module (Read this) |
|---|---|
| Owner's own talking-head video -> Shorts/Reels with b-roll, music, hook titles | `~/.claude/skills/shorts-from-main-video/SKILL.md` |
| Long video / podcast / YouTube URL: AI finds the best moments, auto face-reframe | `~/.claude/skills/clip-video/SKILL.md` |
| Drop videos in the workspace, delegate edit, approve, then post | `~/.claude/skills/ai-video-studio/SKILL.md` (workspace rules: `AI Video Editor/CLAUDE.md`) |
| No footage: explainer reel from a question or the user's voiceover (stick figures, 3D cartoon) | `~/.claude/tools/claude-animation-skills/skills/stick-figure/SKILL.md` or `.../zach-d-films/SKILL.md` |
| No footage: graph / map route / exploded view / minimal line art reel | `.../claude-animation-skills/skills/graph|map-route|breakdown|minimalistic-graphics/SKILL.md` |
| Launch video of a project or website (music, motion, share copy) | `~/.claude/tools/brag/skills/brag-slim/SKILL.md` |
| Titles, descriptions, tags, thumbnails, content strategy | skill `youtube` |
| Schedule / post (one or 40 clips) | workspace `posting/README.md` and `ai-video-studio`. Instagram = official Graph API only, setup: `~/.claude/skills/ai-video-studio/references/instagram-official-api.md` (never instagrapi) |
Faceless details and voice options: `references/faceless.md`. If a module folder is missing, run `python ~/.claude/skills/ai-video/scripts/install_modules.py`.

## Step 3: the standard pipeline (every route)
1. **Intake**: confirm files/script; never touch originals (`Raw Footage/` is read-only).
2. **Plan in one table** (clips, length, hook/title) only if the job is large; otherwise just do it.
3. **Edit/create** in a subagent (brief of at most 10 lines, report of at most 150 words: table file|length|title). Save into the workspace `Exports/<project>/`.
4. **Check** frames, levels, captions; say plainly that audio was not heard.
5. **Review gate**: the owner watches and approves, notes one at a time.
6. **Account gate**: ask WHICH accounts/channels to post to and WHEN. Never assume. Offer "none, I post manually".
7. **Post/schedule** only after an explicit go: dry run, show the plan, then `--execute`. Batch with a CSV.
8. Report links/times. Report failures verbatim.

## Creative rules (learned from a failed first cut; always apply)
1. **Hook first.** A Short must show AND say its hook in the first 1-3 seconds (a bold claim, a question, a result), before any context. If you clip an existing video, move the hook line to the start. Never open on "hi", a title card or a warm-up. Check frame 0-3 s before delivering.
2. **Lead with examples.** Promo or explainer videos open with the real result playing (phones/mockups with real footage), then explain. Show, do not describe.
3. **Captions come from the script when the audio is synthetic** (`shorts-from-main-video/scripts/align_script.py`): script words are displayed, Whisper only supplies timing, mismatches are printed and a mismatch like "Claude" heard as "clod" means the voice mispronounced it: reword and regenerate that clip. For real recordings, proof-read the transcript for names/brands first.
4. **Never reuse a music track** across videos or channels. Use a different licensed track per video (keep a `work/music/music.json` log of titles/licences and what was used where). Voice ducks the music; whooshes only at cuts.
5. **Elegant, not rigid:** clean type, generous spacing, soft gradients, glass cards, real footage in phone mockups, kinetic hook text; keep captions out of platform UI zones (top 220 px, bottom 420 px of vertical video).
6. Delegate mechanical work (music sourcing, frame extraction, example clips) to subagents with tight briefs; keep creative decisions and QA in the main chat.

## Hard rules
- Never post, publish or schedule without explicit approval after the owner saw the final files and chose the accounts.
- Never type passwords/tokens; the owner creates accounts and does logins (OAuth). Credentials stay local.
- Faceless/synthetic videos: no fake testimonials, no fabricated facts or statistics, no impersonating real people. If a cloned voice is used it must be the owner's own voice or a licensed voice.
- Music only if free for commercial use, source noted. Long videos: none unless asked.
- Third-party modules (claude-animation-skills, brag, clip-video) are MIT; keep licence notices.

## Dependencies (all modules)
Python 3.10+, ffmpeg full build (libass), Node 22+, Claude Code CLI. Module-specific installs are in each module's SKILL.md; `python scripts/install_modules.py` installs/updates the third-party ones into `~/.claude/tools/`.
