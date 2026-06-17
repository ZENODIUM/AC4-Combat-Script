"""
Live screen-region preview: prints reflex signals only.

No keyboard/mouse injection. Use for tuning capture regions and thresholds
before wiring signals into your own decision layer.

Requires: pip install mss
"""

import sys
import time
from pathlib import Path

import cv2
import mss
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from reflex import ReflexEngine

# Adjust to your monitor / window (pixels). Example: center band @ 1920x1080.
CAPTURE_REGION = {"top": 0, "left": 192, "width": 1536, "height": 810}

TEMPLATE = ROOT / "assets" / "samples" / "ui_chip_template.png"


def main() -> None:
    engine = ReflexEngine(template_path=TEMPLATE, enable_template=True)
    print("Live signal preview (Ctrl+C to stop). No inputs are sent.")
    print(f"Region: {CAPTURE_REGION}")

    with mss.mss() as sct:
        while True:
            shot = sct.grab(CAPTURE_REGION)
            frame_bgr = cv2.cvtColor(np.array(shot), cv2.COLOR_BGRA2BGR)
            result = engine.analyze(frame_bgr)

            if result.has_signal:
                print(
                    f"[SIGNAL] {result.primary.value}  "
                    f"template={result.metrics.get('template_confidence', 0):.2f}  "
                    f"red_px={result.metrics.get('red_pixels', 0)}"
                )

            time.sleep(0.1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nStopped.")
