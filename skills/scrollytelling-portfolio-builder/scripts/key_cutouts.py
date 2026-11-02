"""
Turn Gemini images on a flat green background into trimmed WebP cutouts with alpha.

  python tools/key_cutouts.py [src=art/gemini] [dst=public/media] [--max 1500] [--quality 84]

For every image in `src` named <act>-<name>.png (a1-solder.png, a5-kata.png ...):
  - keys out the green (hue-distance based, soft edge) and removes green spill from the edges
  - clears the bottom-right 10% corner (Gemini's sparkle watermark)
  - trims to the figure
  - names ending in `-kata`, `-dyno`, `-skate` are STRIPS: sliced into separate poses on the empty gaps
    and written as <name>_0000.webp, _0001.webp ... (one shared crop, so the figure doesn't jitter)
p-<name> -> props, cat-<name> -> cats (single objects on green). bg-* are not keyed: see prep_bgs.py.
Output folder is chosen by the act prefix: a1 -> builder, a2 -> thinker, a3 -> artist, a4 -> wild, a5 -> discipline,
a6 and fin -> human. Prints sizes against the budgets (still <= 250 KB, strip <= 1.5 MB).
"""
import os, sys, re, argparse
import numpy as np
from PIL import Image
from scipy import ndimage as nd

ap = argparse.ArgumentParser()
ap.add_argument('src', nargs='?', default='art/gemini')
ap.add_argument('dst', nargs='?', default='public/media')
ap.add_argument('--max', type=int, default=1500)
ap.add_argument('--quality', type=int, default=84)
a = ap.parse_args()

ACT = {'p': 'props', 'cat': 'cats', 'a1': 'builder', 'a2': 'thinker', 'a3': 'artist', 'a4': 'wild', 'a5': 'discipline', 'a6': 'human', 'fin': 'human'}
STRIPS = ('-kata', '-dyno', '-skate', '-tabla-strike', '-gym', '-walk', '-pedal')


FILL_HOLES = ('p-xp-desktop',)  # props whose own screen is green-ish: anything enclosed by the object stays solid


def key(im, clear=(0.90, 0.90), fill=False):
    """RGBA from an image on a flat green: alpha from the distance to the background colour."""
    rgb = np.asarray(im.convert('RGB')).astype(np.float32)
    h, w, _ = rgb.shape
    border = np.concatenate([rgb[0], rgb[-1], rgb[:, 0], rgb[:, -1]])
    bg = np.median(border, axis=0)
    # "greenness": how much G exceeds R and B, relative to the background's own excess
    excess = rgb[..., 1] - np.maximum(rgb[..., 0], rgb[..., 2])
    bg_excess = max(bg[1] - max(bg[0], bg[2]), 1.0)
    g = np.clip(excess / bg_excess, 0, 1)
    alpha = 1 - np.clip((g - 0.35) / 0.5, 0, 1)             # soft edge between 35% and 85% greenness
    alpha = nd.grey_erosion(alpha, size=2)                   # pull the edge in a pixel: no halo
    # de-spill: where green still exceeds the others, clamp it to them
    spill = np.maximum(rgb[..., 1] - np.maximum(rgb[..., 0], rgb[..., 2]), 0)
    rgb[..., 1] -= spill * 0.9
    if fill:
        # enclosed 'background' (the CRT's green hills) is part of the prop: keep it, with its original colours
        bgm = alpha < 0.5
        lab0, n0 = nd.label(bgm)
        edge = np.unique(np.concatenate([lab0[0], lab0[-1], lab0[:, 0], lab0[:, -1]]))
        holes = bgm & ~np.isin(lab0, edge)
        holes[int(h * 0.68):] = False  # the screen is in the upper part: gaps near the keyboard stay see-through
        holes = nd.binary_erosion(holes, iterations=2)  # stay a little inside the rim
        alpha[holes] = 1.0
        rgb[holes] = np.asarray(im.convert('RGB')).astype(np.float32)[holes]
    # small islands of leftover background (between arm and body) are keyed by the same rule; drop dust
    mask = alpha > 0.5
    lab, n = nd.label(mask)
    if n > 1:
        sizes = nd.sum(mask, lab, range(1, n + 1))
        keep = np.isin(lab, 1 + np.flatnonzero(sizes > mask.size * 0.0004))
        alpha = alpha * nd.binary_dilation(keep, iterations=3)
    # Gemini stamps a small sparkle in the bottom-right corner: clear that corner (the figure never reaches it)
    alpha[int(h * clear[1]):, int(w * clear[0]):] = 0
    out = np.dstack([np.clip(rgb, 0, 255), alpha * 255]).astype(np.uint8)
    return Image.fromarray(out, 'RGBA')


