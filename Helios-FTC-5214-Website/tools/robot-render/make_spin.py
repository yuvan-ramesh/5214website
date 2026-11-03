"""Turn the turntable PNGs into the WebP frames the site loads.
  python3 make_spin.py <render-out-dir> <site-public-assets-robot-dir>"""
import sys, os, glob
from PIL import Image
src, dst = sys.argv[1:3]
for d in ('spin', 'spin-sm'):
    os.makedirs(os.path.join(dst, d), exist_ok=True)
    for f in glob.glob(os.path.join(dst, d, '*.webp')): os.remove(f)
frames = sorted(glob.glob(os.path.join(src, 'f*-cad.png')))
for f in frames:
    i = int(os.path.basename(f)[1:4])
    im = Image.open(f).convert('RGBA')
    im.save(os.path.join(dst, 'spin', f'cad-{i:03d}.webp'), 'WEBP', quality=80, alpha_quality=85, method=6)
    im.resize((im.width // 2, im.height // 2), Image.LANCZOS).save(os.path.join(dst, 'spin-sm', f'cad-{i:03d}.webp'), 'WEBP', quality=78, alpha_quality=85, method=6)
size = lambda d: sum(os.path.getsize(p) for p in glob.glob(os.path.join(dst, d, '*.webp'))) / 1e6
print('frames', len(frames), 'spin MB', round(size('spin'), 2), 'spin-sm MB', round(size('spin-sm'), 2))
