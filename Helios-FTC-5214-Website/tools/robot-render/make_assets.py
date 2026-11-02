"""Convert rendered PNGs into the WebP files the site uses.

usage: python3 make_assets.py <render-out-dir> <site-public-assets-robot-dir>
"""
import sys, os, glob
from PIL import Image, ImageChops

src, dst = sys.argv[1], sys.argv[2]
os.makedirs(os.path.join(dst, 'spin'), exist_ok=True)
os.makedirs(os.path.join(dst, 'spin-sm'), exist_ok=True)


def save(im, path, q, alpha):
    if alpha:
        im.save(path, 'WEBP', quality=q, alpha_quality=90, method=6)
    else:
        im.convert('RGB').save(path, 'WEBP', quality=q, method=6)


hr = Image.open(os.path.join(src, 'hero-render.png')).convert('RGBA')
hc = Image.open(os.path.join(src, 'hero-cad.png')).convert('RGB')
save(hr, os.path.join(dst, 'hero-render.webp'), 88, True)
save(hc, os.path.join(dst, 'hero-cad.webp'), 90, False)
hl = os.path.join(src, 'hero-cadlight.png')
if os.path.exists(hl):
    save(Image.open(hl).convert('RGBA'), os.path.join(dst, 'hero-cad-light.webp'), 90, True)

frames = sorted(glob.glob(os.path.join(src, 'f*-render.png')))
for f in frames:
    i = int(os.path.basename(f)[1:4])
    r = Image.open(f).convert('RGBA')
    c = Image.open(f.replace('-render.png', '-cad.png')).convert('RGB')
    # lift the background to the section color (--night #121010) so no box shows
    c = ImageChops.lighter(c, Image.new('RGB', c.size, (0x12, 0x10, 0x10)))
    save(r, os.path.join(dst, 'spin', f'render-{i:03d}.webp'), 80, True)
    save(c, os.path.join(dst, 'spin', f'cad-{i:03d}.webp'), 82, False)
    w, h = r.size
    save(r.resize((w // 2, h // 2), Image.LANCZOS), os.path.join(dst, 'spin-sm', f'render-{i:03d}.webp'), 78, True)
    save(c.resize((w // 2, h // 2), Image.LANCZOS), os.path.join(dst, 'spin-sm', f'cad-{i:03d}.webp'), 80, False)


def total(d):
    return sum(os.path.getsize(p) for p in glob.glob(os.path.join(dst, d, '*.webp')))


print('frames', len(frames))
print('hero KB', round((os.path.getsize(os.path.join(dst, 'hero-render.webp')) + os.path.getsize(os.path.join(dst, 'hero-cad.webp'))) / 1024))
print('spin MB', round(total('spin') / 1e6, 2), 'spin-sm MB', round(total('spin-sm') / 1e6, 2))
