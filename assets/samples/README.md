# Sample assets for vision reflex demos

Static screenshots and a cropped UI template used by `examples/demo_on_samples.py`.

| File | Description |
|------|-------------|
| `combat_scene.png` | Wide combat frame — used to test color-blob timing indicator detection |
| `break_defence_scene.png` | Frame showing a shield / break-defence style UI prompt |
| `ui_chip_template.png` | Small cropped HUD chip for multi-scale `cv2.matchTemplate` |

## Creating your own template

1. Capture a screenshot at your target resolution.
2. Crop **only** the unique UI element (avoid extra background when possible).
3. Save as PNG; point `ReflexEngine(template_path=...)` at the file.
4. Tune `TemplateMatchConfig.threshold` (typical range 0.62–0.75).

These images are illustrative samples for computer-vision experiments only.
