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
1. Pick the engine (skills installed globally; entry point for the owner is `/ai-video`; read only the SKILL.md you need):
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
After the owner approves an edit, **ASK which account(s) each video goes to** (list them with `post.py accounts`; offer "none, I will post manually") and when (a date/time, or "one per day at 19:30"). Never assume an account. Details: `posting/README.md`. Run with `Tools/.venv/Scripts/python.exe`:
- One video: `post.py add <video> --accounts a,b --title T --when "YYYY-MM-DD HH:MM"`. Many (e.g. 40): fill `posting/schedule.csv` and `post.py import schedule.csv --start DATE --times 07:30,19:30 --per-day 2`.
- `post.py plan` -> show the owner the table -> owner watched/confirmed -> `post.py approve <id|all>` -> dry run `post.py run --account NAME --max N` -> `--execute` only on an explicit "go". Repeat per account.
- **Clipped Shorts: always link the main video.** Queue them with `--related <main video id|queue id|URL>` (upload the main video first). The poster adds the full-video link to the description; YouTube's Studio-only "Related video" field is then set from the checklist `post.py related` (offer to do it via the owner's browser, with explicit OK).
- Safety design (do not weaken): approved-only, ledger with unique key + claim-before-upload, adopt-existing-by-title, halt on any ambiguous error (never auto-retry), dry-run default, lock file, per-account `expected_channel` check, upload-limit stops cleanly.
- Never type or print passwords/tokens. `.env`, `token*.json`, `client_secrets.json`, `ig_*.json`, `accounts.json` stay local and git-ignored. The owner creates accounts and does each one-time login (`post.py auth --account NAME`).
- YouTube = official API (scheduled through `publishAt`, PC need not stay on). Instagram = unofficial `instagrapi` (action-block risk: slow pace, few per day), optional; **all Instagram reels go out as Trial Reels** (`trial` default true, non-followers first, halts if the account is not eligible). TikTok/others: `post.py pack <id>` for manual upload.

## Style
Read `References/brand-sheet.md` if present. Default house look of the Shorts: split screen (b-roll top, face bottom), word-by-word yellow captions, hook title, progress bar, 1.1x speed, quiet whooshes, ducked calm-phonk music.
