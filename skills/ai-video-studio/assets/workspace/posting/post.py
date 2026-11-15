"""Safe, idempotent poster/scheduler: YouTube (official API, Shorts + long) and Instagram Reels (optional).

Design rules (a previous runner posted the same reel 2-4 times, so these are not optional):
  1. One job = (platform, queue id, file content-hash). The SQLite ledger has a UNIQUE key on it.
  2. A job is CLAIMED in the ledger (atomic) BEFORE any network write. Only the claimer uploads.
  3. Before uploading we look at what is ALREADY on the platform and adopt a match instead of re-uploading.
  4. Any ambiguous failure marks the job AMBIGUOUS and HALTS the run. AMBIGUOUS jobs are never auto-retried.
  5. A lock file prevents two runs at once. Dry-run is the default; nothing is written without --execute.
  6. Only items with "approved": true are posted (set by `approve` after the owner watched the video).
  7. `expected_channel` in queue.json must equal the channel the YouTube token controls, else halt.

Commands (workspace python, run from anywhere):
  post.py accounts                          list named accounts (posting/accounts.json)
  post.py auth --account NAME               one-time YouTube login for that account (the OWNER does it)
  post.py whoami --account NAME             print the YouTube channel that account's token controls
  post.py add <video> --accounts a,b --title T --description D [--tags a,b] --when "2026-11-20 19:30"
  post.py import schedule.csv [--start 2026-11-20 --times 07:30,19:30 --per-day 2]   bulk add (40 clips etc.)
  post.py approve <id|all>                  mark as watched + confirmed by the owner
  post.py plan                              validate queue (no network)
  post.py run --account NAME [--max N] [--execute]
  post.py status                            ledger
  post.py pack <id>                         caption+file bundle for manual platforms (TikTok etc.)
"""
import argparse, hashlib, json, os, random, re, sqlite3, sys, time
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = Path(__file__).resolve().parent
WS = HERE.parent                                    # the "AI Video Editor" folder
QUEUE = HERE / "queue.json"
LEDGER = HERE / "ledger"
DB = LEDGER / "ledger.db"
try:
    from dotenv import load_dotenv
    load_dotenv(HERE / ".env")
except Exception:
    pass

YT_SCOPE = ["https://www.googleapis.com/auth/youtube"]
YT_MIN_LEAD = timedelta(minutes=15)
IG_MIN_LEAD = timedelta(minutes=25)
IG_PAUSE = (25, 45)
YT_PAUSE = (20, 40)


def tz():
    off = load_queue().get("timezone_offset", "+05:30")
    sign = -1 if off.startswith("-") else 1
    h, m = off.lstrip("+-").split(":")
    return timezone(sign * timedelta(hours=int(h), minutes=int(m)))


def load_queue():
    if not QUEUE.exists():
        return {"expected_channel": "", "timezone_offset": "+05:30", "items": []}
    return json.loads(QUEUE.read_text(encoding="utf-8-sig"))


def save_queue(q):
    QUEUE.write_text(json.dumps(q, indent=2, ensure_ascii=False), encoding="utf-8")


def accounts():
    """Named accounts from accounts.json. Without the file: one default account per platform (back-compat)."""
    f = HERE / "accounts.json"
    if f.exists():
        return json.loads(f.read_text(encoding="utf-8-sig"))["accounts"]
    return {"yt": {"platform": "yt", "token_file": os.getenv("YOUTUBE_TOKEN_FILE", "token.json"),
                   "expected_channel": load_queue().get("expected_channel", "")},
            "ig": {"platform": "ig", "username_env": "IG_USERNAME", "password_env": "IG_PASSWORD",
                   "session_file": os.getenv("IG_SESSION_FILE", "ig_session.json")}}


def acct(name):
    a = accounts().get(name)
    if not a:
        sys.exit(f"unknown account '{name}'. Known: {', '.join(accounts())}  (edit posting/accounts.json)")
    return a


def item_accounts(it):
    v = it.get("accounts") or it.get("platform") or []
    return v if isinstance(v, list) else [x.strip() for x in str(v).replace(";", ",").split(",") if x.strip()]


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for ch in iter(lambda: f.read(1 << 20), b""):
            h.update(ch)
    return h.hexdigest()[:16]


