"""Run reflex detection on bundled sample screenshots (no live capture, no inputs)."""

import sys
from pathlib import Path

import cv2

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from reflex import ReflexEngine

SAMPLES = ROOT / "assets" / "samples"


def analyze_image(engine: ReflexEngine, path: Path) -> None:
    frame = cv2.imread(str(path))
    if frame is None:
        print(f"SKIP  {path.name} (could not read)")
        return

    result = engine.analyze(frame)
    print(f"\n{path.name}")
    print(f"  primary signal : {result.primary.value}")
    print(f"  red_pixels     : {result.metrics.get('red_pixels', 0)}")
    print(f"  template score : {result.metrics.get('template_confidence', 0):.2f}")
    for hit in result.hits:
        print(f"  hit            : {hit.kind.value}  detail={hit.detail}")


def main() -> None:
    template = SAMPLES / "ui_chip_template.png"
    engine = ReflexEngine(template_path=template, enable_template=True)

    print("Vision reflex demo — static sample images only")
    print("=" * 50)

    for name in ("combat_scene.png", "break_defence_scene.png"):
        analyze_image(engine, SAMPLES / name)


if __name__ == "__main__":
    main()
