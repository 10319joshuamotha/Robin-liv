"""Robin v1 runtime contract.

This module is deliberately dependency-light. It is the single state contract that
PC UI, voice input, animation and a future Android client can share. It does not
perform privileged actions itself; callers must pass through the existing policy.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from threading import RLock
from time import monotonic

from core.robin_policy import Capability, RobinPolicy


class RuntimeMode(str, Enum):
    SLEEPING = "sleeping"
    LISTENING = "listening"
    THINKING = "thinking"
    SPEAKING = "speaking"
    WORKING = "working"
    IDLE = "idle"
    PRIVATE = "private"


@dataclass(frozen=True)
class RuntimeSnapshot:
    mode: RuntimeMode
    animation_enabled: bool
    authenticated: bool
    pc_sleeping: bool
    phone_private: bool
    active_task: str | None
    changed_at: float


class RobinRuntime:
    """Thread-safe state machine for Robin's first integrated runtime."""

    def __init__(self, policy: RobinPolicy | None = None) -> None:
        self.policy = policy or RobinPolicy()
        self._lock = RLock()
        self._mode = RuntimeMode.IDLE
        self._animation_enabled = True
        self._authenticated = False
        self._pc_sleeping = False
        self._phone_private = False
        self._active_task: str | None = None
        self._changed_at = monotonic()

    def _touch(self) -> None:
        self._changed_at = monotonic()

    def snapshot(self) -> RuntimeSnapshot:
        with self._lock:
            return RuntimeSnapshot(
                self._mode,
                self._animation_enabled,
                self._authenticated,
                self._pc_sleeping,
                self._phone_private,
                self._active_task,
                self._changed_at,
            )

    def authenticate(self) -> None:
        with self._lock:
            self._authenticated = True
            if self._mode is RuntimeMode.SLEEPING and not self._pc_sleeping:
                self._mode = RuntimeMode.IDLE
            self._touch()

    def deauthenticate(self) -> None:
        with self._lock:
            self._authenticated = False
            self._active_task = None
            self._mode = RuntimeMode.SLEEPING
            self._touch()

    def sleep_pc(self) -> None:
        with self._lock:
            self._pc_sleeping = True
            self._active_task = None
            self._mode = RuntimeMode.SLEEPING
            self._touch()

    def wake_pc(self) -> None:
        with self._lock:
            self._pc_sleeping = False
            if self._authenticated:
                self._mode = RuntimeMode.IDLE
            self._touch()

    def set_phone_private(self, enabled: bool) -> None:
        with self._lock:
            self._phone_private = bool(enabled)
            if enabled:
                self._mode = RuntimeMode.PRIVATE
            elif not self._pc_sleeping:
                self._mode = RuntimeMode.IDLE
            self._touch()

    def set_animation(self, enabled: bool) -> None:
        with self._lock:
            self._animation_enabled = bool(enabled)
            self._touch()

    def set_mode(self, mode: RuntimeMode) -> None:
        with self._lock:
            if self._pc_sleeping and mode is not RuntimeMode.SLEEPING:
                return
            if self._phone_private and mode not in {RuntimeMode.PRIVATE, RuntimeMode.SLEEPING}:
                return
            self._mode = mode
            self._touch()

    def begin_task(self, task: str) -> None:
        task = task.strip()
        if not task:
            raise ValueError("task must not be empty")
        with self._lock:
            if self._pc_sleeping or self._phone_private:
                raise PermissionError("Robin is not available in the current privacy/sleep state.")
            self._active_task = task
            self._mode = RuntimeMode.WORKING
            self._touch()

    def end_task(self) -> None:
        with self._lock:
            self._active_task = None
            if not self._pc_sleeping:
                self._mode = RuntimeMode.IDLE
            self._touch()

    def authorize(self, capability: Capability, *, confirmed: bool = False,
                  multi_step_verified: bool = False,
                  explicit_media_grant: bool = False):
        with self._lock:
            return self.policy.decide(
                capability,
                authenticated=self._authenticated,
                confirmed=confirmed,
                multi_step_verified=multi_step_verified,
                private_mode=self._phone_private,
                explicit_media_grant=explicit_media_grant,
            )


runtime = RobinRuntime()
