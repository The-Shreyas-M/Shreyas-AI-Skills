# Posting and scheduling

`post.py` posts or schedules approved videos. Dry-run is the default.

## One-time setup (the owner does this; Claude never types passwords)
1. Python env: `Tools/.venv` is created by `setup_workspace.py`. Packages: google-api-python-client, google-auth-oauthlib, python-dotenv (+ instagrapi only if you want Instagram).
2. YouTube login:
   - Google Cloud Console -> new project -> enable **YouTube Data API v3** -> OAuth consent screen (External, add yourself as test user) -> Credentials -> **OAuth client ID, Desktop app** -> download the JSON.
   - Save it as `posting/client_secrets.json` (git-ignored). Copy `.env.example` to `.env` if you want other paths.
   - Run `Tools\.venv\Scripts\python.exe posting\post.py auth --account my-channel` and log in with the **channel you want to post to**. Choose the right brand-channel in the Google account picker.
   - Run `post.py whoami --account my-channel`, then set `expected_channel` in `accounts.json` to that exact channel title. Posting halts if they ever differ.
   - YouTube API note: videos uploaded through an unverified API project may be forced private. If so, request an audit or upload through Studio. Per-channel upload limits apply (about 100 a day was observed); the run stops cleanly when hit.
3. Instagram (optional, unofficial `instagrapi` >= 3.2, risk of action blocks: keep to a few reels a day): put IG_USERNAME / IG_PASSWORD in `.env` yourself.

## Accounts (several channels / Instagram accounts)
Copy `accounts.json.example` to `accounts.json` and name each account (`my-channel`, `second-yt`, `main-ig`...). Each YouTube account has its own `token_file` and `expected_channel`; log each in once with `post.py auth --account NAME` (pick that channel in Google's account picker), then `post.py whoami --account NAME` and paste the exact title into `expected_channel`. Instagram accounts read their login from `.env` variables you name (`IG_USER_MAIN`, `IG_PASS_MAIN`). Every queue item lists `accounts`; a video can go to several accounts, each tracked separately in the ledger. `post.py accounts` lists them. The worker must ASK which account(s) to use whenever it is not obvious.

## Instagram Trial Reels (discovery, on by default)
Every Instagram reel is uploaded as a **Trial Reel** (`clip_upload(trial=True)` in instagrapi: `trial_params={"graduation_strategy": "manual"}`, not shown in the main feed). Trial Reels are shown to people who do NOT follow you, so they are for discovery; you decide in Instagram whether to share one with your followers afterwards. Before the first upload the poster calls `clip_trial_eligible()`: if the account is not eligible (it needs a professional account with Trial Reels enabled) it HALTS and posts nothing, instead of silently publishing a normal reel. Opt out per account (`"trial": false` in `accounts.json`) or per queue item (`"trial": false`). Caveats: this uses Instagram's private API (not documented), Instagram may reject a trial reel at publish time (the run halts as AMBIGUOUS, check the app before retrying), and whether scheduling a trial reel is honoured is not guaranteed: check the first one in the app.

## Bulk scheduling (40 clips at once)
Fill `schedule.csv` (see `schedule.csv.example`; columns file, accounts (`a;b`), title, description, tags (`a;b`), when, thumbnail, ig_caption). Rows with an empty `when` are auto-slotted:
```
post.py import schedule.csv --start 2026-11-20 --times 07:30,19:30 --per-day 2
post.py plan            (check titles/dates; watch the videos)      post.py approve all
post.py run --account my-channel --max 40            # dry run
post.py run --account my-channel --max 40 --execute   # then the same for each account
```
Duplicate titles/files and unknown accounts are rejected before anything is sent. YouTube's per-channel upload limit stops the run cleanly; rerun later and finished items are skipped.

## Normal flow
```
post.py add "Exports/proj/short-1.mp4" --accounts my-channel --title "My first avatar failed" --description "..." --when "2026-11-20 19:30"
(owner watches the video)            post.py approve short-1
post.py plan                          post.py run --account my-channel --max 3          # dry run
post.py run --account my-channel --max 3 --execute                                       # real
```
- `when` is local time in `queue.json` `timezone_offset` (default +05:30). YouTube takes the upload as private with a `publishAt`, so the PC does not need to be on at publish time. Slots must be >= 15 min away (YouTube) / 25 min (Instagram).
- Re-running is safe: finished jobs are skipped, matching titles already on the channel are adopted, ambiguous failures halt and need a manual look (never blind retries).
- Other platforms (TikTok, Facebook, Shorts via app): `post.py pack <id>` copies the file and caption into `Exports/_manual/<id>/`.
- A daily scheduled resume can be set with Windows Task Scheduler running `post.py run --account my-channel --max 40 --execute`.

## Files (all git-ignored except post.py, README, queue example)
`.env`, `client_secrets.json`, `token*.json`, `ig_*.json`, `accounts.json`, `ledger/`, `queue.json`, `schedule.csv`.
