# Robot images

These scripts make the robot images on the home page:

- **Hero**: a real photo of Eclipse from the Meet One pits (background removed), and the Onshape CAD rendered from the *same camera angle*, so the CAD lines up with the photo under the cursor.
- **Turntable**: 48 frames of the CAD turning 360° for the scroll section.

## 1. Export the CAD

In Onshape, right-click the **Assembly 1** tab → **Export** → **glTF**, and save it in this folder as `robot.glb`.

## 2. Install

```bash
cd tools/robot-render
npm install
pip install playwright pillow numpy opencv-python-headless rembg onnxruntime
python3 -m playwright install chromium
```

## 3. Shrink the model

The export is huge (each mecanum roller is ~800k triangles). This keeps every part, including the rollers, but cuts the triangle count:

```bash
node decimate.mjs robot.glb robot-d.glb 8000 1200
```

## 4. Render and build

```bash
python3 -m http.server 8899 &
python3 render_cad.py hero robot-d.glb out
python3 render_cad.py spin robot-d.glb out
python3 make_hero.py ../../public/assets/meet1-robot-workbench.webp out ../../public/assets/robot
python3 make_spin.py out ../../public/assets/robot
```

`hero_camera.json` is the camera that matches the photo. It was found by matching points on the drivetrain plate, pulleys, shooter and intake between the photo and the CAD, then fine-tuned by lining up edges. If you swap in a different photo, that camera has to be found again.

`robot.glb`, `robot-d.glb`, `out/` and `node_modules/` are ignored by git.
