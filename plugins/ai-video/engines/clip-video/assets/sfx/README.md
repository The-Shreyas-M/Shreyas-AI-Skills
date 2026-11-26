# Sound effects

This Devini edition includes `whoosh-soft.wav`, `whoosh-short.wav`, and `click.wav`.
They are synthesized locally from deterministic noise and oscillators, with no recordings.
The source and generated WAVs are provided under the repository's MIT License.
Regenerate them with `python3 scripts/generate_sfx.py`.

The editor uses at most two quiet whooshes; `--sfx light` uses one and `--sfx none` disables them.
You can add your own licensed audio files with whoosh, hit, or click in their filenames.
The generated `catalog.json` is a cache and is rebuilt when the file list changes.
