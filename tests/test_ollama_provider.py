from __future__ import annotations

import json
from unittest.mock import patch

from core.brain_provider import OllamaProvider, create_brain_provider


class _Response:
    def __init__(self, payload: dict):
        self.payload = json.dumps(payload).encode()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return self.payload


def test_ollama_provider_builds_chat_request():
    provider = OllamaProvider(model="qwen2.5:7b", base_url="http://127.0.0.1:11434")
    payload = {"message": {"content": "OLLAMA_OK"}}
    with patch("urllib.request.urlopen", return_value=_Response(payload)) as mocked:
        result = provider.respond("Reply with exactly: OLLAMA_OK")
    assert result.text == "OLLAMA_OK"
    assert result.provider == "ollama"
    assert result.offline is True
    request = mocked.call_args.args[0]
    body = json.loads(request.data.decode())
    assert body["model"] == "qwen2.5:7b"
    assert body["stream"] is False


def test_local_factory_returns_ollama():
    provider = create_brain_provider("local")
    assert provider.name == "ollama"
    assert provider.offline is True
