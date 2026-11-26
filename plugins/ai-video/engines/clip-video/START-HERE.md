# Start here — Claude Video Clipper

## 1. Extract the complete ZIP

Download the ZIP from Drive, then extract it to a normal local folder. Open
`Devini-Claude-Video-Clipper-v1.0`, the folder containing `run.py` and `install.py`.
Keep all its folders together, including the hidden `.claude` folder. Do not copy only
`SKILL.md` into another project; it needs the bundled tools and assets.

On a Mac, press Command + Shift + . in Finder to show hidden files if needed.

## 2. Install the prerequisites

- **Claude Code** configured with your own account: https://code.claude.com/docs/en/overview
- **Python 3.10 or later**. Python 3.11 or 3.12 is a practical choice if a newer version has
  dependency-install problems. https://www.python.org/downloads/
- **FFmpeg and ffprobe**, with `libx264` and **libass** for the default caption renderer.
- **Node.js** is recommended for YouTube downloads and required for optional Remotion.
  https://nodejs.org/
- Several GiB of free space for dependencies, speech models, and your videos. Longer sources
  need more. The first transcription downloads the selected Whisper model.

### macOS with Homebrew

```bash
brew install python@3.11 node ffmpeg-full
export PATH="$(brew --prefix ffmpeg-full)/bin:$PATH"
```

Run the `export` line in the same terminal where you launch setup and Claude Code.
`ffmpeg-full` is keg-only; merely installing it may leave another FFmpeg first on PATH.
If using a desktop app, ensure its terminal inherits this PATH or configure its environment.
Run `ffmpeg -hide_banner -filters` and check for `ass` if captions fail.
Official formula: https://formulae.brew.sh/formula/ffmpeg-full

### Windows

Install Python and enable its PATH option. In PowerShell:

```powershell
winget install -e --id Gyan.FFmpeg
winget install -e --id OpenJS.NodeJS.LTS
```

Open a new terminal after installation. Use `py` in place of `python3` below.

### Ubuntu / Debian

```bash
sudo apt update
sudo apt install python3 python3-venv ffmpeg
```

Install a supported Node.js version from nodejs.org if using YouTube or Remotion.

## 3. Run setup in the extracted folder

```bash
python3 install.py
python3 run.py doctor
```

Setup creates a private `.venv` in this folder and installs the declared dependencies.
It does not automatically install system tools. Fix any `[X]` items and review `[!]` notices.
You can rerun setup. No API key needs to be pasted into these files.

## 4. Open this folder in Claude Code

Open the extracted folder as the Claude Code project, or launch `claude` from its terminal.
The project skill is `.claude/skills/clip-video/SKILL.md`. Invoke it with:

```text
/clip-video https://www.youtube.com/watch?v=YOUR_VIDEO_ID
```

Or paste this prompt:

```text
Clip this video: [PASTE YOUR VIDEO LINK OR LOCAL FILE PATH]
Create the 5 strongest self-contained vertical clips, ideally 25–60 seconds each.
Use a strong opening and a complete ending. Add readable word-timed captions,
subtle zooms, and light sound effects. Check the cuts and captions before delivery.
```

A local video is a useful first test because it avoids YouTube download restrictions.
If `/clip-video` is missing, confirm that Claude Code opened the folder containing `run.py`
and that `.claude/skills/clip-video/SKILL.md` survived extraction. Restart the session.
Claude skill documentation: https://code.claude.com/docs/en/skills

## 5. Find the results

- `output/<project>/clips/`: raw vertical cuts.
- `output/<project>/edited/`: final captioned MP4s and SRT files.
- `output/<project>/clips.json`: moment choices and posting copy.
- `output/<project>/transcript/`: transcript and word timestamps.

Keep the original local video available until editing is complete. Do not move or rename it
mid-project. Share the final exports you choose, not your whole working project.

## Troubleshooting

- **Missing FFmpeg/libass:** follow step 2. Default Homebrew FFmpeg may omit libass. For cuts
  and uncaptioned edits, `--no-captions` works. Remotion is another caption-rendering option.
- **Optional Remotion:** run `python3 install.py --remotion`, then
  `python3 run.py edit <project> --engine remotion`. The first render may download a browser.
  Check Remotion's license before using that engine for your organization.
- **YouTube sign-in or download failure:** first rerun setup to update yt-dlp. If your own
  signed-in browser can view the video, explicitly request
  `python3 run.py fetch "<URL>" --cookies-from-browser chrome` (or Firefox/Edge).
  This reads that browser's login cookies for the download. Never share cookie files.
  If the source still fails, use a permitted local download; do not keep retrying indefinitely.
- **Wrong language:** `python3 run.py fetch "<source>" --lang en --retranscribe`.
- **Low memory / slow transcription:** try `--model base.en --lang en` for English, or `base`
  for other languages. Processing speed depends on your hardware and source length.
- **Incorrect face crop:** review multi-person shots and ask Claude to adjust framing.
- **Horizontal clips:** `cut --horizontal` preserves source framing. The bundled edit engines
  are for vertical 1080 × 1920 clips and now reject horizontal input instead of stretching it.

The tool keeps original speech. Custom narration and full-length tutorial reconstruction are
separate workflows, not features of this clipping package.
