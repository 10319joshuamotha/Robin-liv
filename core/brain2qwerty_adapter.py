"""Optional adapter boundary for brain2qwerty-style input research.

This is deliberately an interface only. Brain2Qwerty is a research system for
brain-signal-to-keyboard decoding, not a drop-in speech/voice recognizer.
Robin therefore does not enable or depend on it by default.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DecodedInput:
    text: str
    confidence: float
    source: str = "brain2qwerty"


class Brain2QwertyAdapter:
    """Safe extension point for an externally supplied decoder.

    A concrete decoder must be injected explicitly. No EEG/neural device is
    opened, captured, or uploaded by this adapter.
    """

    def __init__(self, decoder=None):
        self.decoder = decoder

    @property
    def available(self) -> bool:
        return callable(self.decoder)

    def decode(self, signal) -> DecodedInput:
        if not self.available:
            raise RuntimeError("Brain2Qwerty decoder is not installed/configured")
        result = self.decoder(signal)
        if isinstance(result, DecodedInput):
            return result
        if isinstance(result, str):
            return DecodedInput(result, 0.0)
        text = str(getattr(result, "text", result))
        confidence = float(getattr(result, "confidence", 0.0))
        return DecodedInput(text, confidence)
