# Posting and scheduling

`post.py` posts or schedules approved videos. Dry-run is the default.

## One-time setup (the owner does this; Claude never types passwords)
1. Python env: `Tools/.venv` is created by `setup_workspace.py`. Packages: google-api-python-client, google-auth-oauthlib, python-dotenv (+ instagrapi only if you want Instagram).
2. YouTube login:
   - Google Cloud Console -> new project -> enable **YouTube Data API v3** -> OAuth consent screen (External, add yourself as test user) -> Credentials -> **OAuth client ID, Desktop app** -> download the JSON.
   - Save it as `posting/client_secrets.json` (git-ignored). Copy `.env.example` to `.env` if you want other paths.
   - Run `Tools\.venv\Scripts\python.exe posting\post.py auth` and log in with the **channel you want to post to**. Choose the right brand-channel in the Google account picker.
   - Run `post.py whoami`, then set `expected_channel` in `queue.json` to that exact channel title. Posting halts if they ever differ.
   - YouTube API note: videos uploaded through an unverified API project may be forced private. If so, request an audit or upload through Studio. Per-channel upload limits apply (about 100 a day was observed); the run stops cleanly when hit.
3. Instagram (optional, unofficial `instagrapi`, risk of action blocks: keep to a few reels a day): put IG_USERNAME / IG_PASSWORD in `.env` yourself.

## Normal flow
```
post.py add "Exports/proj/short-1.mp4" --platform yt --title "My first avatar failed" --description "..." --when "2026-11-20 19:30"
(owner watches the video)            post.py approve short-1
post.py plan                          post.py run --platform yt --max 3          # dry run
post.py run --platform yt --max 3 --execute                                       # real
```
- `when` is local time in `queue.json` `timezone_offset` (default +05:30). YouTube takes the upload as private with a `publishAt`, so the PC does not need to be on at publish time. Slots must be >= 15 min away (YouTube) / 25 min (Instagram).
- Re-running is safe: finished jobs are skipped, matching titles already on the channel are adopted, ambiguous failures halt and need a manual look (never blind retries).
- Other platforms (TikTok, Facebook, Shorts via app): `post.py pack <id>` copies the file and caption into `Exports/_manual/<id>/`.
- A daily scheduled resume can be set with Windows Task Scheduler running `post.py run --platform yt --max 40 --execute`.

## Files (all git-ignored except post.py, README, queue example)
`.env`, `client_secrets.json`, `token.json`, `ig_session.json`, `ledger/`, `queue.json`.