def vpath(it):
    p = Path(it["file"])
    return p if p.is_absolute() else WS / p


def when_dt(it):
    return datetime.strptime(it["when"], "%Y-%m-%d %H:%M").replace(tzinfo=tz())


def validate(q):
    errs, seen = [], set()
    for it in q["items"]:
        if it["id"] in seen:
            errs.append(f"duplicate id {it['id']}")
        seen.add(it["id"])
        if not vpath(it).exists():
            errs.append(f"{it['id']}: file missing {it['file']}")
        if len(it.get("title", "")) > 100 or not it.get("title"):
            errs.append(f"{it['id']}: title missing or >100 chars")
        if len(it.get("description", "")) > 4900:
            errs.append(f"{it['id']}: description >4900")
    hashes = {}
    for it in q["items"]:
        if vpath(it).exists():
            hashes.setdefault(sha(vpath(it)), []).append(it["id"])
    for h, ids in hashes.items():
        if len(ids) > 1:
            errs.append(f"same video content in {ids}")
    return errs


# ---------------------------------------------------------------- ledger
def db():
    LEDGER.mkdir(exist_ok=True)
    c = sqlite3.connect(DB, timeout=30, isolation_level=None)
    c.execute("PRAGMA journal_mode=WAL")
    c.execute("""CREATE TABLE IF NOT EXISTS jobs(platform TEXT NOT NULL, job_id TEXT NOT NULL, key TEXT NOT NULL,
        state TEXT NOT NULL, remote_id TEXT, attempts INTEGER NOT NULL DEFAULT 0, note TEXT, updated TEXT NOT NULL,
        PRIMARY KEY(platform, job_id))""")
    c.execute("CREATE UNIQUE INDEX IF NOT EXISTS uq_remote ON jobs(platform, remote_id) WHERE remote_id IS NOT NULL")
    return c


def now():
    return datetime.now(tz()).isoformat(timespec="seconds")


def jid(it):
    return f"{it['id']}:{sha(vpath(it))}"


def get(c, plat, job_id):
    r = c.execute("SELECT state,remote_id,attempts,note FROM jobs WHERE platform=? AND job_id=?", (plat, job_id)).fetchone()
    return dict(zip(("state", "remote_id", "attempts", "note"), r)) if r else None


def claim(c, plat, it):
    c.execute("BEGIN IMMEDIATE")
    try:
        r = get(c, plat, jid(it))
        if r is None:
            c.execute("INSERT INTO jobs VALUES(?,?,?,?,?,?,?,?)", (plat, jid(it), it["id"], "CLAIMED", None, 1, "", now()))
            ok = True
        elif r["state"] == "FAILED_SAFE" and r["attempts"] < 3:
            c.execute("UPDATE jobs SET state='CLAIMED',attempts=attempts+1,updated=? WHERE platform=? AND job_id=?", (now(), plat, jid(it)))
            ok = True
        else:
            ok = False
        c.execute("COMMIT")
        return ok
    except Exception:
        c.execute("ROLLBACK")
        raise


def setstate(c, plat, it, state, remote_id=None, note=None):
    c.execute("UPDATE jobs SET state=?,remote_id=COALESCE(?,remote_id),note=COALESCE(?,note),updated=? WHERE platform=? AND job_id=?",
              (state, remote_id, note, now(), plat, jid(it)))


class Lock:
    def __init__(self, name):
        self.p = LEDGER / f"run-{name}.lock"

    def __enter__(self):
        LEDGER.mkdir(exist_ok=True)
        if self.p.exists() and time.time() - self.p.stat().st_mtime < 6 * 3600:
            sys.exit(f"another run is active ({self.p}). If it crashed, delete the lock file.")
        self.p.write_text(str(os.getpid()))

    def __exit__(self, *a):
        self.p.unlink(missing_ok=True)


# ---------------------------------------------------------------- YouTube
def yt_files(a):
    tf = Path(a.get("token_file", "token.json"))
    cs = Path(os.getenv("YOUTUBE_CLIENT_SECRETS_FILE", "client_secrets.json"))
    return (tf if tf.is_absolute() else HERE / tf), (cs if cs.is_absolute() else HERE / cs)


