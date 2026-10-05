"""Offline voice turn: microphone -> local STT -> caller brain -> local TTS.

The module is deliberately provider-neutral. STT uses faster-whisper and TTS
uses Piper when installed; no network service is required for either stage once
models/voices are present locally.
"""
from __future__ import annotations

import os
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import numpy as np
import sounddevice as sd


@dataclass(frozen=True)
class VoiceConfig:
    sample_rate: int = 16_000
    channels: int = 1
    record_seconds: float = 6.0
    stt_model: str = "small"
    stt_device: str = "cpu"
    stt_compute_type: str = "int8"
    piper_model: str = ""
    piper_executable: str = "piper"
    output_device: int | None = None


class OfflineVoice:
    """Lazy-loaded local STT/TTS engine.

    The model objects are created only when used, so normal online/Gemini startup
    does not pay the local-model initialization cost.
    """

    def __init__(self, config: VoiceConfig | None = None):
        self.config = config or VoiceConfig(
            stt_model=os.getenv("ROBIN_STT_MODEL", "small"),
            stt_device=os.getenv("ROBIN_STT_DEVICE", "cpu"),
            stt_compute_type=os.getenv("ROBIN_STT_COMPUTE", "int8"),
            piper_model=os.getenv("ROBIN_PIPER_MODEL", ""),
            piper_executable=os.getenv("ROBIN_PIPER", "piper"),
        )
        self._whisper = None

    def _load_stt(self):
        if self._whisper is None:
            from faster_whisper import WhisperModel
            self._whisper = WhisperModel(
                self.config.stt_model,
                device=self.config.stt_device,
                compute_type=self.config.stt_compute_type,
            )
        return self._whisper

    def record(self, seconds: float | None = None) -> np.ndarray:
        duration = float(seconds or self.config.record_seconds)
        frames = max(1, int(duration * self.config.sample_rate))
        audio = sd.rec(
            frames,
            samplerate=self.config.sample_rate,
            channels=self.config.channels,
            dtype="float32",
        )
        sd.wait()
        return np.asarray(audio, dtype=np.float32).reshape(-1)

    def transcribe(self, audio: np.ndarray) -> str:
        model = self._load_stt()
        segments, _ = model.transcribe(
            audio,
            language="en",
            vad_filter=True,
            beam_size=5,
        )
        return " ".join(segment.text.strip() for segment in segments).strip()

    def speak(self, text: str) -> None:
        if not text.strip():
            return
        model = self.config.piper_model
        if not model:
            raise RuntimeError("ROBIN_PIPER_MODEL is not configured")
        model_path = str(Path(model).expanduser())
        if not Path(model_path).exists():
            raise FileNotFoundError(f"Piper voice model not found: {model_path}")
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp:
            wav_path = temp.name
        try:
            subprocess.run(
                [self.config.piper_executable, "--model", model_path, "--output_file", wav_path],
                input=text,
                text=True,
                check=True,
                capture_output=True,
            )
            import soundfile as sf
            data, rate = sf.read(wav_path, dtype="float32")
            sd.play(data, rate, device=self.config.output_device)
            sd.wait()
        finally:
            try:
                Path(wav_path).unlink()
            except OSError:
                pass

    def run_turn(self, respond: Callable[[str], str], seconds: float | None = None) -> str:
        """Record, transcribe, pass text to the brain, and speak its reply."""
        text = self.transcribe(self.record(seconds))
        if not text:
            return ""
        reply = respond(text)
        self.speak(reply)
        return reply
