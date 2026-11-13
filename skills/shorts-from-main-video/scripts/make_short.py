"""Build a vertical 1080x1920 Short from a talking-head video + transcript.

Usage:  python make_short.py config.json
See ../references/config-example.json. Needs ffmpeg with libass (the imageio_ffmpeg build has it).

Look: b-roll (screen recording / image) on top, your face big underneath, word-by-word yellow
captions in the middle, a hook title, a yellow progress bar, 1.1x speed, optional music that
ducks under your voice, loudness -14 LUFS.
"""
import json, os, re, shutil, subprocess, sys
from ffmpeg_path import ffmpeg_exe

FF = ffmpeg_exe()
cfg_path = os.path.abspath(sys.argv[1])
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
FACE = C.get("face_crop")  # [x, y, w, h] in source pixels, or null = whole frame
WORK = os.path.join(base, "_work_" + os.path.splitext(os.path.basename(OUT))[0])
os.makedirs(WORK, exist_ok=True)
os.makedirs(os.path.dirname(OUT), exist_ok=True)

# ASS needs a font. Copy one next to the work dir and refer to it by a relative dir
# (absolute Windows paths with "C:" break ffmpeg's filter parser).
FONT_NAME = C.get("font", "Impact")
fd = os.path.join(WORK, "fonts")
os.makedirs(fd, exist_ok=True)
for cand in [C.get("font_file"), r"C:\Windows\Fonts\impact.ttf", "/usr/share/fonts/truetype/impact.ttf",
             "/System/Library/Fonts/Supplemental/Impact.ttf"]:
    if cand and os.path.exists(cand):
        shutil.copy(cand, fd)
        break
else:
    FONT_NAME = "Arial Black"  # system fallback when Impact is missing

words = [(w["s"], w["e"], w["w"].strip()) for s in TR for w in s["words"]]
for a, b in (C.get("fix_words") or {}).items():
    words = [(s, e, t.replace(a, b)) for s, e, t in words]
lines = [(s["start"], s["end"]) for s in TR]


def run(args, cwd=None):
    r = subprocess.run([FF, "-y", "-hide_banner", "-loglevel", "error"] + args, capture_output=True, text=True, cwd=cwd)
    if r.returncode:
        print("FFMPEG FAILED\n", " ".join(args)[:400], "\n", r.stderr[-1800:])
        sys.exit(1)


def merge(rs, gap=0.35):
    out = []
    for a, b in rs:
        if out and a - out[-1][1] < gap:
            out[-1] = (out[-1][0], max(out[-1][1], b))
        else:
            out.append((a, b))
    return out


def ranges(part):
    if "ranges" in part:
        return merge([tuple(r) for r in part["ranges"]])
    return merge([(max(0, lines[i][0] - 0.08), lines[i][1] + 0.14) for i in part["lines"]])


def ass_t(t):
    return f"{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}"


def captions(beats):
    ev = []
    for t0, rs in beats:
        off, ws = 0.0, []
        for a, b in rs:
            for s, e, t in words:
                if s >= a - 0.05 and e <= b + 0.2:
                    ws.append((t0 + off + (s - a), t0 + off + (e - a), t))
            off += b - a
        groups, cur = [], []
        for w in ws:
            cur.append(w)
            if len(cur) >= 3 or re.search(r"[.,!?]$", w[2]):
                groups.append(cur)
                cur = []
        if cur:
            groups.append(cur)
        for g in groups:
            for i, w in enumerate(g):
                end = max(g[i + 1][0] if i + 1 < len(g) else w[1] + 0.25, w[0] + 0.12)
                txt = " ".join((r"{\c&H00D4FF&\fscx114\fscy114}" + x[2].upper() + r"{\r}") if j == i else x[2].upper()
                               for j, x in enumerate(g))
                txt = re.sub(r"[.,!?]", "", txt)
                ev.append((w[0], end, r"{\an5\pos(540,830)}" + txt))
    ev.sort(key=lambda x: x[0])
    # never let two captions overlap (that produced garbled text)
    return [(s, min(e, ev[i + 1][0] - 0.01) if i + 1 < len(ev) else e, b) for i, (s, e, b) in enumerate(ev)]


