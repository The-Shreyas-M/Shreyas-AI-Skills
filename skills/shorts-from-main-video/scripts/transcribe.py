"""Transcribe a talking-head video with word timestamps (faster-whisper, CPU).

Usage: python transcribe.py <video> <outdir>
Writes <outdir>/tr.json  -> [{start,end,text,words:[{w,s,e}]}]  and prints numbered lines.
The line numbers (L0, L1, ...) are what make_short.py configs refer to.
"""
import json, os, subprocess, sys, wave
import numpy as np
from ffmpeg_path import ffmpeg_exe

video, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
wav = os.path.join(out, "audio.wav")
subprocess.run([ffmpeg_exe(), "-y", "-loglevel", "error", "-i", video, "-vn", "-ac", "1", "-ar", "16000", wav], check=True)

from faster_whisper import WhisperModel

model = WhisperModel("small", device="cpu", compute_type="int8")
w = wave.open(wav)
# Feed a numpy array: passing a file path breaks on some PyAV versions.
audio = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0
segs, _ = model.transcribe(audio, word_timestamps=True, language="en", vad_filter=True, beam_size=5)
res = [{"start": s.start, "end": s.end, "text": s.text.strip(),
        "words": [{"w": x.word.strip(), "s": x.start, "e": x.end} for x in s.words]} for s in segs]
json.dump(res, open(os.path.join(out, "tr.json"), "w"), indent=1)
for i, s in enumerate(res):
    print(f"L{i:<3} [{s['start']:6.1f}-{s['end']:6.1f}] {s['text']}")
