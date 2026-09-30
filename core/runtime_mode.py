"""Runtime mode selection for Robin's online/offline providers."""
from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class RuntimeMode:
    brain: str
    voice: str
    offline: bool


def get_runtime_mode() -> RuntimeMode:
    """Read explicit environment configuration without touching the network.

    Online Gemini remains the safe default because Robin's established realtime
    microphone/audio runtime is Gemini Live. Local/offline mode is opt-in until
    the complete local STT/TTS audio path is wired and tested on the target PC.
    """
    brain = os.getenv("ROBIN_BRAIN", "online").strip().lower()
    voice = os.getenv("ROBIN_VOICE", "online").strip().lower()
    if brain not in {"local", "ollama", "online", "gemini"}:
        brain = "online"
    if voice not in {"local", "offline", "online", "gemini"}:
        voice = "online"
    offline = brain in {"local", "ollama"} and voice in {"local", "offline"}
    return RuntimeMode(brain=brain, voice=voice, offline=offline)


def describe_runtime() -> str:
    mode = get_runtime_mode()
    return f"brain={mode.brain}; voice={mode.voice}; offline={'yes' if mode.offline else 'no'}"
