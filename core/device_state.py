"""Device-scoped operating state and capability gates for Robin.

This module is intentionally independent of the UI, Gemini session, Android
transport, and action registry. It is the foundation for enforcing privacy and
sleep behavior in code rather than relying on model instructions.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from threading import RLock


class DeviceKind(str, Enum):
    PC = "pc"
    PHONE = "phone"


class DeviceState(str, Enum):
    ACTIVE = "active"
    PRIVATE = "private"
    SLEEPING = "sleeping"
    OFFLINE = "offline"


@dataclass(frozen=True)
class CapabilitySnapshot:
    """Capabilities available at one point in time."""

    screen_capture: bool
    microphone_processing: bool
    camera_capture: bool
    assistant_processing: bool
    keyboard_wake: bool


class DeviceStateController:
    """Thread-safe state machine for one Robin device client.

    The controller deliberately exposes capabilities instead of asking callers
    to interpret state strings. This makes it harder for a screen/camera/audio
    feature to accidentally bypass a privacy or sleep restriction.
    """

    def __init__(self, device: DeviceKind, initial: DeviceState | None = None) -> None:
        self.device = device
        self._lock = RLock()
        self._state = initial or DeviceState.ACTIVE

        if self.device is DeviceKind.PC and self._state is DeviceState.PRIVATE:
            raise ValueError("PC devices do not support phone Private Mode")
        if self.device is DeviceKind.PHONE and self._state is DeviceState.SLEEPING:
            raise ValueError("Phone devices do not use the PC sleep state")

    @property
    def state(self) -> DeviceState:
        with self._lock:
            return self._state

    def activate(self) -> DeviceState:
        with self._lock:
            self._state = DeviceState.ACTIVE
            return self._state

    def go_offline(self) -> DeviceState:
        with self._lock:
            self._state = DeviceState.OFFLINE
            return self._state

    def sleep_pc(self) -> DeviceState:
        if self.device is not DeviceKind.PC:
            raise RuntimeError("PC sleep is only valid for the PC device")
        with self._lock:
            self._state = DeviceState.SLEEPING
            return self._state

    def wake_pc(self) -> DeviceState:
        if self.device is not DeviceKind.PC:
            raise RuntimeError("PC wake is only valid for the PC device")
        with self._lock:
            if self._state is DeviceState.SLEEPING:
                self._state = DeviceState.ACTIVE
            return self._state

    def set_private_mode(self, enabled: bool) -> DeviceState:
        if self.device is not DeviceKind.PHONE:
            raise RuntimeError("Private Mode is only valid for the phone device")
        with self._lock:
            self._state = DeviceState.PRIVATE if enabled else DeviceState.ACTIVE
            return self._state

    def capabilities(self) -> CapabilitySnapshot:
        with self._lock:
            state = self._state

        if state is DeviceState.OFFLINE:
            return CapabilitySnapshot(False, False, False, False, False)

        if self.device is DeviceKind.PC and state is DeviceState.SLEEPING:
            return CapabilitySnapshot(
                screen_capture=False,
                microphone_processing=False,
                camera_capture=False,
                assistant_processing=False,
                keyboard_wake=True,
            )

        if self.device is DeviceKind.PHONE and state is DeviceState.PRIVATE:
            return CapabilitySnapshot(
                screen_capture=False,
                microphone_processing=True,
                camera_capture=True,
                assistant_processing=True,
                keyboard_wake=False,
            )

        return CapabilitySnapshot(
            screen_capture=True,
            microphone_processing=True,
            camera_capture=True,
            assistant_processing=True,
            keyboard_wake=False,
        )

    def allows(self, capability: str) -> bool:
        """Return whether a named capability is currently permitted.

        Unknown capabilities are denied instead of being implicitly allowed.
        """

        allowed = {
            "screen_capture": self.capabilities().screen_capture,
            "microphone_processing": self.capabilities().microphone_processing,
            "camera_capture": self.capabilities().camera_capture,
            "assistant_processing": self.capabilities().assistant_processing,
            "keyboard_wake": self.capabilities().keyboard_wake,
        }
        return bool(allowed.get(capability, False))
