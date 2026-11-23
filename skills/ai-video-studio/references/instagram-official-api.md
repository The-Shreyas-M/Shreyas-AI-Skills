# Instagram official API: fast setup guide for posting reels

This replaces `instagrapi`. That library used Instagram's private app API, and Instagram locked accounts that posted with it (password reset and appeal needed). From now on, every Instagram post from these skills goes through Meta's official **Instagram Graph API**. Never install or call `instagrapi` again, not even to log in.

Time: about 30 minutes the first time and 5 minutes per extra account. The owner does every step that involves a login, a password or a token. Claude only reads variable *names*, never values.

## What you need first

- Each Instagram account must be a **Professional** account (Creator or Business). Switch it in the app: Settings → Account type and tools.
- One Meta developer login. A personal Facebook profile works, and no Facebook Page is needed. Nothing is posted to Facebook.
- One email for a **business portfolio**: a free, private container that Meta now requires before it shows the token button. Use a spare email, not your main one.

## Step 1: Create one app (once, for all accounts)

1. Go to developers.facebook.com → **My Apps → Create app**. Pick the use case **"Manage messaging & content on Instagram"**. Give the app a neutral name.
2. Open the left menu **Use cases** → that use case → **Customize**.
3. Open **API setup with Unified login**. It was called "Instagram login" before 2026. If it asks for a **Business portfolio**: click **+ Business portfolio → Create**, enter a neutral name, your name and the spare email, then **Create**. It costs nothing, needs no card and creates no Page. Reopen **API setup with Unified login**.
4. Open **Permissions and features** and click **Add** on `instagram_business_basic` and `instagram_business_content_publish`.
5. Open **App settings → Basic** and copy the **App ID** and **App secret** into the env file (step 3). Treat the secret like a password.

## Step 2: Get one token per Instagram account

Confirmed on the reference project: these clicks on the **Unified login** page (after the business portfolio existed) produced `EAA…` SYSTEM_USER tokens that never expire.

1. **API setup with Unified login → Generate access tokens → Add account.** Log in as the Instagram account, then allow both permissions.
2. Click **Generate token** next to it and copy the token straight into the env file. Never paste it into a chat.
3. Copy the account's **numeric Instagram user id**. If the page shows a different kind of id, use the read-only check in step 4. The right id is the one where `/<id>?fields=username` returns that account's handle.
4. Repeat for every account. One app holds many accounts.

**Which token you get decides the host.** The code needs to know:

| Token starts with | Host (`api_host`) | Expires? | Local file upload? |
|---|---|---|---|
| `EAA…` (Facebook Login for Business / business portfolio; often a SYSTEM_USER token) | `graph.facebook.com` | SYSTEM_USER tokens never expire (confirm with the debug check below) | yes for NORMAL reels only. **Tested 2026-11-22: a resumable (local) upload with `trial_params` was published as a normal reel, with no error.** Trial reels need `upload: "url"` (Instagram downloads the file), as in Meta's own trial example |
| `IG…` (plain Instagram Login) | `graph.instagram.com` | 60 days; refresh before then | **no**: Instagram downloads the video from a public URL (`upload: "url"` + `public_url_base`) |

On the reference project, the business-portfolio route produced `EAA…` SYSTEM_USER tokens that never expire. That is the easiest case.

## Step 3: Put the keys in an env file yourself (Notepad)

Use one variable pair per account, named in `accounts.json` (examples):

```
IG_API_USER_ID_MAIN=1784...
IG_API_TOKEN_MAIN=EAA...
META_APP_ID=...
META_APP_SECRET=...
```

The env file must be git-ignored: run `git check-ignore -q <file> && echo IGNORED`. A pattern such as `*.env` covers any name. Never commit it, print it, `cat` it or paste it.

## Step 4: Check the keys (read-only, prints no secrets)

```
post.py whoami --account main-ig
```

It prints which `@username` the token controls and the 24-hour publishing quota (100 posts per 24 h per account). Posting halts if the username does not equal `expected_username`.

