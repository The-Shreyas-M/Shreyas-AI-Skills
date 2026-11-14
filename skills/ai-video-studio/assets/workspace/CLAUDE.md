# AI Video Editor: workspace rules (read first, keep answers short)

This folder is a video studio. Any Claude chat may use it: **edit videos, get the owner's approval, then post/schedule.**
Token rule: do the heavy work inside ONE subagent/session started in this folder; the caller only passes a 5-10 line brief and receives a <=150-word report with file paths. Never paste transcripts, logs or frames into the chat.

## Folders
| Folder | Purpose | Rule |
|---|---|---|
| `Raw Footage/` | originals dropped by the owner | **never modify, move or delete** |
| `References/` | style references + `brand-sheet.md` | read `brand-sheet.md` before every edit (if it exists) |
| `Exports/<project>/` | finished videos, `.srt`, `post.json` per video | the only place edits are written |
| `work/<project>/` | scratch (transcripts, clips.json, configs) | safe to delete after approval |
| `Tools/` | venv, requirements | |
| `posting/` | queue, ledger, `post.py`, `.env` (secrets, git-ignored) | see "Posting" |

## Edit job (what a subagent does)
Input: video path(s) in `Raw Footage/`, desired output (long video / Shorts / Reels), style notes.
1. Pick the engine (skills installed globally):
   - Owner talking head + wants b-roll/screen footage, music, hook titles -> skill `shorts-from-main-video` (`make_short.py`, config JSON, use `--check` first).
   - Long video or someone else's/podcast-style video, AI picks the best moments, auto face-reframe -> skill `clip-video` (`python run.py fetch|cut|edit` run inside its folder `~/.claude/skills/clip-video`).
   - Plain trim / cut dead air / export -> ffmpeg directly (full build is on PATH).
2. Transcribe with word timestamps (both skills do it). Fix mis-heard names via `fix_words`.
3. **Boundary check** (`--check` / `cut --check`): every clip starts on a hook and ends on a payoff, 15-60 s for Shorts.
4. Render into `Exports/<project>/`. Verify: pull 3 frames per video and LOOK (face bright and unaltered, captions not overlapping, nothing in the top 220 px / bottom 420 px / right 120 px UI zones), `volumedetect` mean about -16 dB, max under -1 dB. You cannot hear audio: say so.
5. Write `Exports/<project>/post.json` per video (title, description, hashtags, pinned comment, platform list). Use skill `youtube` for titles/SEO.
6. Report to the caller: a table `file | length | title`, plus anything uncertain. **Stop. The owner watches and confirms.** Never post in the same step as editing.
Music: only tracks free for commercial use without attribution (Pixabay Content License, YouTube Audio Library); note the source in post.json. Main long videos: no music unless told.
Never darken or "improve" the owner's face. Never invent words the speaker did not say.

## Posting (only after explicit "post it" / "schedule it")
Everything is in `posting/`. Details: `posting/README.md`. Core commands (run with the workspace python: `Tools/.venv/Scripts/python.exe`):
- `post.py add <video> --platform yt --when "2026-11-20 19:30" ...` or edit `posting/queue.json`
- `post.py plan` (validates, shows ledger, no network) -> `post.py whoami` (prints which YouTube channel the token controls; must equal `expected_channel`) -> `post.py run --platform yt --max 3` (dry run) -> add `--execute` only when the owner said go.
- Queue items need `"approved": true` (set by `post.py approve <id>` after the owner confirmed). Unapproved items are never posted.
- Safety design (do not weaken): ledger with unique key + claim-before-upload, adopt-existing-by-title, halt on any ambiguous error, never auto-retry ambiguous, dry-run default, lock file, `expected_channel` check, YouTube per-channel upload limit stops the run cleanly.
- Never type or print passwords/tokens. `.env`, `token.json`, `client_secrets.json`, `ig_session.json` stay local and git-ignored. The owner creates accounts and does OAuth login themselves (`post.py auth`).
- YouTube = official API (scheduled via `publishAt`, PC need not stay on). Instagram = unofficial `instagrapi` (risk of action blocks, keep pace slow, max a few per day) and is optional. TikTok/others: `post.py pack` writes caption + file for manual upload.

## Style
Read `References/brand-sheet.md` if present. House look of the existing Shorts: split screen (b-roll top, face bottom), word-by-word yellow captions, hook title, progress bar, 1.1x speed, quiet whooshes, ducked calm-phonk music.
