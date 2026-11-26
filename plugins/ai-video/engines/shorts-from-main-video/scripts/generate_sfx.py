"""Regenerate this release's original synthetic SFX (Python standard library only).

The source and generated WAV files are provided under the repository's MIT License.
No recordings, third-party samples, online service, or API key are used.
"""
import math
import random
import struct
import wave
from pathlib import Path

DEST = Path(__file__).resolve().parents[1] / 'assets' / 'sfx'
SR = 48000


def write(name, duration, seed, click=False):
    rng = random.Random(seed)
    count = round(duration * SR)
    values = []
    low = 0.0
    phase = 0.0
    for i in range(count):
        t = i / SR
        u = i / max(1, count - 1)
        noise = rng.uniform(-1, 1)
        low += 0.12 * (noise - low)
        if click:
            envelope = min(1, t / 0.002) * math.exp(-t * 55) * (1-u)
            value = envelope * (0.55 * math.sin(2 * math.pi * 1700 * t) + 0.45 * noise)
        else:
            envelope = math.sin(math.pi * u) ** 2.4
            phase += 2 * math.pi * (170 + 1100 * u * u) / SR
            value = envelope * (0.8 * low + 0.17 * math.sin(phase))
        values.append(value)
    peak = max(abs(v) for v in values) or 1
    with wave.open(str(DEST / name), 'wb') as f:
        f.setparams((1, 2, SR, count, 'NONE', 'not compressed'))
        f.writeframes(b''.join(struct.pack('<h', round(v / peak * 0.7 * 32767)) for v in values))


if __name__ == '__main__':
    DEST.mkdir(parents=True, exist_ok=True)
    write('whoosh-soft.wav', 0.75, 71)
    write('whoosh-short.wav', 0.48, 91)
    write('click.wav', 0.16, 37, click=True)
    (DEST / 'catalog.json').unlink(missing_ok=True)
    print('Generated three synthetic sound effects in assets/sfx/')
