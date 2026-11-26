---
name: start
description: The one entry point for all video work (/ai-video:start). Edit recordings into long videos, Shorts or Reels; clip the best moments of a long video or URL; make faceless animated reels from a script or voiceover; make a launch video of a project or site; review, schedule and post to YouTube/Instagram. Asks what you have and what you want, then hands over to the right /ai-video:start sub-skill.
argument-hint: "[what you have and what you want]"
---

# /ai-video:start

Engines live in `~/.claude/tools/video/` (not listed as skills, so they cost nothing until used). If that folder is missing or a sub-skill says an engine is missing, run once:
`python "${CLAUDE_PLUGIN_ROOT}/engines/install_engines.py"`

## Step 1: what the owner has and wants (skip what they already said)
If arguments were given, infer both. Otherwise ask ONE `AskUserQuestion` with two questions:
1. **What do you have?** raw video of me talking / a long video, podcast or URL / only a voiceover or script / a project or website to promote / finished videos / nothing yet.
2. **What do you want?** Shorts or Reels / a cleaned long video / a faceless animated reel / a launch video / schedule and post / a launch guide for a product.

## Step 2: route — invoke that sub-skill and follow it
| Situation | Sub-skill |
|---|---|
| Owner's own talking-head video -> Shorts/Reels with b-roll, music, hook titles | `/ai-video:shorts` |
| Long video / podcast / YouTube URL: AI finds the best moments, auto face-reframe | `/ai-video:clip` |
| No footage: explainer or graphic reel from a script or voiceover; launch video of a project or site | `/ai-video:faceless` |
| Videos are done (or dropped in the workspace): review, approve, schedule, post | `/ai-video:post` |
| Titles, descriptions, tags, thumbnails, strategy | skill `youtube` |
| A one-file launch guide for a product | skill `one-file-launch-guide` |

## Step 3: the standard pipeline (every route)
1. **Intake**: confirm files or script; never touch originals (`Raw Footage/` is read-only).
2. **Plan in one table** (clips, length, hook/title) only if the job is large; otherwise just do it.
3. **Edit/create through a worker**, not in this chat: brief of at most 10 lines, report of at most 150 words (table file | length | title). Worker order: free model via `opencode run` (default `opencode/beam-free`, brief in a file, the tested command from the knowledge base `approach.md`) -> a Claude subagent only if opencode fails twice. Output into the workspace `Exports/<project>/`.
4. **Check** frames, levels, captions; say plainly that audio was not heard.
5. **Review gate**: the owner watches and approves; notes one at a time.
6. **Account gate**: ask WHICH accounts/channels and WHEN. Never assume. Offer "none, I post manually".
7. **Post/schedule** only after an explicit go (`/ai-video:post`).

## Creative rules (learned from a failed first cut; always apply)
1. **Hook first.** A Short shows AND says its hook in the first 1-3 s (bold claim, question, result), before any context. When clipping, move the hook line to the start. Never open on "hi", a title card or a warm-up. Check frames 0-3 s before delivering.
2. **Lead with examples.** Promo/explainer videos open with the real result playing, then explain. Show, do not describe.
3. **Captions come from the script when the audio is synthetic** (`~/.claude/tools/video/shorts-from-main-video/scripts/align_script.py`): script words shown, Whisper only times them; a mismatch like "Claude" heard as "clod" means the voice mispronounced it: reword and regenerate. For real recordings, proof-read names and brands first.
4. **Never reuse a music track** across videos or channels; log titles and licences in `work/music/music.json`. Voice ducks the music; whooshes only at cuts.
5. **Elegant, not rigid:** clean type, generous spacing, soft gradients, real footage in phone mockups, kinetic hook text; keep captions out of platform UI zones (top 220 px, bottom 420 px of vertical video).

## Hard rules
- Never post, publish or schedule without explicit approval after the owner saw the final files and chose the accounts.
- Never type passwords or tokens; the owner does logins (OAuth). Credentials stay local.
- Faceless/synthetic: no fake testimonials, no invented facts or statistics, no impersonating real people; a cloned voice only of the owner or a licensed voice.
- Music only if free for commercial use, source noted. Long videos: none unless asked.
- Third-party engines (clip-video, claude-animation-skills, brag) are MIT: keep their licence notices.

## Dependencies
Python 3.10+, ffmpeg full build (libass), Node 22+, Claude Code CLI. Engine installs: `install_engines.py` above; third-party animation and launch tools: `python ~/.claude/tools/video/scripts/install_modules.py`.
