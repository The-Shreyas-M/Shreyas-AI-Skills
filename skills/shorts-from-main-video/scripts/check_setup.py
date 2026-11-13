"""Check every dependency of the shorts-from-main-video skill and print how to fix what is missing.
Usage: python check_setup.py
"""
import importlib, os, shutil, subprocess, sys

ok = True


def line(good, name, fix=""):
    global ok
    ok = ok and good
    print(("[ok]      " if good else "[MISSING] ") + name + ("" if good else "  ->  " + fix))


line(sys.version_info >= (3, 9), f"Python {sys.version.split()[0]} (need 3.9+)", "install Python 3.9+ from python.org")
for mod, pip in [("numpy", "numpy"), ("faster_whisper", "faster-whisper"), ("imageio_ffmpeg", "imageio-ffmpeg"), ("PIL", "pillow")]:
    try:
        importlib.import_module(mod)
        line(True, pip)
    except Exception:
        line(False, pip, f"pip install {pip}")

try:
    sys.path.insert(0, os.path.dirname(__file__))
    from ffmpeg_path import ffmpeg_exe
    exe = ffmpeg_exe()
    filters = subprocess.run([exe, "-hide_banner", "-filters"], capture_output=True, text=True).stdout
    line(" ass " in filters, f"ffmpeg with libass ({exe})",
         "need a full ffmpeg build: pip install imageio-ffmpeg, or set FFMPEG to a full build (gyan.dev 'full')")
    line("sidechaincompress" in filters and "loudnorm" in filters, "ffmpeg audio filters (sidechaincompress, loudnorm)", "use a full ffmpeg build")
except Exception as e:
    line(False, "ffmpeg", f"pip install imageio-ffmpeg  ({e})")

font = any(os.path.exists(p) for p in [r"C:\Windows\Fonts\impact.ttf", "/usr/share/fonts/truetype/impact.ttf",
                                       "/System/Library/Fonts/Supplemental/Impact.ttf"])
line(font, "Impact font (captions)", "optional: set \"font_file\" in the config to any bold .ttf (e.g. Anton from Google Fonts); falls back to Arial Black")

print("\nOptional, only for recording screen b-roll:")
for name, check, fix in [("Node.js 18+ (for playwright)", shutil.which("node"), "install Node.js LTS"),
                         ("Playwright browsers", shutil.which("npx"), "npm i playwright-core && npx playwright install chromium")]:
    print(("[ok]      " if check else "[missing] ") + name + ("" if check else "  ->  " + fix))
print("\nOptional skills: `youtube` (titles, SEO, thumbnails), `one-file-launch-guide` (posting guide). See SKILL.md.")
print("\nALL REQUIRED DEPENDENCIES OK" if ok else "\nFix the [MISSING] items above, then re-run.")