def keep_main(im, frac=0.05):
    """Drop stray islands (specks, leftover shadow) that would widen the trim box and push the figure off centre."""
    a = np.asarray(im.getchannel('A')) > 40
    lab, n = nd.label(nd.binary_dilation(a, iterations=8))
    if n < 2:
        return im
    sizes = nd.sum(a, lab, range(1, n + 1))
    keep = np.isin(lab, 1 + np.flatnonzero(sizes >= sizes.max() * frac))
    arr = np.asarray(im).copy()
    arr[~keep, 3] = 0
    return Image.fromarray(arr, 'RGBA')


def trim(ims, pad=10):
    boxes = [i.getchannel('A').point(lambda v: 255 if v > 24 else 0).getbbox() for i in ims]
    boxes = [b for b in boxes if b]
    l, t = min(b[0] for b in boxes), min(b[1] for b in boxes)
    r, b_ = max(b[2] for b in boxes), max(b[3] for b in boxes)
    return (max(l - pad, 0), max(t - pad, 0), min(r + pad, ims[0].width), min(b_ + pad, ims[0].height))


def drop_below_gap(im, min_gap=10):
    """Gemini sometimes draws stray legs under a figure (left over from the reference image). Everything below the
    first empty band of rows under the figure is removed."""
    rows = (np.asarray(im.getchannel('A')) > 40).any(axis=1)
    ys = np.flatnonzero(rows)
    if ys.size == 0:
        return im
    y = ys.min()
    while y < len(rows):
        if not rows[y]:
            end = y
            while end < len(rows) and not rows[end]:
                end += 1
            if end - y >= min_gap and end < len(rows):  # an empty band with more content below it
                a = np.asarray(im).copy()
                a[y:, :, 3] = 0
                return Image.fromarray(a, 'RGBA')
            y = end
        else:
            y += 1
    return im


def slice_strip(im):
    """Cut a strip into its poses with 2D blob detection (poses may overlap in x). Returns RGBA images the size of
    the source, one per pose, ordered left to right; small bits (a hold, chalk dust) join the nearest pose."""
    alpha = np.asarray(im.getchannel('A')) > 40
    grown = nd.binary_dilation(alpha, iterations=6)
    lab, n = nd.label(grown)
    if n == 0:
        return []
    areas = nd.sum(alpha, lab, range(1, n + 1))
    big = [k + 1 for k, a_ in enumerate(areas) if a_ >= areas.max() * 0.2]
    if not big:
        return []
    centers = {k: nd.center_of_mass(alpha, lab, k) for k in range(1, n + 1)}
    owner = {}
    for k in range(1, n + 1):
        if k in big:
            owner[k] = k
        else:  # attach to the nearest big blob
            owner[k] = min(big, key=lambda b: (centers[b][0] - centers[k][0]) ** 2 + (centers[b][1] - centers[k][1]) ** 2)
    big.sort(key=lambda k: centers[k][1])
    arr = np.asarray(im).copy()
    out = []
    for b in big:
        mask = np.isin(lab, [k for k, o in owner.items() if o == b])
        mask = nd.binary_dilation(mask, iterations=2)
        cell = arr.copy()
        cell[~mask, 3] = 0
        out.append(Image.fromarray(cell, 'RGBA'))
    return out


def save(frames, name, folder):
    box = trim(frames)
    s = a.max / max(box[2] - box[0], box[3] - box[1])
    total = 0
    os.makedirs(os.path.join(a.dst, folder), exist_ok=True)
    for k, f in enumerate(frames):
        c = f.crop(box)
        if s < 1:
            c = c.resize((round(c.width * s), round(c.height * s)), Image.LANCZOS)
        out = os.path.join(a.dst, folder, name + (f'_{k:04d}' if len(frames) > 1 else '') + '.webp')
        c.save(out, 'WEBP', quality=a.quality, method=6)
        total += os.path.getsize(out)
    print(f'{folder}/{name}: {len(frames)} frame(s), {c.size[0]}x{c.size[1]}, {total / 1024:.0f} KB')


