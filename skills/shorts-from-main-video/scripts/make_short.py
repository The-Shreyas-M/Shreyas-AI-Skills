"""Build a vertical 1080x1920 Short from a talking-head video + transcript.   (v2)

Usage:
  python make_short.py config.json            render
  python make_short.py config.json --check    only check the cut boundaries (nothing rendered)

See ../references/config-example.json. Needs ffmpeg with libass (the imageio_ffmpeg build has it).
Optional: opencv-python (<5) for face_crop "auto" (YuNet face detector bundled in ../assets/models).

Look: b-roll (screen recording / image) on top, your face big underneath, word-by-word accent
captions in the middle, a hook title, a progress bar, 1.1x speed, optional music that ducks
under your voice, quiet whooshes on the cuts, loudness -14 LUFS, plus an .srt file.

v2 adds (ideas adopted from the Devini "Claude Video Clipper", MIT): boundary check, word-snapped
ranges, face auto-framing, per-part zoom (open/push/punch), subtle SFX, SRT export, token merging
("$500", "100%"), caption knobs, accent colour.
"""
import json, os, re, shutil, subprocess, sys
from ffmpeg_path import ffmpeg_exe

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)
FF = ffmpeg_exe()
args = [a for a in sys.argv[1:] if not a.startswith("--")]
CHECK_ONLY = "--check" in sys.argv
cfg_path = os.path.abspath(args[0])
C = json.load(open(cfg_path, encoding="utf-8"))
base = os.path.dirname(cfg_path)


def P(p):
    return p if (p is None or os.path.isabs(p)) else os.path.join(base, p)


SRC = P(C["source"])
TR = json.load(open(P(C["transcript"]), encoding="utf-8"))
OUT = P(C["out"])
SPEED = C.get("speed", 1.1)
MUSIC = P(C.get("music"))
MUSIC_SS = C.get("music_start", 0)
ACCENT = C.get("accent", "#FFD400")
CAP_Y = C.get("caption_y", 830)          # centre line of captions (px of 1920)
CAP_SIZE = C.get("caption_size", 96)
UPPER = C.get("uppercase", True)
SFX = C.get("sfx", "light")              # light | none
WORK = os.path.join(base, "_work_" + os.path.splitext(os.path.basename(OUT))[0])
os.makedirs(WORK, exist_ok=True)
os.makedirs(os.path.dirname(OUT), exist_ok=True)


def abgr(hexrgb):  # "#RRGGBB" -> ASS "&H00BBGGRR&"
    h = hexrgb.lstrip("#")
    return f"&H00{h[4:6]}{h[2:4]}{h[0:2]}&".upper()


# ASS needs a font. Copy one next to the work dir and refer to it by a relative dir
# (absolute Windows paths with "C:" break ffmpeg's filter parser).
FONT_NAME = C.get("font", "Impact")
fd = os.path.join(WORK, "fonts")
os.makedirs(fd, exist_ok=True)
for cand in [C.get("font_file"), r"C:\Windows\Fonts\impact.ttf", "/usr/share/fonts/truetype/impact.ttf",
             "/System/Library/Fonts/Supplemental/Impact.ttf", os.path.join(SKILL, "assets", "fonts", "Montserrat-ExtraBold.ttf")]:
    if cand and os.path.exists(cand):
        shutil.copy(cand, fd)
        if cand.endswith("Montserrat-ExtraBold.ttf") and "font" not in C:
            FONT_NAME = "Montserrat ExtraBold"
        break
else:
    FONT_NAME = "Arial Black"


def merge_tokens(ws):
    """Whisper splits "$500" ",000" / "100" "%" / "e" "-commerce" into separate tokens: glue them."""
    out = []
    for s, e, t in ws:
        if out and t and (t[0] in ",%-&" or t.startswith(".0") or out[-1][2].endswith("-")) and s - out[-1][1] < 0.3:
            out[-1] = (out[-1][0], e, (out[-1][2] + t).replace(" ", ""))
        else:
            out.append((s, e, t))
    return out