def yt_service(a):
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    tf, _ = yt_files(a)
    if not tf.exists():
        sys.exit("no YouTube token for this account. Run `post.py auth --account NAME` (the owner logs in once).")
    creds = Credentials.from_authorized_user_file(str(tf), YT_SCOPE)
    if not creds.valid:
        creds.refresh(Request())
        tf.write_text(creds.to_json())
    return build("youtube", "v3", credentials=creds, cache_discovery=False)


def yt_channel(yt):
    r = yt.channels().list(part="snippet", mine=True).execute()["items"][0]
    return r["id"], r["snippet"]["title"]


def yt_uploads(yt):
    """{video_id: {title, privacy, publishAt}} for the whole channel (incl. private/scheduled)."""
    ch = yt.channels().list(part="contentDetails", mine=True).execute()["items"][0]
    pl = ch["contentDetails"]["relatedPlaylists"]["uploads"]
    out, tok = {}, None
    while True:
        r = yt.playlistItems().list(part="contentDetails", playlistId=pl, maxResults=50, pageToken=tok).execute()
        ids = [i["contentDetails"]["videoId"] for i in r["items"]]
        if ids:
            for v in yt.videos().list(part="snippet,status", id=",".join(ids)).execute()["items"]:
                out[v["id"]] = {"title": v["snippet"]["title"], "privacy": v["status"]["privacyStatus"],
                                "publishAt": v["status"].get("publishAt")}
        tok = r.get("nextPageToken")
        if not tok:
            return out


def http_reason(e):
    try:
        return json.loads(e.content.decode())["error"]["errors"][0]["reason"]
    except Exception:
        return "unknown"


def yt_run(items, c, maxn, execute, name):
    from googleapiclient.errors import HttpError
    from googleapiclient.http import MediaFileUpload
    a = acct(name)
    yt = yt_service(a)
    cid, title = yt_channel(yt)
    exp = a.get("expected_channel", "") or load_queue().get("expected_channel", "")
    print(f"account {name} -> YouTube channel: {title} ({cid})")
    if execute and (not exp or exp.strip().lower() != title.strip().lower()):
        sys.exit(f"HALT: expected_channel is '{exp}' but the token controls '{title}'. Fix queue.json or re-run `post.py auth`.")
    uploads = yt_uploads(yt)
    done = 0
    for it in items:
        st = get(c, name, jid(it))
        if st and st["state"] in ("DONE", "UPLOADED"):
            continue
        match = [v for v, d in uploads.items() if d["title"] == it["title"]]
        if st and st["state"] in ("AMBIGUOUS", "CLAIMED"):
            if len(match) == 1 and execute:
                setstate(c, name, it, "DONE", remote_id=match[0], note="adopted")
                print(f"[adopt] {it['id']}: {match[0]}")
            else:
                print(f"[BLOCKED] {it['id']}: state {st['state']}, {len(match)} matches; needs a manual look")
            continue
        if match:
            print(f"[adopt] {it['id']}: already on channel {match}")
            if execute and len(match) == 1 and not st:
                c.execute("INSERT INTO jobs VALUES(?,?,?,?,?,?,?,?)", (name, jid(it), it["id"], "DONE", match[0], 0, "adopted", now()))
            continue
        if done >= maxn:
            break
        when = when_dt(it)
        immediate = it.get("when", "") == "now"
        if when - datetime.now(tz()) < YT_MIN_LEAD:
            print(f"[SKIP] {it['id']}: slot {when:%d %b %H:%M} is past or less than 15 min away")
            continue
        publish = when.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        tags = [t.lstrip("#") for t in (it.get("tags") or re.findall(r"#\w+", it.get("description", "")))][:15]
        body = {"snippet": {"title": it["title"], "description": it.get("description", ""), "tags": tags,
                            "categoryId": it.get("category", "22"), "defaultLanguage": "en"},
                "status": {"privacyStatus": "private", "publishAt": publish, "selfDeclaredMadeForKids": False}}
        if it.get("synthetic"):  # YouTube altered/synthetic-content disclosure
            body["status"]["containsSyntheticMedia"] = True
        print(f"[{done + 1}] {name} {it['id']} | {it['title']} | publishes {when:%a %d %b %H:%M} ({publish})")
        if not execute:
            print("   (dry-run: no upload)")
            done += 1
            continue
        if not claim(c, name, it):
            print("   not claimable; skipping")
            continue
        try:
            req = yt.videos().insert(part="snippet,status", body=body,
                                     media_body=MediaFileUpload(str(vpath(it)), chunksize=8 << 20, resumable=True))
            resp = None
            while resp is None:
                _, resp = req.next_chunk(num_retries=3)
            vid = resp["id"]
        except HttpError as e:
            reason = http_reason(e)
            if reason in ("quotaExceeded", "uploadLimitExceeded", "dailyLimitExceeded", "rateLimitExceeded"):
                c.execute("DELETE FROM jobs WHERE platform=? AND job_id=? AND state='CLAIMED'", (name, jid(it)))
                print(f"   STOP: {reason}. Nothing created; claim released. Retry later.")
                return done
            setstate(c, name, it, "AMBIGUOUS", note=f"HttpError {reason}")
            mm = [v for v, d in yt_uploads(yt).items() if d["title"] == it["title"]]
            if len(mm) == 1:
                setstate(c, name, it, "DONE", remote_id=mm[0], note="recovered after error")
            print(f"   HALT: ambiguous error {reason}")
            return done
        except Exception as e:
            setstate(c, name, it, "AMBIGUOUS", note=type(e).__name__)
            print(f"   HALT: {type(e).__name__}: {e}")
            return done
        setstate(c, name, it, "DONE", remote_id=vid)
        print(f"   uploaded + scheduled: https://youtu.be/{vid}")
        if it.get("thumbnail"):
            try:
                yt.thumbnails().set(videoId=vid, media_body=MediaFileUpload(str(WS / it["thumbnail"]))).execute()
            except Exception as e:
                print(f"   thumbnail failed ({e}); set it in Studio")
        done += 1
        if done < maxn:
            time.sleep(random.uniform(*YT_PAUSE))
    return done


