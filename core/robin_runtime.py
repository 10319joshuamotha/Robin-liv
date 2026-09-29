"""Single runtime coordinator for Robin's device state and presentation state.

The coordinator is intentionally small: existing Gemini/audio/tool systems remain
responsible for transport and execution, while this object provides one place to
apply sleep/private/animation policy consistently.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from threading import RLock

from .animation_state import AnimationController, AnimationState
from .device_state import DeviceKind, DeviceState, DeviceStateController


class RuntimeEvent(str, Enum):
    LISTEN = "listen"
    THINK = "think"
    SPEAK = "speak"
    TASK = "task"
    SUCCESS = "success"
    ERROR = "error"
    SLEEP = "sleep"
    WAKE = "wake"
    PRIVATE_ON = "private_on"
    PRIVATE_OFF = "private_off"
    ANIMATION_ON = "animation_on"
    ANIMATION_OFF = "animation_off"


@dataclass(frozen=True)
class RuntimeSnapshot:
    device: DeviceKind
    device_state: DeviceState
    animation: AnimationState
    animation_enabled: bool
    task: str | None


class RobinRuntime:
    """Coordinates device state and character state without owning I/O."""

    def __init__(self, device: DeviceKind) -> None:
        self._lock = RLock()
        self.device = DeviceStateController(device)
        self.animation = AnimationController()

    def apply(self, event: RuntimeEvent, task: str | None = None) -> RuntimeSnapshot:
        with self._lock:
            if event is RuntimeEvent.SLEEP:
                if self.device.device is not DeviceKind.PC:
                    raise RuntimeError("sleep event is only valid for PC runtime")
                self.device.sleep_pc()
                self.animation.set_state(AnimationState.SLEEPING)
            elif event is RuntimeEvent.WAKE:
                if self.device.device is not DeviceKind.PC:
                    raise RuntimeError("wake event is only valid for PC runtime")
                self.device.wake_pc()
                if self.animation.enabled:
                    self.animation.set_state(AnimationState.LISTENING)
            elif event is RuntimeEvent.PRIVATE_ON:
                if self.device.device is not DeviceKind.PHONE:
                    raise RuntimeError("private mode is only valid for phone runtime")
                self.device.set_private_mode(True)
            elif event is RuntimeEvent.PRIVATE_OFF:
                if self.device.device is not DeviceKind.PHONE:
                    raise RuntimeError("private mode is only valid for phone runtime")
                self.device.set_private_mode(False)
            elif event is RuntimeEvent.ANIMATION_ON:
                self.animation.set_enabled(True)
            elif event is RuntimeEvent.ANIMATION_OFF:
                self.animation.set_enabled(False)
            elif event is RuntimeEvent.LISTEN:
                self.animation.set_state(AnimationState.LISTENING)
            elif event is RuntimeEvent.THINK:
                self.animation.set_state(AnimationState.THINKING)
            elif event is RuntimeEvent.SPEAK:
                self.animation.set_state(AnimationState.SPEAKING)
            elif event is RuntimeEvent.TASK:
                self.animation.begin_task(task or "working")
            elif event is RuntimeEvent.SUCCESS:
                self.animation.complete(True)
            elif event is RuntimeEvent.ERROR:
                self.animation.complete(False)
            return self.snapshot()

    def snapshot(self) -> RuntimeSnapshot:
        with self._lock:
            return RuntimeSnapshot(
                device=self.device.device,
                device_state=self.device.state,
                animation=self.animation.state,
                animation_enabled=self.animation.enabled,
                task=self.animation.task,
            )

    def allows(self, capability: str) -> bool:
        return self.device.allows(capability)