words = [(w["s"], w["e"], w["w"].strip()) for s in TR for w in s["words"]]
for a, b in (C.get("fix_words") or {}).items():
    words = [(s, e, t.replace(a, b)) for s, e, t in words]
words = merge_tokens(words)
lines = [(s["start"], s["end"]) for s in TR]
sentence_starts = [s for s, _ in lines]
sentence_ends = [e for _, e in lines]


def run(args_, cwd=None):
    r = subprocess.run([FF, "-y", "-hide_banner", "-loglevel", "error"] + args_, capture_output=True, text=True, cwd=cwd)
    if r.returncode:
        print("FFMPEG FAILED\n", " ".join(args_)[:400], "\n", r.stderr[-1800:])
        sys.exit(1)


def merge(rs, gap=0.35):
    out = []
    for a, b in rs:
        if out and a - out[-1][1] < gap:
            out[-1] = (out[-1][0], max(out[-1][1], b))
        else:
            out.append((a, b))
    return out


def snap(a, b):
    """Snap a custom range to whole words (start of the first word >= a-0.15, end of the last word <= b+0.15)."""
    ws = [w for w in words if w[1] > a - 0.15 and w[0] < b + 0.15]
    if not ws:
        return a, b
    return max(0.0, ws[0][0] - 0.08), ws[-1][1] + 0.14


def ranges(part):
    if "ranges" in part:
        return merge([snap(*r) for r in part["ranges"]])
    return merge([(max(0.0, lines[i][0] - 0.08), lines[i][1] + 0.14) for i in part["lines"]])


# ---------- boundary check ----------
def check(parts_cfg):
    ok = True
    total = 0.0
    for i, p in enumerate(parts_cfg):
        rs = ranges(p)
        d = sum(b - a for a, b in rs)
        total += d
        for a, b in rs:
            if min(abs(a + 0.08 - s) for s in sentence_starts) > 0.6:
                near = [w[2] for w in words if abs(w[0] - (a + 0.08)) < 0.5][:4]
                print(f"[warn] part {i}: starts mid-sentence near '{' '.join(near)}' ({a:.1f}s). Use a line id or `find_phrase.py`.")
                ok = False
            if min(abs(b - 0.14 - e) for e in sentence_ends) > 0.6:
                near = [w[2] for w in words if abs(w[1] - (b - 0.14)) < 0.5][-4:]
                print(f"[warn] part {i}: ends mid-sentence near '{' '.join(near)}' ({b:.1f}s). End on a full sentence/payoff.")
                ok = False
        print(f"part {i}: {d:.1f}s  ranges {[(round(a, 1), round(b, 1)) for a, b in rs]}")
    out_len = total / SPEED
    print(f"total {out_len:.1f}s at {SPEED}x" + ("" if 15 <= out_len <= 60 else "  [warn] outside 15-60 s"))
    if not (15 <= out_len <= 60):
        ok = False
    print("CHECK OK" if ok else "CHECK: review the warnings above")


if CHECK_ONLY:
    check(C["parts"])
    sys.exit(0)


# ---------- face auto-framing (YuNet via OpenCV, optional) ----------
def detect_face(rs):
    try:
        import cv2, numpy as np
    except Exception:
        print("[warn] face_crop 'auto' needs opencv-python<5 (pip install 'opencv-python<5'); using whole frame")
        return None
    model = os.path.join(SKILL, "assets", "models", "face_detection_yunet_2023mar.onnx")
    cap = cv2.VideoCapture(SRC)
    det = cv2.FaceDetectorYN.create(model, "", (640, 360), 0.6, 0.3, 5000)
    pts, W0, H0 = [], 0, 0
    total = sum(b - a for a, b in rs)
    for k in range(10):
        t = (k + 0.5) / 10 * total
        for a, b in rs:
            if t <= b - a:
                t += a
                break
            t -= b - a
        cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000)
        ok, fr = cap.read()
        if not ok:
            continue
        H0, W0 = fr.shape[:2]
        sc = 640 / W0
        small = cv2.resize(fr, (640, int(H0 * sc)))
        det.setInputSize((small.shape[1], small.shape[0]))
        _, faces = det.detect(small)
        if faces is not None and len(faces):
            x, y, w, h = max(faces, key=lambda f: f[2] * f[3])[:4]
            pts.append(((x + w / 2) / sc, (y + h / 2) / sc, h / sc))
    cap.release()
    if len(pts) < 3:
        print("[warn] no stable face found; using whole frame")
        return None
    cx, cy, fh = (float(v) for v in np.median(np.array(pts), axis=0))
    return cx, cy, fh, W0, H0


