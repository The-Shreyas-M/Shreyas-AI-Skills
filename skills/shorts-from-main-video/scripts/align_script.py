"""Captions from the SCRIPT, not from speech recognition (use this whenever the audio is synthetic / the text is known).

Why: Whisper mis-hears names and brand words ("Claude" -> "clod"). When you generated the voice from a script,
the script IS the ground truth. Whisper is used only to find WHEN each word is spoken (timing), then its words are
aligned to the script words and discarded. Mismatches are printed so you can also catch a mispronunciation.

    from align_script import align_script
    words, report = align_script(spoken_text, wav_path)           # [{"w","s","e"}], {"match":0.97,"mismatch":[(script,heard)]}
`spoken_text` is what the voice says (write numbers/symbols as words). COLLAPSE turns spoken forms back into display
forms ("slash ai dash video" -> "/ai-video"). Extend it per project.
"""
import difflib, re, wave
import numpy as np

COLLAPSE = {("slash", "ai", "dash", "video"): "/ai-video", ("install", "dot", "py"): "install.py",
            ("m", "i", "t"): "MIT", ("c", "s", "v"): "CSV", ("a", "i"): "AI"}
_norm = lambda t: re.sub(r"[^a-z0-9]", "", t.lower())


def _read_wav(path):
    w = wave.open(path)
    sr, ch = w.getframerate(), w.getnchannels()
    a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
    if ch > 1:
        a = a.reshape(-1, ch).mean(1)
    if sr != 16000:
        a = np.interp(np.linspace(0, len(a) - 1, int(len(a) * 16000 / sr)), np.arange(len(a)), a).astype(np.float32)
    return a, len(a) / 16000


_model = {}


def heard_words(path, model_name="small.en"):
    from faster_whisper import WhisperModel
    if model_name not in _model:
        _model[model_name] = WhisperModel(model_name, device="cpu", compute_type="int8")
    a, dur = _read_wav(path)
    segs, _ = _model[model_name].transcribe(a, language="en", word_timestamps=True)
    return [{"w": x.word.strip(), "s": x.start, "e": x.end} for s in segs for x in s.words], dur


def align_script(spoken_text, wav_path, model_name="small.en"):
    script = spoken_text.split()
    heard, dur = heard_words(wav_path, model_name)
    ns, nh = [_norm(w) for w in script], [_norm(w["w"]) for w in heard]
    t = [None] * len(script)  # (start, end) per script word
    for blk in difflib.SequenceMatcher(None, ns, nh, autojunk=False).get_matching_blocks():
        for k in range(blk.size):
            t[blk.a + k] = (heard[blk.b + k]["s"], heard[blk.b + k]["e"])
    matched = sum(x is not None for x in t)
    mism = []
    i = 0
    while i < len(script):  # fill gaps proportionally to word length between anchors
        if t[i] is None:
            j = i
            while j < len(script) and t[j] is None:
                j += 1
            lo = t[i - 1][1] if i > 0 else 0.0
            hi = t[j][0] if j < len(script) else dur
            hi = max(hi, lo + 0.05 * (j - i))
            tot = sum(len(script[k]) for k in range(i, j)) or 1
            cur = lo
            for k in range(i, j):
                step = (hi - lo) * len(script[k]) / tot
                t[k] = (cur, cur + step)
                cur += step
            i = j
        else:
            i += 1
    for blk in difflib.SequenceMatcher(None, ns, nh, autojunk=False).get_opcodes():
        if blk[0] == "replace":
            mism.append((" ".join(script[blk[1]:blk[2]]), " ".join(w["w"] for w in heard[blk[3]:blk[4]])))
    words, i = [], 0
    low = [_norm(w) for w in script]
    while i < len(script):
        for pat, disp in COLLAPSE.items():
            if tuple(low[i:i + len(pat)]) == pat:
                words.append({"w": disp, "s": t[i][0], "e": t[i + len(pat) - 1][1]})
                i += len(pat)
                break
        else:
            words.append({"w": script[i], "s": t[i][0], "e": t[i][1]})
            i += 1
    return words, {"match": round(matched / max(1, len(script)), 3), "mismatch": mism, "duration": dur}
