"""Analyze frames and emit reflex signals for a downstream decision layer."""

from pathlib import Path

import cv2

from reflex.config import ColorBlobConfig, TemplateMatchConfig
from reflex.detectors import (
    build_color_mask,
    find_color_blob,
    load_template_grayscale,
    template_match_confidence,
)
from reflex.signals import FrameAnalysis, PromptHit, ReflexKind


class ReflexEngine:
    """
    Vision-only reflex analyzer.

    Intended as a fast perception submodule inside a larger agent:
      capture → ReflexEngine.analyze() → planner → (your action policy)

    This repo does NOT implement action policies or OS input injection.
    """

    def __init__(
        self,
        color_cfg: ColorBlobConfig | None = None,
        template_cfg: TemplateMatchConfig | None = None,
        template_path: Path | None = None,
        enable_template: bool = True,
    ) -> None:
        self.color_cfg = color_cfg or ColorBlobConfig()
        self.template_cfg = template_cfg or TemplateMatchConfig()
        self.enable_template = enable_template and template_path is not None
        self._template_gray = (
            load_template_grayscale(template_path) if self.enable_template else None
        )

    def analyze(self, frame_bgr) -> FrameAnalysis:
        mask = build_color_mask(frame_bgr, self.color_cfg)
        red_pixels = int(cv2.countNonZero(mask))
        blob_area = find_color_blob(mask, self.color_cfg)

        hits: list[PromptHit] = []
        primary = ReflexKind.NONE

        if blob_area is not None:
            hit = PromptHit(
                kind=ReflexKind.TIMING_PROMPT_A,
                confidence=1.0,
                detail={"blob_area": blob_area, "red_pixels": red_pixels},
            )
            hits.append(hit)
            primary = ReflexKind.TIMING_PROMPT_A

        template_score = 0.0
        if self.enable_template and self._template_gray is not None:
            template_score = template_match_confidence(
                frame_bgr, self._template_gray, self.template_cfg
            )
            if template_score >= self.template_cfg.threshold:
                hit = PromptHit(
                    kind=ReflexKind.TIMING_PROMPT_B,
                    confidence=template_score,
                    detail={"method": "template_match"},
                )
                hits.append(hit)
                if primary == ReflexKind.NONE:
                    primary = ReflexKind.TIMING_PROMPT_B

        return FrameAnalysis(
            primary=primary,
            hits=hits,
            metrics={
                "red_pixels": red_pixels,
                "template_confidence": template_score,
            },
        )
