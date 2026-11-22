# Posting and scheduling

`post.py` posts or schedules approved videos. Dry-run is the default.

## One-time setup (the owner does this; Claude never types passwords)
1. Python env: `Tools/.venv` is created by `setup_workspace.py`. Packages: google-api-python-client, google-auth-oauthlib, python-dotenv. Instagram needs no extra package (stdlib `ig_graph.py`).
2. YouTube login:
   - Google Cloud Console -> new project -> enable **YouTube Data API v3** -> OAuth consent screen (External, add yourself as test user) -> Credentials -> **OAuth client ID, Desktop app** -> download the JSON.
   - Save it as `posting/client_secrets.json` (git-ignored). Copy `.env.example` to `.env` if you want other paths.
   - Run `Tools\.venv\Scripts\python.exe posting\post.py auth --account my-channel` and log in with the **channel you want to post to**. Choose the right brand-channel in the Google account picker.
   - Run `post.py whoami --account my-channel`, then set `expected_channel` in `accounts.json` to that exact channel title. Posting halts if they ever differ.
   - YouTube API note: videos uploaded through an unverified API project may be forced private. If so, request an audit or upload through Studio. Per-channel upload limits apply (about 100 a day was observed); the run stops cleanly when hit.
3. Instagram (official Graph API): follow `~/.claude/skills/ai-video-studio/references/instagram-official-api.md` (one Meta app, a token + numeric user id per account in `.env`, set by the owner). Then `post.py whoami --account main-ig` must print the right @username. instagrapi is removed for good (it got accounts locked).

## Accounts (several channels / Instagram accounts)
Copy `accounts.json.example` to `accounts.json` and name each account (`my-channel`, `second-yt`, `main-ig`...). Each YouTube account has its own `token_file` and `expected_channel`; log each in once with `post.py auth --account NAME` (pick that channel in Google's account picker), then `post.py whoami --account NAME` and paste the exact title into `expected_channel`. Instagram accounts read their user id and token from `.env` variables you name (`IG_API_USER_ID_MAIN`, `IG_API_TOKEN_MAIN`) and must set `expected_username`. Every queue item lists `accounts`; a video can go to several accounts, each tracked separately in the ledger. `post.py accounts` lists them. The worker must ASK which account(s) to use whenever it is not obvious.

## Related video (Shorts clipped from a main video)
When a Short is clipped from a main video, link them: queue it with `--related <main video's queue id | youtu.be URL | video id>` (CSV column `related`; a queue id is resolved from the ledger once the main video is uploaded, so the main video must go up first: a Short whose target is not uploaded yet is skipped with `[WAIT]`).
What happens:
1. The poster appends `Full video: https://youtu.be/<id>` to the Short's description (the part the API allows).
2. YouTube's own **Related video** field (Studio -> Details -> Related video) can only be set in YouTube Studio: the public Data API does not expose it. `post.py related` prints a ready checklist (Studio edit link + the main video link for each uploaded Short) and saves it to `Exports/_related-todo.md`. It takes about 10 seconds per Short.
3. Optional shortcut: with the owner's explicit OK, a Claude session driving the owner's logged-in browser (Claude in Chrome or the built-in browser) can open each Studio link from the checklist and set the field. Use the browser only for this edit, never to upload, and confirm the channel and the video before saving.
The destination must be a public or unlisted video on the SAME channel.

## Instagram (official API): publish when due, Trial Reels by default
- The Instagram API has **no scheduled publish**. `post.py run --account <ig> --execute` publishes queue items whose `when` has arrived; earlier items print `[WAIT]`, items more than `max_late_minutes` (default 360) late print `[LATE]` and are skipped (give them a new `--when`). Run it at/after each slot (Task Scheduler only if the owner asks, or a cloud cron).
- Flow per reel: container (`media_type=REELS`, caption, `trial_params`) -> upload (`upload: "local"`, resumable, needs an `EAA...` Facebook-Login token on graph.facebook.com) or Instagram fetches `public_url_base/<file name>` (`upload: "url"`, needed for `IG...` tokens on graph.instagram.com) -> wait for `FINISHED` -> `media_publish`.
- Every reel is a **Trial Reel** (shown to non-followers first): `trial_graduation` `MANUAL` (you share it to followers) or `SS_PERFORMANCE` (Instagram shares it if it performs well). Opt out per account or item with `"trial": false`.
- Before the first upload of a run the token's @username must equal `expected_username`, else HALT, nothing posted.
- Failure before publish = `FAILED_SAFE` (nothing public, retried next run). Failure during publish = `AMBIGUOUS` + HALT: check the app first, never blind-retry.
- The first real trial reel on a new account is a checkpoint: confirm in the app that it is marked trial and visible to non-followers.
- Test the client without network: `python posting/test_ig_graph.py` -> `IG GRAPH OK`.

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
- `when` is local time in `queue.json` `timezone_offset` (default +05:30). YouTube takes the upload as private with a `publishAt`, so the PC does not need to be on at publish time. YouTube slots must be >= 15 min away; Instagram publishes when the run happens (see above).
- Re-running is safe: finished jobs are skipped, matching titles already on the channel are adopted, ambiguous failures halt and need a manual look (never blind retries).
- Other platforms (TikTok, Facebook, Shorts via app): `post.py pack <id>` copies the file and caption into `Exports/_manual/<id>/`.
- A daily scheduled resume can be set with Windows Task Scheduler running `post.py run --account my-channel --max 40 --execute`.

## Files (all git-ignored except post.py, README, queue example)
`.env`, `client_secrets.json`, `token*.json`, `accounts.json`, `ledger/`, `queue.json`, `schedule.csv`.