# ---------------------------------------------------------------- Instagram (optional, unofficial)
def ig_run(items, c, maxn, execute, name):
    a = acct(name)
    try:
        from instagrapi import Client
    except Exception:
        sys.exit("instagrapi not installed (optional): Tools/.venv/Scripts/pip install instagrapi")
    cl = Client()
    sess = Path(a.get("session_file", "ig_session.json"))
    sess = sess if sess.is_absolute() else HERE / sess
    if sess.exists():
        cl.load_settings(sess)
    cl.login(os.environ[a.get("username_env", "IG_USERNAME")], os.environ[a.get("password_env", "IG_PASSWORD")])
    cl.dump_settings(sess)
    import inspect
    trial_default = a.get("trial", True)  # Instagram TRIAL REELS: shown to non-followers first (discovery), not to your followers
    grad = a.get("trial_graduation", "manual")
    if "trial" not in inspect.signature(cl.clip_upload).parameters:
        sys.exit("HALT: your instagrapi has no Trial Reel support. Upgrade: Tools/.venv pip install -U 'instagrapi>=3.2'")
    eligible = None
    done = 0
    for it in items:
        st = get(c, name, jid(it))
        if st and st["state"] != "FAILED_SAFE":
            continue
        if done >= maxn:
            break
        when = when_dt(it)
        if when - datetime.now(tz()) < IG_MIN_LEAD:
            print(f"[SKIP] {it['id']}: Instagram needs >= 25 min lead")
            continue
        cap = it.get("ig_caption") or (it.get("title", "") + "\n\n" + it.get("description", ""))
        want_trial = it.get("trial", trial_default)
        print(f"[{done + 1}] {name} {it['id']} | schedule {when:%a %d %b %H:%M} | {'TRIAL reel (non-followers first)' if want_trial else 'normal reel (shown to followers)'}")
        if execute and want_trial and eligible is None:
            try:
                eligible = bool(cl.clip_trial_eligible())
            except Exception as e:
                eligible = False
                print(f"   could not confirm Trial Reel eligibility: {type(e).__name__}: {e}")
            if not eligible:
                sys.exit("HALT: this Instagram account is not eligible for Trial Reels (needs a professional account with the feature enabled). "
                         "Nothing was posted. Set \"trial\": false in accounts.json only if you really want normal reels.")
        if not execute:
            print("   (dry-run: no upload)")
            done += 1
            continue
        if not claim(c, name, it):
            continue
        try:
            extra = cl._scheduled_extra_data({}, when)
            media = cl.clip_upload(path=vpath(it), caption=cap, extra_data=extra, trial=bool(want_trial), trial_graduation_strategy=grad)
            setstate(c, name, it, "DONE", remote_id=str(media.pk), note=f"scheduled {when.isoformat()}{' trial' if want_trial else ''}")
            print(f"   scheduled OK, media {media.pk}")
        except Exception as e:
            setstate(c, name, it, "AMBIGUOUS", note=type(e).__name__)
            print(f"   HALT (ambiguous, check Instagram before retrying): {type(e).__name__}: {e}")
            return done
        done += 1
        if done < maxn:
            time.sleep(random.uniform(*IG_PAUSE))
    return done


