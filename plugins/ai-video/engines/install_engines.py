"""Install or update the ai-video engines into ~/.claude/tools/video/ (not listed as skills = no token cost).

Copies the engine code shipped in this plugin over the installed copy. Never deletes anything there,
so each engine's own .venv, downloaded models, output/ and catalogs survive updates.
Re-run after every plugin update.

    python install_engines.py            install / update
"""
import shutil
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parent
DST = Path.home() / ".claude" / "tools" / "video"
ENGINES = ["clip-video", "shorts-from-main-video", "studio", "scripts"]
SKIP = shutil.ignore_patterns(".venv", "node_modules", "__pycache__", "output", ".git")


def main() -> int:
    DST.mkdir(parents=True, exist_ok=True)
    for name in ENGINES:
        src = SRC / name
        if not src.is_dir():
            print(f"missing in plugin: {name}")
            continue
        shutil.copytree(src, DST / name, ignore=SKIP, dirs_exist_ok=True)
        print(f"updated {DST / name}")
    shutil.copy2(SRC / "faceless.md", DST / "faceless.md") if (SRC / "faceless.md").exists() else None
    if not (DST / "clip-video" / ".venv").exists():
        print(f"NEXT: create clip-video's environment once:  cd \"{DST / 'clip-video'}\" && python install.py")
    print("Third-party animation / launch tools:  python \"%s\"" % (DST / "scripts" / "install_modules.py"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
