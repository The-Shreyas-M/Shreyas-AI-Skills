"""Install or update the third-party video modules into ~/.claude/tools (not listed as skills = no token cost).

Usage: python install_modules.py [--voice]
 - claude-animation-skills (MIT, artemnovitckii): cloned + kit/setup.sh (npm, Playwright Chromium, GSAP, HyperFrames)
 - brag-slim (MIT, latent-spaces): sparse clone of skills/brag-slim only
Windows: creates a python3 shim so the macOS/Linux setup script runs under Git Bash. Needs git, Node 22+, ffmpeg, bash.
"""
import os, shutil, subprocess, sys
from pathlib import Path

T = Path.home() / ".claude" / "tools"
T.mkdir(parents=True, exist_ok=True)


def run(cmd, cwd=None, env=None):
    print("+", " ".join(cmd))
    return subprocess.run(cmd, cwd=cwd, env=env).returncode


def clone(url, name, sparse=None):
    d = T / name
    if d.exists():
        run(["git", "pull", "--ff-only"], cwd=d)
        return d
    if sparse:
        run(["git", "clone", "--depth", "1", "--filter=blob:none", "--sparse", url, str(d)])
        run(["git", "sparse-checkout", "set", *sparse], cwd=d)
    else:
        run(["git", "clone", "--depth", "1", url, str(d)])
    return d


for tool in ("git", "node", "ffmpeg", "bash"):
    if not shutil.which(tool):
        sys.exit(f"missing {tool}: install it first (Windows: winget install Git.Git OpenJS.NodeJS.LTS Gyan.FFmpeg).")

anim = clone("https://github.com/artemnovitckii/claude-animation-skills.git", "claude-animation-skills")
clone("https://github.com/latent-spaces/brag.git", "brag", sparse=["skills/brag-slim"])

env = dict(os.environ)
if os.name == "nt":
    shim = T / "shims"
    shim.mkdir(exist_ok=True)
    (shim / "python3").write_text(f'#!/usr/bin/env bash\nexec "{sys.executable.replace(chr(92), "/")}" "$@"\n')
    env["PATH"] = str(shim) + os.pathsep + env["PATH"]
setup = ["bash", "kit/setup.sh"] + (["--voice"] if "--voice" in sys.argv else [])
code = run(setup, cwd=anim, env=env)
print("\nmodules ready in", T if code == 0 else f"{T} (kit setup exit {code}: read the log above)")
