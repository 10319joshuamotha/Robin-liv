"""Privacy-first situational context for Robin.

Inspired by the layered/spatial presentation ideas in God's Eye View, but
restricted to local device context. This module does NOT perform person search,
face recognition, or individual tracking, and it does not upload captured data.
"""
from __future__ import annotations

import os
import platform
import time
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class PerceptionSnapshot:
    timestamp: float
    platform: str
    hostname: str
    screen_access_allowed: bool
    private_mode: bool
    sleep_mode: bool
    usb_knowledge_available: bool

    def to_dict(self) -> dict:
        return asdict(self)


def snapshot(*, private_mode: bool = False, sleep_mode: bool = False,
             usb_knowledge_available: bool = False) -> PerceptionSnapshot:
    """Return a minimal local context snapshot.

    The snapshot intentionally contains no screenshot, camera frame, GPS
    coordinate, biometric data, or person-identifying information.
    """
    return PerceptionSnapshot(
        timestamp=time.time(),
        platform=platform.platform(),
        hostname=platform.node(),
        screen_access_allowed=not private_mode and not sleep_mode,
        private_mode=private_mode,
        sleep_mode=sleep_mode,
        usb_knowledge_available=usb_knowledge_available,
    )


def allowed_layers(s: PerceptionSnapshot) -> tuple[str, ...]:
    """Return which perception layers Robin may use for this snapshot."""
    layers = ["system"]
    if s.usb_knowledge_available and not s.sleep_mode:
        layers.append("knowledge")
    if s.screen_access_allowed:
        layers.append("screen")
    return tuple(layers)
