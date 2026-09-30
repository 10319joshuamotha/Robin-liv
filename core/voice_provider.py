"""Provider-neutral voice interfaces for Robin.

Local STT/TTS adapters are optional and imported lazily. This keeps the core
install lightweight while giving the runtime a stable offline voice boundary.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


@dataclass(frozen=True)
class SpeechResult:
    text: str
    provider: str
    offline: bool = True


class STTProvider(Protocol):
    def transcribe(self, audio_path: str | Path) -> SpeechResult: ...


class TTSProvider(Protocol):
    def synthesize(self, text: str, output_path: str | Path) -> Path: ...


class FasterWhisperSTT:
    """Lazy faster-whisper adapter; model is loaded only when first used."""

    provider = "faster-whisper"
    offline = True

    def __init__(self, model_size: str = "base", device: str = "cpu", compute_type: str = "int8"):
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self._model = None

    def _load(self):
        if self._model is None:
            try:
                from faster_whisper import WhisperModel
            except ImportError as exc:
                raise RuntimeError("faster-whisper is not installed") from exc
            self._model = WhisperModel(self.model_size, device=self.device, compute_type=self.compute_type)
        return self._model

    def transcribe(self, audio_path: str | Path) -> SpeechResult:
        model = self._load()
        segments, _ = model.transcribe(str(audio_path), vad_filter=True)
        text = " ".join(segment.text.strip() for segment in segments).strip()
        return SpeechResult(text=text, provider=self.provider, offline=True)


class PiperTTS:
    """Optional Piper CLI adapter. The executable/model remain user-configured."""

    provider = "piper"
    offline = True

    def __init__(self, executable: str = "piper", model: str | None = None):
        self.executable = executable
        self.model = model

    def synthesize(self, text: str, output_path: str | Path) -> Path:
        import subprocess

        if not self.model:
            raise RuntimeError("Piper model is not configured")
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        cmd = [self.executable, "--model", self.model, "--output_file", str(output)]
        subprocess.run(cmd, input=text, text=True, check=True)
        return output
