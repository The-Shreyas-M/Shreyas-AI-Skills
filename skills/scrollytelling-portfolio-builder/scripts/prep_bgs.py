"""
Gemini backgrounds (art/gemini/bg-*.jpg) -> public/media/bg/<name>.webp  (1920 wide, no keying).
  python tools/prep_bgs.py [src=art/gemini] [dst=public/media/bg]
Crops the bottom-right sparkle watermark by cropping 3% off the bottom, keeps the rest as is.
Variants (bg-rock1, bg-rock2 ...) are all written; the scenes pick one by name.
"""
import os, sys
from PIL import Image, ImageFilter

src = sys.argv[1] if len(sys.argv) > 1 else 'art/gemini'
dst = sys.argv[2] if len(sys.argv) > 2 else 'public/media/bg'
os.makedirs(dst, exist_ok=True)
for f in sorted(os.listdir(src)):
    if not f.startswith('bg-'):
        continue
    stem = f.split('.')[0][3:]
    im = Image.open(os.path.join(src, f)).convert('RGB')
    w, h = im.size
    # Gemini's sparkle sits in the bottom-right corner: paint it over with a soft, mirrored patch of the picture next to it
    x0, y0 = int(w * 0.905), int(h * 0.885)
    pw, ph = w - x0, h - y0
    patch = im.crop((x0 - pw, y0, x0, h)).transpose(Image.FLIP_LEFT_RIGHT).filter(ImageFilter.GaussianBlur(5))
    mask = Image.new('L', (pw, ph), 255).filter(ImageFilter.GaussianBlur(10))
    ring = Image.new('L', (pw, ph), 0)
    ring.paste(Image.new('L', (pw - 24, ph - 24), 255), (12, 12))
    mask = ring.filter(ImageFilter.GaussianBlur(9))
    im.paste(patch, (x0, y0), mask)
    im = im.crop((0, 0, w, int(h * 0.97)))
    if im.width > 1920:
        im = im.resize((1920, round(im.height * 1920 / im.width)), Image.LANCZOS)
    out = os.path.join(dst, stem + '.webp')
    im.save(out, 'WEBP', quality=74, method=6)
    print(stem, im.size, round(os.path.getsize(out) / 1024), 'KB')
