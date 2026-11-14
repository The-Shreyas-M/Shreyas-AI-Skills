"""Read-only setup checks. Run: python run.py doctor"""
import shutil
import subprocess
import sys

from .common import ASSETS, ROOT


def ffmpeg_has_filter(name):
    if not shutil.which('ffmpeg'):
        return False
    result = subprocess.run(['ffmpeg', '-hide_banner', '-filters'], capture_output=True, text=True)
    return result.returncode == 0 and any(len(parts := line.split()) > 1 and parts[1] == name
                                        for line in result.stdout.splitlines())


def main():
    failed = []

    def report(label, ok, fix=''):
        print(f'[{"ok" if ok else "X"}] {label}' + (f' — {fix}' if not ok and fix else ''))
        if not ok:
            failed.append(label)

    report('Python 3.10+', sys.version_info >= (3, 10))
    for name in ('ffmpeg', 'ffprobe'):
        report(name, bool(shutil.which(name)), 'See START-HERE.md')
    if shutil.which('ffmpeg'):
        enc = subprocess.run(['ffmpeg', '-hide_banner', '-encoders'], capture_output=True, text=True)
        report('H.264 / libx264 encoder', enc.returncode == 0 and 'libx264' in enc.stdout)
        for name in ('loudnorm', 'acompressor'):
            report(f'FFmpeg {name}', ffmpeg_has_filter(name))
        if not ffmpeg_has_filter('ass'):
            print('[!] FFmpeg lacks libass. Default captioned edits need a libass-enabled build; '
                  'see START-HERE.md. --no-captions or optional Remotion remain alternatives.')
        else:
            print('[ok] FFmpeg libass captions')
    for name in ('yt_dlp', 'faster_whisper', 'soundfile', 'numpy', 'cv2'):
        # Keep PyAV and OpenCV's separate FFmpeg libraries out of one process on macOS.
        code = f'import {name}'
        if name == 'cv2':
            model = str(ASSETS / 'models/face_detection_yunet_2023mar.onnx')
            code += (f'; import numpy as np; d=cv2.FaceDetectorYN.create({model!r}, "", (320,320)); '
                     'd.detect(np.zeros((320,320,3), dtype=np.uint8))')
        result = subprocess.run([sys.executable, '-c', code], capture_output=True, text=True)
        report(name + (' and YuNet inference' if name == 'cv2' else ''), result.returncode == 0,
               '\n'.join(result.stderr.splitlines()[-4:]) or 'rerun install.py')
    for path in ('fonts/Montserrat-ExtraBold.ttf', 'fonts/OFL.txt', 'models/LICENSE'):
        report(path, (ASSETS / path).is_file())
    print('[ok] Node.js available' if shutil.which('node') else '[!] Node.js recommended for YouTube downloads')
    print(f'Free space: {shutil.disk_usage(ROOT).free / 1024**3:.1f} GiB (long videos need several GiB)')
    print('Core checks passed. Review any [!] notices.' if not failed else 'Fix [X] items, then rerun this check.')
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
