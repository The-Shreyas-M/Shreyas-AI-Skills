"""Check dependencies of the one-file-launch-guide skill. Usage: python check_setup.py"""
import shutil, sys

print(("[ok]      " if sys.version_info >= (3, 9) else "[MISSING] ") + f"Python {sys.version.split()[0]} (need 3.9+)")
print("[ok]      build_guide.py uses only the standard library")
for name, found, fix in [
    ("Node.js 18+ (optional, for testing the guide)", shutil.which("node"), "install Node.js LTS"),
    ("npx (optional, for installing skills)", shutil.which("npx"), "comes with Node.js"),
    ("git (optional, to back up)", shutil.which("git"), "install git"),
]:
    print(("[ok]      " if found else "[missing] ") + name + ("" if found else "  ->  " + fix))
print("\nRecommended skills: youtube, shorts-from-main-video, frontend-design, gitcp (install commands in SKILL.md).")
