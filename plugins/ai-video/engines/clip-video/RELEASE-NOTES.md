# Devini Community Edition 1.0 — 2026-11-01

Based on the supplied Claude-Video-Clipper archive (upstream commit
`d0d0ec6def447998b951a26b447c89538888847f`). Original source attribution retained.

Changes for this release:
- Added an extraction/setup guide, copyable prompts, and `run.py doctor` checks.
- Clarified Claude Code costs, transcript data flow, and optional Remotion licensing.
- Added YuNet's upstream MIT notice; retained Montserrat's OFL notice.
- Replaced uncredited bundled SFX with reproducible synthetic effects and source code.
- Kept OpenCV below version 5 for the bundled 2023 YuNet model's compatibility.
- Prevented cache reuse between same-named local videos or changed local sources.
- Made WAV extraction atomic and excluded unfinished download files from cache hits.
- Added a clear libass preflight error; made subtitle filter paths safe for spaced folders.
- Clamped caption start times at zero and escaped subtitle control characters.
- Detect decode/encode failures and reject horizontal inputs in vertical edit engines.
- Clamped clip handles to source duration, reset audio timestamps for splices, and aligned
  the final audio mix to an exact sample count.
- Added command help and reproducible optional npm installation (`npm ci`).

See VALIDATION.md for what was tested. No private footage, outputs, credentials, environments,
or downloaded dependencies are included in the share ZIP. This project clips existing speech;
it is not the separate long-form narration-replacement workflow.
