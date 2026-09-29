"""State-to-animation mapping for Robin's desktop character."""
from __future__ import annotations

from enum import Enum


class AnimationState(str, Enum):
    IDLE = "idle"
    LISTENING = "listening"
    THINKING = "thinking"
    SPEAKING = "speaking"
    EXECUTING = "executing"
    SUCCESS = "success"
    ERROR = "error"
    SLEEPING = "sleeping"
    CALLING = "calling"
    HIDDEN = "hidden"


class AnimationController:
    """Small deterministic presentation state machine.

    Rendering is intentionally separate from this controller so the same states
    can later drive a 2D Qt renderer, a phone UI, or another supported client.
    """

    def __init__(self) -> None:
        self.enabled = True
        self.state = AnimationState.IDLE
        self.task: str | None = None

    def set_enabled(self, enabled: bool) -> AnimationState:
        self.enabled = bool(enabled)
        self.state = AnimationState.IDLE if self.enabled else AnimationState.HIDDEN
        return self.state

    def set_state(self, state: AnimationState, task: str | None = None) -> AnimationState:
        if not self.enabled and state is not AnimationState.SLEEPING:
            self.state = AnimationState.HIDDEN
            return self.state
        self.state = state
        self.task = task
        return state

    def begin_task(self, description: str) -> AnimationState:
        return self.set_state(AnimationState.EXECUTING, description)

    def complete(self, success: bool) -> AnimationState:
        return self.set_state(AnimationState.SUCCESS if success else AnimationState.ERROR)