_face_cache = {}


def crop_for(aspect, rs):
    """crop filter fragment for the face panel of the given aspect (w/h), or ''."""
    fc = C.get("face_crop")
    if isinstance(fc, list):
        return f"crop={fc[2]}:{fc[3]}:{fc[0]}:{fc[1]}," if aspect == 1080 / 1000 else ""
    if fc != "auto":
        return ""
    if "face" not in _face_cache:
        _face_cache["face"] = detect_face(ranges_all)
    f = _face_cache["face"]
    if not f:
        return ""
    cx, cy, fh, W0, H0 = f
    ch = min(H0, fh * C.get("face_headroom", 3.9))
    cw = ch * aspect
    if cw > W0:
        cw, ch = W0, W0 / aspect
    x = min(max(cx - cw / 2, 0), W0 - cw)
    y = min(max(cy - ch * 0.42, 0), H0 - ch)
    ev = lambda v: int(v) // 2 * 2
    return f"crop={ev(cw)}:{ev(ch)}:{ev(x)}:{ev(y)},"


ranges_all = merge([r for p in C["parts"] for r in ranges(p)])


def zoom_expr(mode, D):
    """scale factor over the clip time t for the face panel."""
    if mode == "open":
        return "1+0.18*max(0,1-t/0.30)+0.03*t/%.2f" % D
    if mode == "push":
        return "1+0.05*t/%.2f" % D
    if mode == "punch":
        return "1.14+0.03*t/%.2f" % D
    return "1"


def beat(i, part):
    rs = ranges(part)
    D = sum(b - a for a, b in rs)
    v = [f"[0:v]trim=start={a:.3f}:end={b:.3f},setpts=PTS-STARTPTS,fps=30[v{k}];"
         f"[0:a]atrim=start={a:.3f}:end={b:.3f},asetpts=PTS-STARTPTS[a{k}]" for k, (a, b) in enumerate(rs)]
    n = len(rs)
    fc = ";".join(v) + ";" + "".join(f"[v{k}][a{k}]" for k in range(n)) + f"concat=n={n}:v=1:a=1[fv][fa]"
    zmode = part.get("zoom", "open" if i == 0 else ("punch" if i % 2 == 0 else "push"))
    z = zoom_expr(zmode, D)
    zoom = "" if z == "1" else (f"scale=w='trunc(PW*({z})/2)*2':h=-2:eval=frame,crop=PW:PH:'(iw-PW)/2':'(ih-PH)/2',")
    inp = ["-i", SRC]
    br = part.get("broll")
    if br:
        br = P(br)
        if br.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
            inp += ["-loop", "1", "-t", f"{D:.2f}", "-framerate", "30", "-i", br]
            top = ("[1:v]scale=2160:-2,zoompan=z='1+0.0007*on':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
                   ":d=1:s=1080x608:fps=30,setsar=1[top]")
        else:
            inp += ["-stream_loop", "-1", "-ss", f"{part.get('broll_start', 0):.2f}", "-t", f"{D:.2f}", "-i", br]
            top = "[1:v]scale=1080:608:force_original_aspect_ratio=increase,crop=1080:608,setsar=1[top]"
        crop = crop_for(1080 / 1000, rs)
        fz = zoom.replace("PW", "1080").replace("PH", "1000")
        fc += (f";color=c=0x050506:s=1080x1920:r=30[cv];{top};"
               f"[fv]{crop}scale=1080:1000:force_original_aspect_ratio=increase,crop=1080:1000,setsar=1,{fz}setsar=1[face];"
               "[cv][top]overlay=x=0:y=110[c1];[c1][face]overlay=x=0:y=740[outv]")
    else:  # face only, full screen
        crop = crop_for(1080 / 1920, rs)
        fz = zoom.replace("PW", "1080").replace("PH", "1920")
        fc += f";[fv]{crop}scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,{fz}setsar=1[outv]"
    out = os.path.join(WORK, f"b{i}.mp4")
    run(inp + ["-filter_complex", fc, "-map", "[outv]", "-map", "[fa]", "-t", f"{D:.3f}",
               "-c:v", "libx264", "-crf", "18", "-preset", "veryfast", "-pix_fmt", "yuv420p", "-r", "30",
               "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", out])
    return out, D, rs