def beat(i, part):
    rs = ranges(part)
    D = sum(b - a for a, b in rs)
    v = [f"[0:v]trim=start={a:.3f}:end={b:.3f},setpts=PTS-STARTPTS,fps=30[v{k}];"
         f"[0:a]atrim=start={a:.3f}:end={b:.3f},asetpts=PTS-STARTPTS[a{k}]" for k, (a, b) in enumerate(rs)]
    n = len(rs)
    fc = ";".join(v) + ";" + "".join(f"[v{k}][a{k}]" for k in range(n)) + f"concat=n={n}:v=1:a=1[fv][fa]"
    crop = f"crop={FACE[2]}:{FACE[3]}:{FACE[0]}:{FACE[1]}," if FACE else ""
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
        fc += (f";color=c=0x050506:s=1080x1920:r=30[cv];{top};"
               f"[fv]{crop}scale=1080:1000:force_original_aspect_ratio=increase,crop=1080:1000,setsar=1[face];"
               "[cv][top]overlay=x=0:y=110[c1];[c1][face]overlay=x=0:y=740[outv]")
    else:  # face only, full screen
        fc += f";[fv]{crop}scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1[outv]"
    out = os.path.join(WORK, f"b{i}.mp4")
    run(inp + ["-filter_complex", fc, "-map", "[outv]", "-map", "[fa]", "-t", f"{D:.3f}",
               "-c:v", "libx264", "-crf", "18", "-preset", "veryfast", "-pix_fmt", "yuv420p", "-r", "30",
               "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", out])
    return out, D, rs


parts = [beat(i, p) for i, p in enumerate(C["parts"])]
starts, t = [], 0.0
for _, D, _ in parts:
    starts.append(t)
    t += D
total = t
open(os.path.join(WORK, "list.txt"), "w").write("".join(f"file 'b{i}.mp4'\n" for i in range(len(parts))))
run(["-f", "concat", "-safe", "0", "-i", "list.txt", "-c", "copy", "raw.mp4"], cwd=WORK)

ev = captions([(starts[i], parts[i][2]) for i in range(len(parts))])
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
Style: Cap,{FONT_NAME},96,&H00FFFFFF,&H00FFFFFF,&H00000000,&H96000000,0,0,0,0,100,100,1,0,1,8,3,2,60,60,150,1
Style: Title,{FONT_NAME},100,&H0000D4FF,&H0000D4FF,&H00000000,&H96000000,0,0,0,0,100,100,1,0,1,8,3,8,60,60,40,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
open(os.path.join(WORK, "cap.ass"), "w", encoding="utf-8").write(HEAD + "\n".join(lines_ass) + "\n")

tot2 = total / SPEED
vf = (f"[0:v]setpts=PTS/{SPEED},ass=cap.ass:fontsdir=fonts,"
      f"drawbox=x=0:y=1900:w='iw*t/{tot2:.2f}':h=8:color=0xFFD400:t=fill[vout]")
voice = f"[0:a]atempo={SPEED},highpass=f=70,acompressor=threshold=-18dB:ratio=3:attack=5:release=80"
inp = ["-i", "raw.mp4"]
if MUSIC:
    inp += ["-i", MUSIC]
    af = (f"{voice}[v];[1:a]atrim=start={MUSIC_SS},asetpts=PTS-STARTPTS,volume={C.get('music_volume', 0.55)},"
          f"afade=t=in:st=0:d=0.6,afade=t=out:st={max(0, tot2 - 1.2):.2f}:d=1.2[m0];"
          "[v]asplit=2[vs][vk];[m0][vk]sidechaincompress=threshold=0.02:ratio=6:attack=20:release=350[md];"
          "[vs][md]amix=inputs=2:duration=first:normalize=0:weights=1 0.9,loudnorm=I=-14:TP=-1.5:LRA=11[aout]")
else:
    af = f"{voice},loudnorm=I=-14:TP=-1.5:LRA=11[aout]"
run(inp + ["-filter_complex", vf + ";" + af, "-map", "[vout]", "-map", "[aout]", "-t", f"{tot2:.2f}",
           "-c:v", "libx264", "-crf", "18", "-preset", "veryfast", "-pix_fmt", "yuv420p", "-r", "30",
           "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", "-movflags", "+faststart", OUT], cwd=WORK)
print(f"OK {OUT}  {tot2:.1f}s (work files in {WORK}; delete when happy)")
