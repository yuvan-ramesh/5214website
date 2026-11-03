"""Build the hero images: the real photo of Eclipse cut out, plus the CAD from the same camera.

  python3 make_hero.py <photo> <render-out-dir> <site-public-assets-robot-dir>

Needs: pip install rembg onnxruntime opencv-python-headless pillow numpy
"""
import sys, os, json
import numpy as np, cv2
from PIL import Image
from rembg import remove, new_session

photo_path, src, dst = sys.argv[1:4]
cam = json.load(open(os.path.join(os.path.dirname(__file__) or '.', 'hero_camera.json')))
W, H = cam['width'], cam['height']
photo = Image.open(photo_path).convert('RGB').resize((W, H))
cad = Image.open(os.path.join(src, 'hero-cad.png')).convert('RGBA').resize((W, H), Image.LANCZOS)
cad_mask = np.array(Image.open(os.path.join(src, 'hero-mask.png')).convert('L').resize((W, H))) > 127

# 1. cut the robot out of the photo, keeping only what sits near the CAD silhouette (drops tools on the bench)
m = np.array(remove(photo, session=new_session('isnet-general-use'), only_mask=True)).astype(np.float32) / 255
near = cv2.GaussianBlur(cv2.dilate(cad_mask.astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (61, 61))).astype(np.float32), (0, 0), 12)
m = np.clip(m * np.clip(near * 1.6, 0, 1), 0, 1)
n, lab, st, _ = cv2.connectedComponentsWithStats((m > 0.3).astype(np.uint8))
keep = np.isin(lab, [i for i in range(1, n) if st[i, cv2.CC_STAT_AREA] > 4000]).astype(np.uint8)
m *= cv2.GaussianBlur(cv2.dilate(keep, np.ones((9, 9), np.uint8)).astype(np.float32), (0, 0), 3)

# 2. brighten the dim pit photo
lin = (np.asarray(photo, np.float32) / 255) ** 2.2 * 2.1
out = np.clip(lin / (1 + lin * 0.35), 0, 1) ** (1 / 2.2)
g = out.mean(2, keepdims=True); out = np.clip(g + (out - g) * 1.08, 0, 1)
lab8 = cv2.cvtColor((out * 255).astype(np.uint8), cv2.COLOR_RGB2LAB)
lab8[..., 0] = cv2.createCLAHE(1.6, (8, 8)).apply(lab8[..., 0])
rgb = cv2.cvtColor(lab8, cv2.COLOR_LAB2RGB)

# 3. crop both the same way and save
box = tuple(cam['crop'])
Image.fromarray(np.dstack([rgb, (m * 255).astype(np.uint8)])).crop(box).save(os.path.join(dst, 'hero-photo.webp'), 'WEBP', quality=86, alpha_quality=92, method=6)
cad.crop(box).save(os.path.join(dst, 'hero-cad.webp'), 'WEBP', quality=90, alpha_quality=92, method=6)
print('saved', box[2] - box[0], 'x', box[3] - box[1])