def caption_groups(beats):
    """[(start, end, [(s,e,text)...])] on the pre-speed timeline."""
    groups_out = []
    for t0, rs in beats:
        off, ws = 0.0, []
        for a, b in rs:
            for s, e, t in words:
                if s >= a - 0.05 and e <= b + 0.2:
                    ws.append((t0 + off + (s - a), t0 + off + (e - a), t))
            off += b - a
        cur = []
        groups = []
        for w in ws:
            txt = re.sub(r"[.,;:?!\"]", "", w[2])
            if not txt:
                continue
            if cur and (len(cur) >= 3 or sum(len(c[2]) + 1 for c in cur) + len(txt) > 17 or w[0] - cur[-1][1] > 0.35):
                groups.append(cur)
                cur = []
            cur.append((w[0], w[1], txt))
            if re.search(r"[.?!]$", w[2]):
                groups.append(cur)
                cur = []
        if cur:
            groups.append(cur)
        groups_out += groups
    return groups_out


def captions(groups):
    ev = []
    for g in groups:
        for i, w in enumerate(g):
            end = max(g[i + 1][0] if i + 1 < len(g) else w[1] + 0.25, w[0] + 0.12)
            txt = " ".join(((r"{\c%s\fscx114\fscy114}" % abgr(ACCENT)) + (x[2].upper() if UPPER else x[2]) + r"{\r}") if j == i
                           else (x[2].upper() if UPPER else x[2]) for j, x in enumerate(g))
            ev.append((w[0], end, r"{\an5\pos(540,%d)}" % CAP_Y + txt))
    ev.sort(key=lambda x: x[0])
    # never let two captions overlap (that produced garbled text)
    return [(s, min(e, ev[i + 1][0] - 0.01) if i + 1 < len(ev) else e, b) for i, (s, e, b) in enumerate(ev)]


def ass_t(t):
    return f"{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}"


def srt_t(t):
    ms = int(round(t * 1000))
    return f"{ms // 3600000:02d}:{ms % 3600000 // 60000:02d}:{ms % 60000 // 1000:02d},{ms % 1000:03d}"


parts = [beat(i, p) for i, p in enumerate(C["parts"])]
starts, t = [], 0.0
for _, D, _ in parts:
    starts.append(t)
    t += D
total = t
open(os.path.join(WORK, "list.txt"), "w").write("".join(f"file 'b{i}.mp4'\n" for i in range(len(parts))))
run(["-f", "concat", "-safe", "0", "-i", "list.txt", "-c", "copy", "raw.mp4"], cwd=WORK)

groups = caption_groups([(starts[i], parts[i][2]) for i in range(len(parts))])
ev = captions(groups)
tit = []
for ti in C.get("titles", []):
    s0 = starts[ti.get("part", 0)] + ti.get("t0", 0.1)
    s1 = starts[ti.get("part", 0)] + ti.get("t1", 2.8)
    tit.append((s0, s1, ti["text"].replace("|", r"\N")))
sc = lambda x: x / SPEED
lines_ass = [f"Dialogue: 1,{ass_t(sc(s))},{ass_t(sc(e))},Cap,,0,0,0,,{b}" for s, e, b in ev if e - s > 0.05]
lines_ass += [f"Dialogue: 2,{ass_t(sc(s))},{ass_t(sc(e))},Title,,0,0,0,,{{\\an8\\pos(540,70)\\fad(150,150)"
              f"\\fscx60\\fscy60\\t(0,200,\\fscx108\\fscy108)\\t(200,330,\\fscx100\\fscy100)}}{tx}" for s, e, tx in tit]
