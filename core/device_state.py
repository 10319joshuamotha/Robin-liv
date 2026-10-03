"""Device-scoped operating state and capability gates for Robin."""
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
    screen_capture: bool
    microphone_processing: bool
    camera_capture: bool
    assistant_processing: bool
    keyboard_wake: bool


class DeviceStateController:
    """Thread-safe state machine whose capability snapshot is deny-by-default."""

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

        # PC sleep is a hard stop. Only the physical ESC wake path remains alive.
        if self.device is DeviceKind.PC and state is DeviceState.SLEEPING:
            return CapabilitySnapshot(False, False, False, False, True)

        # Phone Private Mode blocks screen-derived access. Physical camera use is
        # not screen access; gallery/media authorization is enforced separately.
        if self.device is DeviceKind.PHONE and state is DeviceState.PRIVATE:
            return CapabilitySnapshot(False, True, True, True, False)

        return CapabilitySnapshot(True, True, True, True, False)

    def allows(self, capability: str) -> bool:
        caps = self.capabilities()
        allowed = {
            "screen_capture": caps.screen_capture,
            "screen_view": caps.screen_capture,
            "screen_monitoring": caps.screen_capture,
            "microphone_processing": caps.microphone_processing,
            "camera_capture": caps.camera_capture,
            "assistant_processing": caps.assistant_processing,
            "keyboard_wake": caps.keyboard_wake,
        }
        return bool(allowed.get(capability, False))


# Shared controllers make capability gates consistent across action modules.
_pc_controller = DeviceStateController(DeviceKind.PC)
_phone_controller = DeviceStateController(DeviceKind.PHONE)


def get_device_controller(device: DeviceKind) -> DeviceStateController:
    return _pc_controller if device is DeviceKind.PC else _phone_controller


def get_pc_controller() -> DeviceStateController:
    return _pc_controller


def get_phone_controller() -> DeviceStateController:
    return _phone_controller
