"""Privacy-first perception/context facade for Robin.

Inspired by the layered/spatial architecture of God's Eye View, adapted for
Robin's local assistant. It exposes deterministic context layers while keeping
screen/selection data disabled during Private Mode or PC Sleep.
"""
from __future__ import annotations

import platform
import time
from dataclasses import asdict, dataclass

from core.spatial_context import spatial_context


@dataclass(frozen=True)
class PerceptionSnapshot:
    timestamp: float
    platform: str
    hostname: str
    screen_access_allowed: bool
    private_mode: bool
    sleep_mode: bool
    usb_knowledge_available: bool
    layers: tuple[str, ...]

    def to_dict(self) -> dict:
        return asdict(self)


def snapshot(*, private_mode: bool = False, sleep_mode: bool = False,
             usb_knowledge_available: bool = False) -> PerceptionSnapshot:
    """Return local context state and synchronise the GEV-style context store."""
    spatial_context.set_privacy(private_mode=private_mode, sleeping=sleep_mode)
    spatial_context.set_layer(
        "knowledge",
        [{"available": bool(usb_knowledge_available)}],
        enabled=bool(usb_knowledge_available) and not sleep_mode,
    )
    s = spatial_context.snapshot()
    return PerceptionSnapshot(
        timestamp=time.time(),
        platform=platform.platform(),
        hostname=platform.node(),
        screen_access_allowed=not private_mode and not sleep_mode,
        private_mode=private_mode,
        sleep_mode=sleep_mode,
        usb_knowledge_available=usb_knowledge_available,
        layers=tuple(s["layers"].keys()),
    )


def allowed_layers(s: PerceptionSnapshot) -> tuple[str, ...]:
    """Return which perception layers Robin may use for this snapshot."""
    layers = ["system"]
    if s.usb_knowledge_available and not s.sleep_mode:
        layers.append("knowledge")
    if s.screen_access_allowed:
        layers.append("screen")
    return tuple(layers)


def context_snapshot() -> dict:
    """Return the current layered context for tool/model consumers."""
    return spatial_context.snapshot()


def context_prompt() -> str:
    """Return a compact observation-only context block for the assistant."""
    return spatial_context.prompt_context()