HEAD = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,{FONT_NAME},{CAP_SIZE},&H00FFFFFF,&H00FFFFFF,&H00000000,&H96000000,0,0,0,0,100,100,1,0,1,8,3,2,60,60,150,1
Style: Title,{FONT_NAME},100,{abgr(ACCENT)},{abgr(ACCENT)},&H00000000,&H96000000,0,0,0,0,100,100,1,0,1,8,3,8,60,60,40,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
open(os.path.join(WORK, "cap.ass"), "w", encoding="utf-8").write(HEAD + "\n".join(lines_ass) + "\n")
with open(os.path.splitext(OUT)[0] + ".srt", "w", encoding="utf-8") as f:
    for i, g in enumerate(groups, 1):
        f.write(f"{i}\n{srt_t(sc(g[0][0]))} --> {srt_t(sc(g[-1][1] + 0.2))}\n{' '.join(x[2] for x in g)}\n\n")

# ---------- SFX (quiet whooshes on the opening and on each cut) ----------
sfx_inputs, sfx_chain, sfx_labels = [], [], []
tot2 = total / SPEED
if SFX != "none":
    cues = [(0.0, "whoosh-soft.wav", -16)] + [(sc(s), "whoosh-short.wav", -21) for s in starts[1:]]
    for k, (at, fn, gain) in enumerate(cues):
        sfx_inputs.append(os.path.join(SKILL, "assets", "sfx", fn))
        ms = int(max(0, at - 0.05) * 1000)
        sfx_chain.append((fn, gain, ms))

vf = (f"[0:v]setpts=PTS/{SPEED},ass=cap.ass:fontsdir=fonts,"
      f"drawbox=x=0:y=1900:w='iw*t/{tot2:.2f}':h=8:color=0xFFD400:t=fill[vout]")
voice = f"[0:a]atempo={SPEED},highpass=f=70,acompressor=threshold=-18dB:ratio=3:attack=5:release=80"
inp = ["-i", "raw.mp4"]
idx = 1
labels = []
af = ""
if MUSIC:
    inp += ["-i", MUSIC]
    af += (f"{voice}[vv];[{idx}:a]atrim=start={MUSIC_SS},asetpts=PTS-STARTPTS,volume={C.get('music_volume', 0.55)},"
           f"afade=t=in:st=0:d=0.6,afade=t=out:st={max(0, tot2 - 1.2):.2f}:d=1.2[m0];"
           "[vv]asplit=2[vs][vk];[m0][vk]sidechaincompress=threshold=0.02:ratio=6:attack=20:release=350[md];")
    labels = ["[vs]", "[md]"]
    idx += 1
else:
    af += f"{voice}[vs];"
    labels = ["[vs]"]
for k, ((fn, gain, ms), path) in enumerate(zip(sfx_chain, sfx_inputs)):
    inp += ["-i", path]
    af += f"[{idx}:a]aresample=48000,aformat=channel_layouts=stereo,volume={gain}dB,adelay={ms}|{ms}[sx{k}];"
    labels.append(f"[sx{k}]")
    idx += 1
weights = " ".join(["1", "0.9"][:2] if MUSIC else ["1"]) + "".join(" 1" for _ in sfx_chain)
af += "".join(labels) + f"amix=inputs={len(labels)}:duration=first:normalize=0:weights={weights},loudnorm=I=-14:TP=-1.5:LRA=11[aout]"
run(inp + ["-filter_complex", vf + ";" + af, "-map", "[vout]", "-map", "[aout]", "-t", f"{tot2:.2f}",
           "-c:v", "libx264", "-crf", "18", "-preset", "veryfast", "-pix_fmt", "yuv420p", "-r", "30",
           "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", "-movflags", "+faststart", OUT], cwd=WORK)
print(f"OK {OUT}  {tot2:.1f}s  (+ .srt)  (work files in {WORK}; delete when happy)")
