"""Render the robot: hero beauty + skeleton, and turntable sequences.

usage: python3 drive.py <model-url-or-TEST> <outdir> [--frames N] [--hero-only] [--size WxH] [--ss 2] [--json opts]
"""
import asyncio, base64, io, json, os, sys, time, argparse
from PIL import Image
from playwright.async_api import async_playwright

ap = argparse.ArgumentParser()
ap.add_argument('model'); ap.add_argument('out')
ap.add_argument('--frames', type=int, default=0)
ap.add_argument('--size', default='1600x1000')
ap.add_argument('--ss', type=float, default=2)
ap.add_argument('--opts', default='{}')
ap.add_argument('--hero-az', type=float, default=35)
ap.add_argument('--start-az', type=float, default=35)
ap.add_argument('--modes', default='beauty,skeleton')
ap.add_argument('--port', type=int, default=8899)
args = ap.parse_args()
W, H = map(int, args.size.split('x'))
SS = args.ss
RW, RH = int(W * SS), int(H * SS)
opts = json.loads(args.opts)
os.makedirs(args.out, exist_ok=True)


def save(data_url, path, alpha):
    raw = base64.b64decode(data_url.split(',', 1)[1])
    im = Image.open(io.BytesIO(raw))
    im = im.convert('RGBA' if alpha else 'RGB')
    if SS != 1:
        im = im.resize((W, H), Image.LANCZOS)
    im.save(path)


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width': 400, 'height': 300})
        pg.on('console', lambda m: print('console:', m.text) if m.type in ('error', 'warning') else None)
        pg.on('pageerror', lambda e: print('pageerror:', e))
        await pg.goto(f'http://localhost:{args.port}/render.html')
        await pg.wait_for_function('window.RENDER && window.RENDER.ready')
        t = time.time()
        stats = await pg.evaluate('(o) => RENDER.init(o)', {'url': args.model, 'width': RW, 'height': RH, 'upAxis': opts.get('upAxis', 'y'), 'hide': opts.get('hide', []), 'simplifyRollers': opts.get('simplifyRollers', False), 'minPart': opts.get('minPart', 0), 'srgbColors': opts.get('srgbColors', False), 'merge': opts.get('merge', False), 'exposure': opts.get('exposure', 1.0)})
        print('loaded', stats, f'{time.time() - t:.1f}s')
        modes = args.modes.split(',')
        if 'beauty' in modes:
            await pg.evaluate('(o) => RENDER.setupBeauty(o)', opts.get('beauty', {}))
        if 'skeleton' in modes:
            so = dict(opts.get('skeleton', {})); so.update({'width': RW, 'height': RH})
            print('skeleton', await pg.evaluate('(o) => RENDER.setupSkeleton(o)', so))
        lo = dict(opts.get('skeletonLight', {})); lo.update({'width': RW, 'height': RH})
        print('skeleton-light', await pg.evaluate('(o) => RENDER.setupSkeletonLight(o)', lo))
        cam = dict(opts.get('camera', {})); cam.update({'width': RW, 'height': RH})

        async def shot(az, tag):
            c = dict(cam); c['az'] = az
            await pg.evaluate('(c) => RENDER.setCamera(c)', c)
            if 'beauty' in modes:
                await pg.evaluate('(az) => RENDER.orbitLights(az)', az)
                url = await pg.evaluate("() => RENDER.render('beauty')")
                save(url, os.path.join(args.out, f'{tag}-render.png'), True)
            if 'skeleton' in modes:
                url = await pg.evaluate("() => RENDER.render('skeleton')")
                save(url, os.path.join(args.out, f'{tag}-cad.png'), False)

        t = time.time()
        await shot(args.hero_az, 'hero')
        url = await pg.evaluate("() => RENDER.render('skeleton-light')")
        save(url, os.path.join(args.out, 'hero-cadlight.png'), True)
        print('hero done', f'{time.time() - t:.1f}s')
        for i in range(args.frames):
            az = args.start_az + i * 360 / args.frames
            await shot(az, f'f{i:03d}')
            if i % 10 == 0:
                print('frame', i, f'{time.time() - t:.1f}s', flush=True)
        await b.close()

asyncio.run(main())
