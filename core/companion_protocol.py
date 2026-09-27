"""Companion task protocol shared by Robin's Windows host and future Android app.

This module deliberately contains no cloud SDK and performs no phone actions.
It defines the device-neutral contract so local LAN transport and a future
cloud relay can carry the same tasks.

Execution rule:
    local Android/Windows capability first when the target device is reachable;
    cloud relay only transports/synchronizes the task when direct connectivity
    is unavailable.

The Android native app will map PHONE_* capabilities to Android APIs such as
Contacts, AlarmManager, notifications, and Telecom/Intent-based calling.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any
import time
import uuid


class Device(str, Enum):
    WINDOWS = "windows"
    ANDROID = "android"


class Transport(str, Enum):
    LOCAL = "local"
    CLOUD = "cloud"


class Capability(str, Enum):
    WINDOWS_TASK = "windows.task"
    PHONE_CALL = "phone.call"
    PHONE_MESSAGE = "phone.message"
    PHONE_ALARM = "phone.alarm"
    PHONE_REMINDER = "phone.reminder"
    PHONE_NOTIFICATION = "phone.notification"
    PHONE_CONTACTS = "phone.contacts"
    PHONE_VOICE = "phone.voice"


@dataclass
class CompanionTask:
    """A transport-neutral request that can be executed by a device."""

    capability: Capability
    target: Device
    payload: dict[str, Any] = field(default_factory=dict)
    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: float = field(default_factory=time.time)
    expires_at: float | None = None
    requires_confirmation: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "capability": self.capability.value,
            "target": self.target.value,
            "payload": self.payload,
            "created_at": self.created_at,
            "expires_at": self.expires_at,
            "requires_confirmation": self.requires_confirmation,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CompanionTask":
        return cls(
            task_id=str(data["task_id"]),
            capability=Capability(data["capability"]),
            target=Device(data["target"]),
            payload=dict(data.get("payload") or {}),
            created_at=float(data.get("created_at", time.time())),
            expires_at=(
                float(data["expires_at"])
                if data.get("expires_at") is not None else None
            ),
            requires_confirmation=bool(data.get("requires_confirmation", False)),
        )


@dataclass
class TaskResult:
    task_id: str
    ok: bool
    message: str = ""
    data: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "ok": self.ok,
            "message": self.message,
            "data": self.data,
        }


def make_call_task(contact: str, *, confirm: bool = True) -> CompanionTask:
    """Create a phone-call request without placing the call."""
    return CompanionTask(
        capability=Capability.PHONE_CALL,
        target=Device.ANDROID,
        payload={"contact": contact},
        requires_confirmation=confirm,
    )


def make_alarm_task(hour: int, minute: int, *, label: str = "Robin") -> CompanionTask:
    """Create a phone alarm request without touching Android APIs."""
    if not 0 <= hour <= 23 or not 0 <= minute <= 59:
        raise ValueError("hour must be 0-23 and minute must be 0-59")
    return CompanionTask(
        capability=Capability.PHONE_ALARM,
        target=Device.ANDROID,
        payload={"hour": hour, "minute": minute, "label": label},
    )


def choose_transport(*, android_reachable_locally: bool) -> Transport:
    """Prefer direct local transport; fall back to cloud relay when needed."""
    return Transport.LOCAL if android_reachable_locally else Transport.CLOUD
