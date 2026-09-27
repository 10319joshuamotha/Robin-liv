"""
Local wake-word detection for Robin.

Uses faster-whisper in a background thread so the microphone callback stays
non-blocking. Audio never leaves the machine. The detector listens only while
Robin is asleep and fires when the transcript contains the standalone word
"Robin".
"""
from __future__ import annotations
import queue, subprocess, sys, threading, time
from typing import Callable
import numpy as np

SAMPLE_RATE = 16000
DEFAULT_THRESHOLD = 0.0
WAKE_PHRASE = "robin"

def is_installed() -> bool:
    try:
        import importlib.util
        return importlib.util.find_spec("faster_whisper") is not None
    except Exception:
        return False

def is_ready() -> bool:
    return is_installed()

def install_and_download(logger: Callable[[str], None] = print,
                         notify: Callable[[str], None] | None = None) -> tuple[bool, str]:
    tell = notify or (lambda _msg: None)
    try:
        if not is_installed():
            logger("Wake word: installing faster-whisper (one-time)…")
            tell("Wake word: installing faster-whisper (one-time)…")
            r = subprocess.run([sys.executable, "-m", "pip", "install", "faster-whisper>=1.1,<2"],
                               capture_output=True, text=True)
            if r.returncode != 0:
                tail = (r.stderr or r.stdout or "").strip().splitlines()[-1:] or [""]
                return False, f"pip install failed: {tail[0][:160]}"
        logger("Wake word: Robin speech model is ready on first use.")
        tell("Wake word ready. Say 'Robin'.")
        return True, "Robin wake word ready."
    except Exception as e:
        return False, f"setup error: {e}"

class WakeWordDetector:
    """Offline speech wake detector. Buffers short PCM windows and transcribes them."""
    def __init__(self, on_detect: Callable[[], None], threshold: float = DEFAULT_THRESHOLD,
                 logger: Callable[[str], None] = print,
                 notify: Callable[[str], None] | None = None):
        self._on_detect, self._logger = on_detect, logger
        self._notify = notify or (lambda _msg: None)
        self._queue = queue.Queue(maxsize=12)
        self._thread = None
        self._running = self._ready = False
        self._model = None
        self._buffer = np.zeros(0, dtype=np.float32)
        self._last_detect = 0.0

    def start(self) -> bool:
        if self._running: return True
        try:
            from faster_whisper import WhisperModel
            self._logger("Wake word: loading local speech model (tiny.en)…")
            self._model = WhisperModel("tiny.en", device="cpu", compute_type="int8")
        except Exception as e:
            self._logger(f"Wake word: could not load model — {e}")
            self._notify("Robin wake word unavailable — use WAKE NOW.")
            return False
        self._running = self._ready = True
        self._buffer = np.zeros(0, dtype=np.float32)
        self._thread = threading.Thread(target=self._loop, daemon=True, name="RobinWakeWord")
        self._thread.start()
        self._logger("Wake word: listening for 'Robin'.")
        return True

    def stop(self):
        self._running = False
        try: self._queue.put_nowait(None)
        except Exception: pass
        self._model = None
        self._ready = False

    @property
    def ready(self) -> bool: return self._ready

    def feed(self, frame_int16):
        if not self._running: return
        try:
            data = frame_int16[:, 0] if getattr(frame_int16, "ndim", 1) > 1 else frame_int16
            self._queue.put_nowait(np.asarray(data, dtype=np.int16).copy())
        except Exception: pass

    def _loop(self):
        while self._running:
            try:
                frame = self._queue.get(timeout=0.5)
                if frame is None: break
                pcm = frame.astype(np.float32) / 32768.0
                self._buffer = np.concatenate((self._buffer, pcm))
                if self._buffer.size < int(SAMPLE_RATE * 1.25): continue
                chunk = self._buffer[-int(SAMPLE_RATE * 1.8):]
                self._buffer = self._buffer[-int(SAMPLE_RATE * 0.35):]
                if float(np.sqrt(np.mean(chunk * chunk) + 1e-12)) < 0.008: continue
                segments, _ = self._model.transcribe(chunk, language="en", beam_size=1,
                    best_of=1, condition_on_previous_text=False, vad_filter=True)
                text = " ".join(s.text for s in segments).strip().lower()
                if "robin" in text and time.monotonic() - self._last_detect > 2.0:
                    self._last_detect = time.monotonic()
                    self._buffer = np.zeros(0, dtype=np.float32)
                    try: self._on_detect()
                    except Exception as e: self._logger(f"Wake word callback error: {e}")
            except queue.Empty:
                continue
            except Exception as e:
                self._logger(f"Wake word: inference error — {e}")
