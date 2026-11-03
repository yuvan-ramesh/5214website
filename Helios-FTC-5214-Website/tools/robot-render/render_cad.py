"""Render the CAD for the website with three.js in headless Chromium.

  python3 render_cad.py hero robot-d.glb out           # CAD + silhouette from the photo's camera (hero_camera.json)
  python3 render_cad.py spin robot-d.glb out --frames 48

Serve this folder first: python3 -m http.server 8899
"""
import asyncio, base64, json, math, os, sys, time, argparse
from playwright.async_api import async_playwright

ap = argparse.ArgumentParser()
ap.add_argument('what', choices=['hero', 'spin']); ap.add_argument('glb'); ap.add_argument('out')
ap.add_argument('--frames', type=int, default=48)
ap.add_argument('--port', type=int, default=8899)
a = ap.parse_args()
os.makedirs(a.out, exist_ok=True)

# Onshape-style look: part colours, soft light, thin dark edges
CAD_LOOK = {'lineColor': 0x161412, 'lineOpacity': 0.85, 'hemi': 1.5, 'key': 1.5, 'fill': 0.5}


def orbit(az, el, dist, target, fov, roll=0):
    r, e = math.radians(az), math.radians(el)
    pos = [target[0] + dist * math.cos(e) * math.sin(r), target[1] + dist * math.sin(e), target[2] + dist * math.cos(e) * math.cos(r)]
    return {'pos': pos, 'target': target, 'fov': fov, 'roll': roll}


def save(url, path):
    open(path, 'wb').write(base64.b64decode(url.split(',', 1)[1]))


async def main():
    if a.what == 'hero':
        cam = json.load(open(os.path.join(os.path.dirname(__file__) or '.', 'hero_camera.json')))
        W, H, ss = cam['width'], cam['height'], 2           # render at 2x, make_hero.py scales down
        c = orbit(cam['az'], cam['el'], cam['dist'], cam['target'], cam['fov'], cam['roll'])
    else:
        W, H = 1280, 800
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width': 400, 'height': 300})
        pg.on('pageerror', lambda e: print('pageerror:', e, flush=True))
        await pg.goto(f'http://localhost:{a.port}/photo.html')
        await pg.wait_for_function('window.P && window.P.ready')
        if a.what == 'hero':
            await pg.evaluate('(o) => P.init(o)', {'url': a.glb, 'width': W * ss, 'height': H * ss})
            print('edges', await pg.evaluate('() => P.edges(35)'), flush=True)
            await pg.evaluate('(c) => P.camera(c)', c)
            look = dict(CAD_LOOK, linewidth=2.2)
            save(await pg.evaluate('(o) => P.render("cad", o)', look), os.path.join(a.out, 'hero-cad.png'))
            save(await pg.evaluate('() => P.render("mask", {})'), os.path.join(a.out, 'hero-mask.png'))
        else:
            await pg.evaluate('(o) => P.init(o)', {'url': a.glb, 'width': W, 'height': H})
            await pg.evaluate('() => P.edges(35)')
            look = dict(CAD_LOOK, thin=True)
            for i in range(a.frames):
                fn = os.path.join(a.out, f'f{i:03d}-cad.png')
                if os.path.exists(fn): continue
                await pg.evaluate('(c) => P.camera(c)', orbit(35 + i * 360 / a.frames, 20, 0.95, [-0.006, 0.058, 0.004], 28))
                save(await pg.evaluate('(o) => P.render("cad", o)', look), fn)
                print('frame', i, flush=True)
        await b.close()

asyncio.run(main())
