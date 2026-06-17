"""OpenCV detectors — color blob and template matching."""

from pathlib import Path

import cv2
import numpy as np

from reflex.config import ColorBlobConfig, TemplateMatchConfig


def build_color_mask(frame_bgr: np.ndarray, cfg: ColorBlobConfig) -> np.ndarray:
    lower = np.clip(cfg.target_bgr.astype(np.int16) - cfg.tolerance, 0, 255).astype(np.uint8)
    upper = np.clip(cfg.target_bgr.astype(np.int16) + cfg.tolerance, 0, 255).astype(np.uint8)
    return cv2.inRange(frame_bgr, lower, upper)


def find_color_blob(mask: np.ndarray, cfg: ColorBlobConfig) -> float | None:
    """Return blob area if a compact region matches size constraints."""
    if cv2.countNonZero(mask) < cfg.min_pixels:
        return None

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for contour in contours:
        area = cv2.contourArea(contour)
        if cfg.blob_min_area <= area <= cfg.blob_max_area:
            return area
    return None


def load_template_grayscale(path: Path) -> np.ndarray:
    image = cv2.imread(str(path))
    if image is None:
        raise FileNotFoundError(f"Could not read template image: {path}")
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


def template_match_confidence(
    frame_bgr: np.ndarray, template_gray: np.ndarray, cfg: TemplateMatchConfig
) -> float:
    frame_gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
    frame_h, frame_w = frame_gray.shape[:2]
    template_h, template_w = template_gray.shape[:2]
    best = 0.0

    for scale in cfg.scales:
        scaled_w = max(1, int(template_w * scale))
        scaled_h = max(1, int(template_h * scale))
        if scaled_h > frame_h or scaled_w > frame_w:
            continue

        scaled = (
            template_gray
            if scale == 1.0
            else cv2.resize(template_gray, (scaled_w, scaled_h), interpolation=cv2.INTER_AREA)
        )
        result = cv2.matchTemplate(frame_gray, scaled, cv2.TM_CCOEFF_NORMED)
        best = max(best, float(cv2.minMaxLoc(result)[1]))

    return best
