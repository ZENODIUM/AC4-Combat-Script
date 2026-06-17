"""Structured outputs for a higher-level decision / action planner."""

from dataclasses import dataclass, field
from enum import Enum


class ReflexKind(str, Enum):
    """Detected UI prompt categories (labels only — no game actions implied)."""

    NONE = "none"
    TIMING_PROMPT_A = "timing_prompt_a"  # e.g. color-blob timing indicator
    TIMING_PROMPT_B = "timing_prompt_b"  # e.g. template-matched UI chip


@dataclass
class PromptHit:
    kind: ReflexKind
    confidence: float
    detail: dict = field(default_factory=dict)


@dataclass
class FrameAnalysis:
    """Result of analyzing one BGR frame."""

    primary: ReflexKind = ReflexKind.NONE
    hits: list[PromptHit] = field(default_factory=list)
    metrics: dict = field(default_factory=dict)

    @property
    def has_signal(self) -> bool:
        return self.primary != ReflexKind.NONE
