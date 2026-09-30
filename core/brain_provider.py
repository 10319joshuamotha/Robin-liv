"""Provider-neutral reasoning interface for Robin.

The runtime can select an offline local provider or the existing Gemini provider.
This module deliberately has no hard dependency on Ollama, so installing Robin
without the local model stack remains possible.
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(frozen=True)
class BrainResponse:
    text: str
    provider: str
    offline: bool
    raw: Any = None


class BrainProvider(Protocol):
    name: str
    offline: bool

    def respond(self, prompt: str, *, system: str = "", context: str = "") -> BrainResponse: ...


class OllamaProvider:
    """Small stdlib-only adapter for a local Ollama server."""

    name = "ollama"
    offline = True

    def __init__(self, model: str | None = None, base_url: str | None = None, timeout: float = 120.0):
        self.model = model or os.getenv("ROBIN_OLLAMA_MODEL", "qwen2.5:7b")
        self.base_url = (base_url or os.getenv("ROBIN_OLLAMA_URL", "http://127.0.0.1:11434")).rstrip("/")
        self.timeout = timeout

    def respond(self, prompt: str, *, system: str = "", context: str = "") -> BrainResponse:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        if context:
            messages.append({"role": "system", "content": context})
        messages.append({"role": "user", "content": prompt})
        payload = json.dumps({"model": self.model, "messages": messages, "stream": False}).encode("utf-8")
        request = urllib.request.Request(
            f"{self.base_url}/api/chat",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                data = json.loads(response.read().decode("utf-8"))
            text = str(data.get("message", {}).get("content", "")).strip()
            if not text:
                raise RuntimeError("Ollama returned an empty response")
            return BrainResponse(text=text, provider=self.name, offline=True, raw=data)
        except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
            raise RuntimeError(f"Local Ollama provider unavailable: {exc}") from exc


def create_brain_provider(mode: str | None = None) -> BrainProvider:
    """Create the configured local provider.

    ``online`` remains supported by the existing GeminiLive implementation in
    main.py; this factory intentionally owns only the provider-independent local
    path so the live runtime can migrate without a second brain implementation.
    """
    selected = (mode or os.getenv("ROBIN_BRAIN", "local")).strip().lower()
    if selected in {"local", "ollama", "offline"}:
        return OllamaProvider()
    raise ValueError(f"Unsupported Robin brain provider: {selected}")
