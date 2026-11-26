"""Word-accurate time of a phrase in the transcript (idea from the Devini Claude Video Clipper, MIT).

Usage: python find_phrase.py work/tr.json "the thing that separates" [--near 120]

A transcript line can hold several sentences. When a hook or payoff starts or ends INSIDE a line,
use the start of its first word and the end of its last word as a custom range:
    {"ranges": [[457.35, 474.95]]}
"""
import json, re, sys

args = [a for a in sys.argv[1:] if not a.startswith("--")]
near = float(sys.argv[sys.argv.index("--near") + 1]) if "--near" in sys.argv else None
if near is not None:
    args = [a for a in args if a != str(sys.argv[sys.argv.index("--near") + 1])]
tr = json.load(open(args[0], encoding="utf-8"))
phrase = args[1]
norm = lambda t: re.sub(r"[^\w$%']+", "", t.lower())
words = [(w["s"], w["e"], w["w"].strip()) for s in tr for w in s["words"]]
toks = [norm(w[2]) for w in words]
target = [norm(t) for t in phrase.split() if norm(t)]
hits = 0
for i in range(len(toks) - len(target) + 1):
    if toks[i:i + len(target)] == target:
        s, e = words[i][0], words[i + len(target) - 1][1]
        if near is not None and abs(s - near) > 60:
            continue
        ctx = " ".join(w[2] for w in words[max(0, i - 4):i + len(target) + 4])
        print(f"start {s:.2f}  end {e:.2f}   ...{ctx}...")
        hits += 1
if not hits:
    print("no exact match. Try fewer words (whisper may have spelled something differently).")
