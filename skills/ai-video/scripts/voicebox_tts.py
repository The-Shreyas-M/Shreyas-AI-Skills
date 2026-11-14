"""Narration with your OWN cloned voice via the local, free Voicebox app (https://voicebox.sh).

Usage: python voicebox_tts.py script.json outdir [--profile "My Voice"] [--engine luxtts]
  script.json = {"clips": {"s1": "text", ...}}  ->  outdir/s1.wav ...
Needs the Voicebox server running locally (Windows: "C:/Program Files/Voicebox/voicebox-server.exe"
--host 127.0.0.1 --port 17493 --data-dir "%APPDATA%/sh.voicebox.app") and a voice profile you created from
YOUR OWN voice sample in the Voicebox app. Engines seen: qwen (best, slow on CPU), luxtts (fast, good), chatterbox.
Never clone another person's voice without their consent. Disclose synthetic voices when you publish.
"""
import json, os, sys, time, urllib.request

BASE = os.environ.get("VOICEBOX_URL", "http://127.0.0.1:17493")
args = [a for a in sys.argv[1:] if not a.startswith("--")]
opt = lambda k, d=None: sys.argv[sys.argv.index(k) + 1] if k in sys.argv else d
engine, wanted = opt("--engine", "luxtts"), opt("--profile")


def get(path):
    return json.loads(urllib.request.urlopen(BASE + path, timeout=30).read())


def post(path, data):
    req = urllib.request.Request(BASE + path, data=json.dumps(data).encode(), headers={"Content-Type": "application/json"})
    return json.loads(urllib.request.urlopen(req, timeout=3600).read())


profiles = get("/profiles")
if wanted:
    profiles = [p for p in profiles if p["name"].lower() == wanted.lower()]
cloned = [p for p in profiles if p.get("voice_type") == "cloned"]
if not cloned:
    sys.exit("no cloned voice profile found (create one from your own voice sample in the Voicebox app, or pass --profile NAME)")
prof = cloned[0]
print("voice profile:", prof["name"])
script = json.load(open(args[0], encoding="utf-8"))
os.makedirs(args[1], exist_ok=True)
for name, text in script["clips"].items():
    f = os.path.join(args[1], name + ".wav")
    if os.path.exists(f):
        continue
    t0 = time.time()
    gid = post("/generate", {"profile_id": prof["id"], "text": text, "language": "en", "normalize": True, "engine": engine})["id"]
    for _ in range(600):  # /generate blocks until done; /audio serves the wav
        try:
            b = urllib.request.urlopen(f"{BASE}/audio/{gid}", timeout=60).read()
            if len(b) > 2000:
                break
        except Exception:
            pass
        time.sleep(3)
    else:
        sys.exit(f"{name}: no audio")
    open(f, "wb").write(b)
    print(f"{name}: {time.time() - t0:.0f}s, {len(text.split())} words", flush=True)