# ---------------------------------------------------------------- CLI
def selected(q, name, only_ids=None):
    out = []
    for it in sorted(q["items"], key=lambda i: i["when"]):
        if name in item_accounts(it) and it.get("approved") is True and (not only_ids or it["id"] in only_ids):
            out.append(it)
    return out


def auto_slots(n, start, times, per_day):
    """n datetimes: from `start` (YYYY-MM-DD), `per_day` per day, at the given HH:MM times."""
    day = datetime.strptime(start, "%Y-%m-%d")
    slots, k = [], 0
    while len(slots) < n:
        for t in times[:per_day]:
            if len(slots) < n:
                slots.append(f"{day:%Y-%m-%d} {t}")
        day += timedelta(days=1)
    return slots


def kind(name):
    return acct(name)["platform"]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for n in ("auth", "whoami"):
        x = sub.add_parser(n)
        x.add_argument("--account", required=True)
    sub.add_parser("plan")
    sub.add_parser("status")
    sub.add_parser("accounts")
    a = sub.add_parser("add")
    a.add_argument("video")
    a.add_argument("--id")
    a.add_argument("--accounts", required=True, help="comma list of account names from accounts.json")
    a.add_argument("--title", required=True)
    a.add_argument("--description", default="")
    a.add_argument("--tags", default="")
    a.add_argument("--when", required=True, help='"YYYY-MM-DD HH:MM" in the queue timezone')
    a.add_argument("--thumb")
    a.add_argument("--synthetic", action="store_true", help="mark as AI-generated/synthetic (YouTube disclosure flag)")
    im = sub.add_parser("import", help="bulk-add from a CSV (see README)")
    im.add_argument("csv")
    im.add_argument("--start", help="auto-slot rows with empty 'when' from this date YYYY-MM-DD")
    im.add_argument("--times", default="19:30", help="comma HH:MM list used by auto-slot")
    im.add_argument("--per-day", type=int, default=1)
    ap_ = sub.add_parser("approve")
    ap_.add_argument("id")
    r = sub.add_parser("run")
    r.add_argument("--account", required=True)
    r.add_argument("--max", type=int, default=3)
    r.add_argument("--execute", action="store_true")
    r.add_argument("--only", default="")
    k = sub.add_parser("pack")
    k.add_argument("id")
    args = ap.parse_args()
    q = load_queue()
    slug = lambda p: re.sub(r"\W+", "-", p.stem).lower()
    rel = lambda p: os.path.relpath(p, WS).replace("\\", "/") if str(p).startswith(str(WS)) else str(p)

    if args.cmd == "accounts":
        for n, v in accounts().items():
            print(f"{n:20} {v['platform']:3} {v.get('expected_channel', v.get('username_env', ''))}")
    elif args.cmd == "auth":
        a_ = acct(args.account)
        if a_["platform"] != "yt":
            sys.exit("auth is for YouTube accounts; Instagram logs in with the .env credentials.")
        from google_auth_oauthlib.flow import InstalledAppFlow
        tf, cs = yt_files(a_)
        if not cs.exists():
            sys.exit(f"missing {cs}. Google Cloud Console -> YouTube Data API v3 -> OAuth client (Desktop) -> download JSON to that path.")
        flow = InstalledAppFlow.from_client_secrets_file(str(cs), YT_SCOPE)
        tf.write_text(flow.run_local_server(port=0).to_json())
        print("token saved:", tf, "-> now run `whoami --account", args.account + "` and set expected_channel in accounts.json")
    elif args.cmd == "whoami":
        a_ = acct(args.account)
        cid, title = yt_channel(yt_service(a_))
        print(f"account {args.account}: token controls channel '{title}' ({cid}); expected_channel: {a_.get('expected_channel') or '(not set)'}")
    elif args.cmd == "add":
        p = Path(args.video).resolve()
        it = {"id": args.id or slug(p), "file": rel(p), "accounts": [x.strip() for x in args.accounts.split(",")],
              "title": args.title, "description": args.description, "tags": [t for t in args.tags.split(",") if t],
              "when": args.when, "approved": False, "thumbnail": args.thumb, "synthetic": args.synthetic}
        for n in it["accounts"]:
            acct(n)
        q["items"] = [i for i in q["items"] if i["id"] != it["id"]] + [it]
        save_queue(q)
        print("queued (NOT approved yet):", it["id"])
    elif args.cmd == "import":
        import csv
        rows = list(csv.DictReader(open(args.csv, newline="", encoding="utf-8-sig")))
        empty = [r_ for r_ in rows if not (r_.get("when") or "").strip()]
        if empty and not args.start:
            sys.exit(f"{len(empty)} rows have no 'when'. Pass --start YYYY-MM-DD [--times 07:30,19:30 --per-day 2] to auto-slot them.")
        slots = iter(auto_slots(len(empty), args.start, args.times.split(","), args.per_day)) if empty else iter(())
        n = 0
        for r_ in rows:
            vp = Path(r_["file"])
            vp = vp if vp.is_absolute() else (WS / vp)
            accs = [x.strip() for x in re.split(r"[;,]", r_.get("accounts") or r_.get("account") or "") if x.strip()]
            for x in accs:
                acct(x)
            it = {"id": (r_.get("id") or slug(vp)), "file": rel(vp), "accounts": accs, "title": r_["title"].strip(),
                  "description": (r_.get("description") or "").replace("\\n", "\n"),
                  "tags": [t.strip() for t in (r_.get("tags") or "").split(";") if t.strip()],
                  "when": (r_.get("when") or "").strip() or next(slots), "approved": False,
                  "thumbnail": (r_.get("thumbnail") or None), "ig_caption": (r_.get("ig_caption") or None),
                  "synthetic": (r_.get("synthetic") or "").strip().lower() in ("1", "true", "yes")}
            q["items"] = [i for i in q["items"] if i["id"] != it["id"]] + [it]
            n += 1
        save_queue(q)
        print(f"imported {n} rows (NOT approved). Run `plan`, watch the videos, then `approve all`.")
    elif args.cmd == "approve":
        n = 0
        for it in q["items"]:
            if args.id in ("all", it["id"]):
                it["approved"] = True
                n += 1
        save_queue(q)
        print(f"approved {n}")
    elif args.cmd == "plan":
        errs = validate(q)
        for it in q["items"]:
            print(f"{it['id']:28} {it['when']}  {','.join(item_accounts(it)):22} approved={it.get('approved')}  {it['title'][:45]}")
            for n in item_accounts(it):
                if n not in accounts():
                    errs.append(f"{it['id']}: unknown account {n}")
        print("\nERRORS:\n  " + "\n  ".join(errs) if errs else f"\nqueue valid ({len(q['items'])} items)")
    elif args.cmd == "status":
        for row in db().execute("SELECT platform,key,state,remote_id,note,updated FROM jobs ORDER BY updated"):
            print(row)
    elif args.cmd == "run":
        errs = validate(q)
        if errs:
            sys.exit("queue invalid: " + "; ".join(errs))
        only = {x for x in args.only.split(",") if x}
        c = db()
        with Lock(args.account):
            fn = yt_run if kind(args.account) == "yt" else ig_run
            n = fn(selected(q, args.account, only), c, args.max, args.execute, args.account)
        print(f"{'executed' if args.execute else 'dry-run'}: {n} job(s)")
    elif args.cmd == "pack":
        it = next(i for i in q["items"] if i["id"] == args.id)
        out = WS / "Exports" / "_manual" / it["id"]
        out.mkdir(parents=True, exist_ok=True)
        import shutil
        shutil.copy(vpath(it), out / vpath(it).name)
        (out / "caption.txt").write_text(f"{it['title']}\n\n{it.get('description', '')}\n", encoding="utf-8")
        print("manual pack:", out)


if __name__ == "__main__":
    main()
