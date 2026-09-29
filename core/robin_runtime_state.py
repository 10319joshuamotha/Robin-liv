"""Small, dependency-free runtime state shared by Robin clients.

The state object deliberately contains no model, UI, microphone, or network code.
It is therefore safe to reuse from the Windows core and the future native phone
companion. It is also the single place where sleep/private-mode transitions can
be observed by UI and animation layers.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from threading import RLock


class RuntimeMode(str, Enum):
    ACTIVE = "active"
    SLEEPING = "sleeping"
    PHONE_PRIVATE = "phone_private"


class AnimationMode(str, Enum):
    IDLE = "idle"
    LISTENING = "listening"
    THINKING = "thinking"
    SPEAKING = "speaking"
    WORKING = "working"
    SLEEPING = "sleeping"
    HIDDEN = "hidden"


@dataclass
class RobinRuntimeState:
    """Thread-safe state machine for lifecycle and animation coordination."""

    mode: RuntimeMode = RuntimeMode.ACTIVE
    animation: AnimationMode = AnimationMode.IDLE
    current_task: str | None = None
    current_device: str = "pc"
    animation_enabled: bool = True
    _lock: RLock = field(default_factory=RLock, repr=False)

    def sleep(self) -> None:
        with self._lock:
            self.mode = RuntimeMode.SLEEPING
            self.animation = AnimationMode.SLEEPING if self.animation_enabled else AnimationMode.HIDDEN
            self.current_task = None

    def wake(self) -> None:
        with self._lock:
            self.mode = RuntimeMode.ACTIVE
            self.animation = AnimationMode.IDLE if self.animation_enabled else AnimationMode.HIDDEN

    def private_mode_on(self) -> None:
        with self._lock:
            self.mode = RuntimeMode.PHONE_PRIVATE
            self.animation = AnimationMode.HIDDEN
            self.current_task = None

    def private_mode_off(self) -> None:
        with self._lock:
            self.mode = RuntimeMode.ACTIVE
            self.animation = AnimationMode.IDLE if self.animation_enabled else AnimationMode.HIDDEN

    def set_animation_enabled(self, enabled: bool) -> None:
        with self._lock:
            self.animation_enabled = bool(enabled)
            if not enabled:
                self.animation = AnimationMode.HIDDEN
            elif self.mode is RuntimeMode.SLEEPING:
                self.animation = AnimationMode.SLEEPING
            else:
                self.animation = AnimationMode.IDLE

    def set_animation(self, mode: AnimationMode) -> None:
        with self._lock:
            if not self.animation_enabled:
                self.animation = AnimationMode.HIDDEN
                return
            if self.mode is RuntimeMode.SLEEPING:
                self.animation = AnimationMode.SLEEPING
                return
            if self.mode is RuntimeMode.PHONE_PRIVATE:
                self.animation = AnimationMode.HIDDEN
                return
            self.animation = mode

    def begin_task(self, description: str) -> None:
        with self._lock:
            if self.mode is not RuntimeMode.ACTIVE:
                return
            self.current_task = description.strip() or "working"
            self.animation = AnimationMode.WORKING if self.animation_enabled else AnimationMode.HIDDEN

    def end_task(self) -> None:
        with self._lock:
            self.current_task = None
            if self.mode is RuntimeMode.SLEEPING:
                self.animation = AnimationMode.SLEEPING
            elif self.mode is RuntimeMode.PHONE_PRIVATE or not self.animation_enabled:
                self.animation = AnimationMode.HIDDEN
            else:
                self.animation = AnimationMode.IDLE

    def snapshot(self) -> dict:
        with self._lock:
            return {
                "mode": self.mode.value,
                "animation": self.animation.value,
                "current_task": self.current_task,
                "current_device": self.current_device,
                "animation_enabled": self.animation_enabled,
            }


STATE = RobinRuntimeState()
