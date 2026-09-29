"""Resource-aware defaults for Robin on modest Windows PCs and phones."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PerformanceProfile:
    animation_fps: int = 30
    idle_poll_interval_s: float = 2.0
    screen_polling: bool = False
    background_workers: int = 2
    max_memory_mb: int = 512
    pause_animation_when_hidden: bool = True


def for_desktop(*, ram_gb: float, gpu_memory_gb: float) -> PerformanceProfile:
    """Choose conservative defaults without assuming a discrete GPU is usable."""
    if ram_gb <= 8 or gpu_memory_gb <= 2:
        return PerformanceProfile(animation_fps=24, idle_poll_interval_s=3.0,
                                  background_workers=1, max_memory_mb=384)
    if ram_gb <= 16:
        return PerformanceProfile(animation_fps=30, idle_poll_interval_s=2.0,
                                  background_workers=2, max_memory_mb=512)
    return PerformanceProfile(animation_fps=45, idle_poll_interval_s=1.5,
                              background_workers=3, max_memory_mb=768)
