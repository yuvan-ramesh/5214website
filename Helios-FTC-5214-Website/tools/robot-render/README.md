# Robot renders

These scripts turn our Onshape CAD into the robot images on the website:
a rendered robot, a matching CAD "skeleton" from the same camera, a line drawing, and 48-frame turntables of both.

## 1. Export the CAD

In Onshape, right-click the **Assembly 1** tab → **Export** → format **glTF** → save the file into this folder as `robot.glb` (or `robot.gltf`).

## 2. Install

```bash
cd tools/robot-render
npm install                                   # three.js
pip install playwright pillow
python3 -m playwright install chromium
```

## 3. Render

```bash
python3 -m http.server 8899 &                 # serve this folder for the renderer
python3 drive.py robot.glb out --frames 48 --size 1280x800 --ss 1 --opts "$(cat robot_opts.json)"
python3 make_assets.py out ../../public/assets/robot
```

`drive.py` renders `hero-render.png`, `hero-cad.png`, `hero-cadlight.png` and the turntable frames into `out/`.
`robot_opts.json` holds the settings used for the site (Z-up, simplified mecanum rollers, small screws and nuts left out, lighting and camera). The hero images were rendered separately at `--size 1600x1000 --ss 1.5 --frames 0`.
`make_assets.py` converts them to the WebP files the site loads. Large files (`robot.glb`, `out/`, `node_modules/`) are ignored by git.
