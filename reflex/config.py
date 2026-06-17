"""Tunable detection parameters (vision only)."""

from dataclasses import dataclass, field

import numpy as np


@dataclass
class ColorBlobConfig:
    """HSV/BGR color range + blob size filter for compact UI indicators."""

    # Example: bright red UI dot — BGR for OpenCV
    target_bgr: np.ndarray = field(
        default_factory=lambda: np.array([14, 17, 203], dtype=np.uint8)
    )
    tolerance: int = 35
    min_pixels: int = 50
    blob_min_area: float = 25
    blob_max_area: float = 900


@dataclass
class TemplateMatchConfig:
    """Multi-scale template matching for small HUD chips / key prompts."""

    threshold: float = 0.65
    scales: tuple[float, ...] = (
        0.75, 0.8, 0.85, 0.9, 0.95, 1.0, 1.05, 1.1, 1.15, 1.2, 1.25,
    )
