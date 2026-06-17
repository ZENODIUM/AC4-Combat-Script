# Detection approaches & lessons learned

This document describes the vision techniques used in `reflex/` and how they fit
into a larger reflex + planning stack. It is written for **perception and integration**
— not for automating third-party games.

## Problem shape

Fast combat UIs often show **brief, high-contrast prompts**:

- A **saturated color indicator** (small circle) — good for color + blob filtering.
- A **HUD chip / key hint** (gray icon on dark box) — good for template matching.

A reflex module must:

1. Scan a **cropped region** frequently (~10 ms).
2. Emit a **signal** when confidence is high enough.
3. Let a **separate policy** choose actions and rate limits.

## Approach A — Color range + blob area

### Steps

1. Convert frame to BGR mask with `cv2.inRange(lower, upper)`.
2. Count matching pixels; ignore if below `min_pixels`.
3. `findContours` → measure `contourArea`.
4. Accept blobs in `[blob_min_area, blob_max_area]`.

### Why blob filtering?

Raw pixel counts fire on uniforms, blood, and large red UI blocks. The counter-style
icon is a **compact** blob (~25–900 px² at 1080p). Area constraints reject scatter.

### Tuning

| Knob | Effect |
|------|--------|
| `tolerance` | Wider = more hits, more false positives |
| `min_pixels` | Floor on total red noise |
| `blob_min_area` / `blob_max_area` | Size gate for icon vs background |

## Approach B — Multi-scale template matching

### Steps

1. Load grayscale template PNG (cropped HUD chip).
2. For each scale in `0.75 … 1.25`, resize template and `matchTemplate`.
3. Take max confidence (`TM_CCOEFF_NORMED`, 0–1).
4. Fire if `confidence >= threshold`.

### Why multi-scale?

Snipping Tool crops are 1:1 pixels, but in-game scale can differ slightly. Trying
several scales avoids a single-size mismatch.

### Tuning

| Symptom | Fix |
|---------|-----|
| Never fires | Lower threshold (0.62–0.65); verify template size |
| False fires | Raise threshold; tighten crop; require 2-of-3 scans |
| Score 0.6–0.64 with prompt visible | Threshold too high |
| Score 0.65+ without prompt | Threshold too low or template too generic |

### Template capture tips

- Crop at **native play resolution**; do not resize after crop.
- Include minimal background; black boxes over scenery reduce match stability.
- Viewer “zoom” when opening PNG is **not** the same as resizing the file.

## Scan vs action timing

Separate **perception rate** from **action rate**:

| Loop | Typical interval | Role |
|------|------------------|------|
| Vision scan | ~0.01 s | Catch short prompts |
| Default action | ~0.33 s | Avoid input flood / dropped events |

The public `ReflexEngine` only analyzes frames. A planner applies cooldowns and
priority (e.g. Prompt A before Prompt B before default behavior).

## Capture region (`mss`)

Only scan a center combat band — not the full screen:

```python
CAPTURE_REGION = {"top": 0, "left": 192, "width": 1536, "height": 810}  # 1920×1080 example
```

Tune by saving one debug frame and confirming prompts sit inside the crop.

## Integration sketch

```python
analysis = engine.analyze(frame_bgr)

if analysis.primary == ReflexKind.TIMING_PROMPT_A:
    planner.enqueue("counter_window")  # your policy — not in this repo
elif analysis.primary == ReflexKind.TIMING_PROMPT_B:
    planner.enqueue("break_window")
else:
    planner.enqueue("idle_attack")  # or no-op
```

## What we intentionally omit from the public repo

- OS input injection (`SendInput`, synthetic clicks)
- Game-specific main loops and hotkey bots
- Publisher-trademarked automation scripts

Those belong in private integration layers under `private/` (gitignored) if you
experiment locally — not in a public GitHub tree.

## Sample assets

See [`assets/samples/README.md`](../assets/samples/README.md) for the bundled PNGs
used by `examples/demo_on_samples.py`.