To check token type and expiry without printing the token, ask Claude to call `GET /debug_token?input_token=<token>` with `access_token=<APP_ID>|<APP_SECRET>` and print only `type`, `is_valid`, `expires_at` and `scopes`. This is the one call that must carry secrets in the URL (Meta's design): run it from a script, never with `curl -v`, and never log the URL.

## Step 5: accounts.json entry

```json
"main-ig": {"platform": "ig", "user_id_env": "IG_API_USER_ID_MAIN", "token_env": "IG_API_TOKEN_MAIN",
            "expected_username": "your_handle", "api_host": "graph.facebook.com", "api_version": "v23.0",
            "trial": true, "trial_graduation": "MANUAL", "upload": "url", "public_url_base": "https://your-public-host/reels", "max_late_minutes": 360}
```

- `trial: true` (default) posts every reel as a **Trial Reel**, which is shown to non-followers first. `trial_graduation`: `MANUAL` means you share it to followers yourself. `SS_PERFORMANCE` means Instagram shares it automatically if it performs well.
- `upload: "url"` (needed for `IG…` tokens) also needs `public_url_base`, a public HTTPS folder where the same file name is reachable. Google Drive's direct download URL works (see the Worker section below), as does any static host. The URL must return `video/mp4`.
- Old entries with `username_env`/`password_env` (instagrapi) now halt with a pointer to this file.

## How posting works now (it differs from YouTube)

The API has **no scheduled-publish option**. A reel goes live when `post.py run --account <ig> --execute` runs. Each queue item's `when` is the earliest time it may go out:

- Items not yet due print `[WAIT]`.
- Items more than `max_late_minutes` past their slot print `[LATE]` and are skipped, so a late run never dumps a backlog. Give them a new `--when`.
- To post at each slot, run the command at or after each slot. The PC must be on for local runs. To post with the laptop off, use the free Cloudflare Worker below (recommended for anything longer than a few days).

## Always-on posting with a free Cloudflare Worker (laptop off)

Proven in a live project in 2026 (4 Instagram accounts, 1,900+ queued reels). Free plan, no card. The laptop renders and uploads once; after that the Worker posts everything.

**Pieces**
1. **Video hosting: Google Drive.** `rclone copy <renders> gdrive:<folder>/reels --include "*.mp4"`. Share the **folder** once as "anyone with the link"; every file inside inherits it (no per-file `rclone link`). Each file's URL is `https://drive.usercontent.google.com/download?id=<FILE_ID>&export=download&confirm=t`, which returns `video/mp4` with no login. Get the ids with `rclone lsjson gdrive:<folder>/reels`. Free Drive is 15 GB; about 2,000 short reels used under 5 GB. **Before a bulk upload, create your own Google OAuth client_id for rclone** (free, about 10 min): rclone's shared client is rate-limited project-wide (Drive 403 `RATE_LIMIT_EXCEEDED`), and we saw about 1 file per minute at worst. Upload in posting-date order, so a slow upload still covers the first days.
2. **Cloudflare account:** an API token with *Workers Scripts: Edit*, *Workers KV Storage: Edit* and *Account Settings: Read*, plus the account id, both in the git-ignored env file as `CLOUDFLARE_API_TOKEN` and `CLOUDFLARE_ACCOUNT_ID`. `wrangler` (npm) reads them from the environment, so there is no `wrangler login`. Pick a workers.dev subdomain once in the dashboard.
3. **KV namespace** (one, for example `wa_state`, binding `WA`). Keys:
   - `q:YYYY-MM-DD` (local posting date) → array of `{id, slot, handle, at (unix UTC seconds), video_id, caption}`.
   - `led:<slot>:<id>` → `{state: container | publishing | posted | ambiguous, container_id, media_id, permalink}`, written only by the Worker.
   - `halt:<slot>` → a reason; while present, that account is never touched.
4. **Worker** (plain JS module, cron `*/5 * * * *`, var `DRY_RUN` where only `"0"` means live). Secrets per account via `wrangler secret put TOKEN_<slot>` and `UID_<slot>`. Each run, for each due item (`at <= now`), at most **one action per account**:
   - no ledger entry → `GET /<uid>?fields=username` must equal the item's handle (a mismatch writes a halt; a network error just retries) → `POST /<uid>/media` with `media_type=REELS`, `video_url`, `caption`, `trial_params` → ledger `container`.
   - `container` → `GET /<container>?fields=status_code`; on `FINISHED` write `publishing` **first**, then `media_publish`, then `GET /<media>?fields=is_shared_to_feed,permalink` → ledger `posted`. If `is_shared_to_feed` is not `false`, write a halt (it went out as a normal reel). A publish error → `ambiguous` + halt, **never retried** (check the app by hand). `ERROR`/`EXPIRED` → delete the ledger entry so the next run makes a fresh container.
   - more than 2 h past its slot with no ledger entry → skipped (no backlog dumps).
   - a `/status` route returns today's items, their states and any halts (no secrets).
   Test it in Node with a fake KV and fake fetch before deploying; then do one live dry tick (`DRY_RUN="1"`) that only checks each username, and switch to `"0"` on the owner's yes.
5. **Filling the queue:** a laptop script turns the content plan plus the Drive ids into wrangler bulk format (`[{key, value}]`), then `wrangler kv bulk put queue.json --binding WA --remote`. Seed `led:` keys as `posted` for reels that are already live, so they are never posted twice.

**Rules that keep it safe**
- The Worker writes only `led:` and `halt:` keys, never `q:` keys. So adding reels later means rebuilding the queue and putting **only the `q:` days that changed**. Diff each day against `wrangler kv key get` first: only the new items may differ. Never re-put `led:` seeds over a live queue.
- Do not put a day's key within a few minutes of one of its posting slots.
- A KV read just after a put can show the old value for about 60 s (edge cache). Read again before you worry.
- Clear a halt by hand only after checking the app: `wrangler kv key delete halt:<slot> --binding WA --remote`.
- The first real post through the Worker is the proof: open `/status` after its slot and confirm the Trial label in the app.

The flow per reel: create container (`media_type=REELS`, caption, `trial_params`) → upload the bytes (local) or let Instagram fetch the URL → wait until `status_code` is `FINISHED` → `media_publish`.

Failures:
- A failure **before** publish is marked `FAILED_SAFE`. Nothing went public, so the next run retries it.
- A failure **during** publish is marked `AMBIGUOUS` and the run halts. Check the app before you retry.

## Gotchas we actually hit

- Meta renames dashboard pages often: "Instagram login" became "Unified login", and the token button appears only after a business portfolio exists. If a screen looks different, send a screenshot and follow the use case → Customize path.
- The id shown beside the token was not always the id the API wants. The username check settles it in one call.
- The business portfolio can be created with a different email from the developer login. That is fine.
- A token's host must match its type (see the table above). Using the wrong host returns "Invalid OAuth access token".
- Development-mode apps: the first real trial reel is the test. Confirm from another account that a non-follower can see it, and that the app labels it a trial.
- **Trial reels + local upload = NORMAL reel** (silently, 2026-11-22). `post.py` now refuses that combination. Use `upload: "url"` for trials, and test the first one on your least important account. Check right after publishing: `GET /<media_id>?fields=is_shared_to_feed` was `True` for the wrongly normal reels and `False` for real trial reels (url route, 2026-11-22). Stop if it is not `False`. Public video URL that worked: Google Drive via rclone, `rclone link` → `https://drive.usercontent.google.com/download?id=<id>&export=download&confirm=t` (serves `video/mp4`).

## Security

- Tokens and the app secret live only in a git-ignored env file. In a cloud runner they go in the platform's secret store (for example `wrangler secret put`), never in code, a URL, a log or a chat.
- `ig_graph.py` sends the token only in the `Authorization: OAuth …` header and removes it from every error message.
- If a token ever leaks, remove the account in the app dashboard (or reset the app secret) and generate a new one.
