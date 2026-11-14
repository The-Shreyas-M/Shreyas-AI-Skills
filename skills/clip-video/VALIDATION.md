# Validation — Devini Community Edition 1.0

Checked on 2026-11-01 on macOS / Apple Silicon with Python 3.11.

Passed:
- Python source parsing and skill frontmatter/reference layout validation.
- Fresh isolated installation of the declared Python requirements; pip dependency check.
- Setup doctor, including actual YuNet inference and FFmpeg/libass capability checks.
- Three focused regression tests: distinct local-source caches, interrupted audio extraction,
  and caption timestamps / literal subtitle text.
- Actual transcription of a nine-second local speech sample with Whisper tiny.en: word-level
  timestamps and transcript files were produced. This checks the transcription path, not
  recognition accuracy across all languages and models.
- Synthetic local-video smoke test through vertical cutting, framing, zooms, caption burn-in,
  generated SFX mixing, SRT export, and H.264/AAC MP4 output at 1080 × 1920.
- Final smoke export decoded successfully and a representative captioned frame was inspected.
- ZIP integrity and per-file SHA-256 manifest checks at packaging time.

The captioned export test used an isolated FFmpeg 7.1 build with libass. It did not replace
system FFmpeg. Tested core packages included faster-whisper 1.2.1, OpenCV 4.14.0, NumPy 2.4.6,
SoundFile 0.14.0, and yt-dlp 2026.10.26. Setup installs compatible versions from requirements.txt;
these are tested versions, not a full dependency lock.

Not end-to-end tested in this release:
- Windows/Linux installation, CUDA, every language/model, or long-source performance.
- Live YouTube downloads, browser-cookie login, and active-speaker selection in multi-person scenes.
- Optional Remotion renderer installation/rendering (its original package lock is retained).

The test footage, speech sample, test environments, model cache, and rendered outputs are not
included in the distribution. Review captions, boundaries, and framing for each real video.