def strip_frames(rgba, bottom_align=False, centroid=False):
    """Poses of a strip as equal-size cells (so the sequence is steady): each pose keeps its own height in the strip."""
    poses = slice_strip(rgba)
    if not poses:
        return []
    boxes = [p.getchannel('A').point(lambda v: 255 if v > 24 else 0).getbbox() for p in poses]
    wmax = max(b[2] - b[0] for b in boxes)
    top, bottom = min(b[1] for b in boxes), max(b[3] for b in boxes)
    cells = []
    if bottom_align:
        # seated poses (the tabla): every pose keeps its own seat on one baseline, so the figure never drifts between frames
        hmax = max(b[3] - b[1] for b in boxes)
        for p, b in zip(poses, boxes):
            cell = Image.new('RGBA', (wmax + 20, hmax), (0, 0, 0, 0))
            cell.paste(p.crop(b), ((wmax + 20 - (b[2] - b[0])) // 2, hmax - (b[3] - b[1])))
            cells.append(cell)
        return cells
    if centroid:
        # a leap: centre every pose on its body mass (not its bounding box, which swings with the outstretched arms)
        cxs = [np.nonzero(np.asarray(p.getchannel('A')) > 40)[1].mean() for p in poses]
        half = max(max(cx - b[0], b[2] - cx) for cx, b in zip(cxs, boxes)) + 10
        for p, b, cx in zip(poses, boxes, cxs):
            cell = Image.new('RGBA', (int(half * 2), bottom - top), (0, 0, 0, 0))
            cell.paste(p.crop((b[0], top, b[2], bottom)), (int(half - (cx - b[0])), 0))
            cells.append(cell)
        return cells
    for p, b in zip(poses, boxes):
        cell = Image.new('RGBA', (wmax + 20, bottom - top), (0, 0, 0, 0))
        cell.paste(p.crop((b[0], top, b[2], bottom)), ((wmax + 20 - (b[2] - b[0])) // 2, 0))
        cells.append(cell)
    return cells


groups = {}  # a pose-split sequence (a5-kata_pose1and2 + a5-kata_pose3and4) gathers here, in file order
for f in sorted(os.listdir(a.src)):
    stem, ext = os.path.splitext(f)
    if ext.lower() not in ('.png', '.webp', '.jpg', '.jpeg'):
        continue
    while stem.lower().endswith(('.png', '.webp', '.jpg', '.jpeg')):  # "a4-hike.png.png"
        stem = os.path.splitext(stem)[0]
    act = stem.split('-')[0]
    if act not in ACT:
        print('skip (no act prefix):', f)
        continue
    if re.search(r'_f\d+$', stem):
        # one frame of a move, generated on its own: a4-hike-walk_f1.png, a4-hike-walk_f2.png ...  (merged below, feet on one baseline)
        rgba = key(Image.open(os.path.join(a.src, f)))
        box = rgba.getchannel('A').point(lambda v: 255 if v > 24 else 0).getbbox()
        groups.setdefault(re.sub(r'_f\d+$', '', stem), []).append(rgba.crop(box))
        continue
    # a walk strip has the last pose's boots close to the corner: clear only the sparkle itself
    rgba = key(Image.open(os.path.join(a.src, f)), clear=(0.935, 0.72) if stem.endswith('-walk') else (0.90, 0.90), fill=stem in FILL_HOLES)
    if '_pose' in stem:
        rgba = drop_below_gap(rgba)  # one move split over several images: a5-kata_pose1and2, a5-kata_pose3and4
        base = stem.split('_pose')[0]
        frames = strip_frames(rgba)
        if len(frames) < 1:
            print('WARN', f, 'no poses found')
            continue
        groups.setdefault(base, []).extend(frames)
    elif stem.endswith(STRIPS):
        frames = strip_frames(rgba, stem.endswith('-tabla-strike'), stem.endswith('-dyno'))
        if len(frames) < 2:
            print('WARN', f, 'did not split into poses (gaps too small?), found', len(frames))
            continue
        save(frames, stem[len(act) + 1:], ACT[act])
    else:
        save([keep_main(rgba) if 'yoga-' in stem else rgba], stem[len(act) + 1:], ACT[act])

for base, frames in groups.items():
    # all frames must share one canvas size so the sequence is steady
    w, h = max(f.width for f in frames), max(f.height for f in frames)
    fixed = []
    for f in frames:
        c = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        c.paste(f, ((w - f.width) // 2, h - f.height))
        fixed.append(c)
    act = base.split('-')[0]
    save(fixed, base[len(act) + 1:], ACT[act])
