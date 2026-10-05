import json
import os
from unittest.mock import patch

from core.brain_provider import OllamaProvider, create_brain_provider


def test_local_factory_uses_ollama():
    provider = create_brain_provider("local")
    assert isinstance(provider, OllamaProvider)
    assert provider.offline is True


def test_ollama_provider_posts_chat_request():
    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self):
            return json.dumps({"message": {"content": "Hello from Robin"}}).encode()

    captured = {}

    def fake_urlopen(request, timeout):
        captured["url"] = request.full_url
        captured["timeout"] = timeout
        captured["body"] = json.loads(request.data.decode())
        return FakeResponse()

    with patch("core.brain_provider.urllib.request.urlopen", fake_urlopen):
        result = OllamaProvider(model="test-model", base_url="http://127.0.0.1:11434", timeout=7).respond(
            "Hello", system="Be concise", context="User context"
        )

    assert result.text == "Hello from Robin"
    assert result.provider == "ollama"
    assert result.offline is True
    assert captured["url"].endswith("/api/chat")
    assert captured["timeout"] == 7
    assert captured["body"]["model"] == "test-model"
    assert captured["body"]["stream"] is False
    assert [m["role"] for m in captured["body"]["messages"]] == ["system", "system", "user"]


def test_ollama_environment_configuration():
    with patch.dict(os.environ, {"ROBIN_OLLAMA_MODEL": "env-model", "ROBIN_OLLAMA_URL": "http://localhost:9999"}):
        provider = OllamaProvider()
    assert provider.model == "env-model"
    assert provider.base_url == "http://localhost:9999"


def test_ollama_empty_response_is_rejected():
    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self):
            return b'{"message": {"content": ""}}'

    with patch("core.brain_provider.urllib.request.urlopen", lambda *a, **k: FakeResponse()):
        try:
            OllamaProvider().respond("Hello")
        except RuntimeError as exc:
            assert "empty response" in str(exc).lower()
        else:
            raise AssertionError("Expected empty Ollama response to fail")
