"""Create (or refresh) the "AI Video Editor" workspace.

Usage: python setup_workspace.py [target_dir] [--no-venv]
Default target: ~/AI Video Editor (saved in ~/.claude/ai-video-editor.json so every skill can find it). Safe to re-run: existing files are NOT overwritten
(except nothing), folders are created, the posting venv is created if missing.
"""
import json, os, shutil, subprocess, sys, venv
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
SRC = SKILL / "assets" / "workspace"
args = [a for a in sys.argv[1:] if not a.startswith("--")]
ptr = Path.home() / ".claude" / "ai-video-editor.json"
target = Path(args[0]) if args else (Path(json.loads(ptr.read_text())["workspace"]) if ptr.exists() else Path.home() / "AI Video Editor")
target.mkdir(parents=True, exist_ok=True)
ptr.parent.mkdir(parents=True, exist_ok=True)
ptr.write_text(json.dumps({"workspace": str(target)}), encoding="utf-8")

for p in SRC.rglob("*"):
    rel = p.relative_to(SRC)
    dst = target / rel
    if p.is_dir():
        dst.mkdir(parents=True, exist_ok=True)
    elif not dst.exists():
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, dst)
        print("created", rel)
for d in ("Raw Footage", "References", "Exports", "work", "Tools", "posting/ledger"):
    (target / d).mkdir(parents=True, exist_ok=True)
q = target / "posting" / "queue.json"
if not q.exists():
    q.write_text(json.dumps({"expected_channel": "", "timezone_offset": "+05:30", "items": []}, indent=2), encoding="utf-8")

if "--no-venv" not in sys.argv:
    v = target / "Tools" / ".venv"
    py = v / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    if not py.exists():
        print("creating posting venv ...")
        venv.create(v, with_pip=True)
    subprocess.run([str(py), "-m", "pip", "install", "-q", "google-api-python-client", "google-auth-oauthlib", "python-dotenv"], check=False)
    print("posting packages ready (instagrapi is optional: Tools/.venv pip install instagrapi)")

skills = Path.home() / ".claude" / "skills"
for s in ("ai-video", "clip-video", "shorts-from-main-video", "youtube", "ai-video-studio"):
    print(("[ok]      " if (skills / s).exists() else "[MISSING] ") + f"skill {s}")
print(f"\nWorkspace ready: {target}\nNext: drop videos into 'Raw Footage', read START-HERE.md. For posting: posting/README.md")
