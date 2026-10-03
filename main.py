import platform as _platform
import subprocess as _subprocess

# ── Nuclear: force CREATE_NO_WINDOW on EVERY subprocess call on Windows ───────
# This patches Popen itself, so no per-file flag is needed anywhere.
if _platform.system() == "Windows":
    _OrigPopen = _subprocess.Popen

    class _Popen(_OrigPopen):
        def __init__(self, args, **kw):
            kw["creationflags"] = kw.get("creationflags", 0) | _subprocess.CREATE_NO_WINDOW
            kw.pop("startupinfo", None)
            super().__init__(args, **kw)

    _subprocess.Popen = _Popen

import sys as _sys
for _stream in ("stdout", "stderr"):
    try:
        _s = getattr(_sys, _stream, None)
        if _s is not None and hasattr(_s, "reconfigure"):
            _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import asyncio
import re
import threading
import time
import json
import sys
import traceback
from datetime import datetime
from pathlib import Path

import sounddevice as sd
import numpy as np
from google import genai
from google.genai import types
from ui import JarvisUI
from actions.browser_bridge import start_bridge
from memory.memory_manager import (
    load_memory, update_memory, format_memory_for_prompt,
    save_session_summary, pop_last_session,
    search_memory, set_trim_notifier,
)
from actions.screen_processor import _capture_camera, _capture_screen
from actions.system_monitor import SystemMonitor, get_system_status
from actions.proactive import ProactiveEngine
from actions.background_monitor import (
    add_monitor, remove_monitor, list_monitors, check_all as monitor_check_all,
)
from actions.web_search import _news as _fetch_news_sync
from memory.config_manager import (
    get_brief_enabled, get_media_resolution, get_proactive_audio_enabled,
    get_push_to_talk_enabled, get_thinking_enabled, get_turn_tuning, get_voice,
    get_wake_word_enabled, save_wake_word_enabled, get_input_device, get_output_device,
)
from core.plugin_loader import discover_plugins
from core import undo as undo_stack
from core import confirm as confirm_gate
from core import audio_devices
from core.action_loader import discover_actions
from core.echo import EchoGuard
from core.viseme import VisemeStream
from core.wake_word import (
    WakeWordDetector, is_ready as wake_is_ready, install_and_download as wake_install,
)
from core.spatial_context import spatial_context

try:
    from core.runtime_mode import get_runtime_mode
    from core.brain_provider import create_brain_provider
except Exception:
    get_runtime_mode = None
    create_brain_provider = None

WAKE_SLEEP_TIMEOUT = 120.0

def get_base_dir():
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent

BASE_DIR = get_base_dir()
API_CONFIG_PATH = BASE_DIR / "config" / "api_keys.json"
PROMPT_PATH = BASE_DIR / "core" / "prompt.txt"
LIVE_MODEL = "models/gemini-3.1-flash-live-preview"
CHANNELS = 1
SEND_SAMPLE_RATE = 16000
RECEIVE_SAMPLE_RATE = 24000
CHUNK_SIZE = 1024
_LEVEL_FLOOR = 60.0
_LEVEL_FULL = 2600.0
_TAIL_MARGIN = 0.25
_VIS_WIN = 1024
_VIS_HOP = 480
_FIRST_SOUND = CHUNK_SIZE / RECEIVE_SAMPLE_RATE
_CURSOR_SLACK = 0.15

def _pcm_level(samples) -> float:
    try:
        x = np.asarray(samples, dtype=np.float32)
        if x.size == 0:
            return 0.0
        rms = float(np.sqrt(np.mean(x * x)))
    except Exception:
        return 0.0
    if rms <= _LEVEL_FLOOR:
        return 0.0
    return min(1.0, (rms - _LEVEL_FLOOR) / (_LEVEL_FULL - _LEVEL_FLOOR))

def _pcm_visemes(samples, sr: int = 24000):
    try:
        x = np.asarray(samples, dtype=np.float32)
        if x.size < _VIS_WIN:
            return []
        win = np.hanning(_VIS_WIN).astype(np.float32)
        freqs = np.fft.rfftfreq(_VIS_WIN, 1.0 / sr)
        frames = []
        for start in range(0, x.size - _VIS_WIN + 1, _VIS_HOP):
            block = x[start:start + _VIS_WIN] * win
            spec = np.abs(np.fft.rfft(block))
            total = float(np.sum(spec)) + 1e-9
            level = min(1.0, float(np.sqrt(np.mean(block * block))) / 2600.0)
            f1 = float(np.sum(spec[(freqs >= 300) & (freqs < 1000)])) / total
            f2 = float(np.sum(spec[(freqs >= 1000) & (freqs < 3000)])) / total
            openness = min(1.0, max(0.0, 1.8 * f1))
            width = min(1.0, max(0.0, 1.8 * f2))
            frames.append((level, openness, width))
        return frames
    except Exception:
        return []


# NOTE: The complete historical Robin runtime is intentionally preserved below.
# The following helper is the only new runtime integration: it synchronises the
# God's Eye View-style context store with lifecycle and task state without
# capturing a screen or camera automatically.
def _sync_spatial_context(*, private_mode: bool = False, sleeping: bool = False,
                          task: str | None = None) -> None:
    spatial_context.set_privacy(private_mode=private_mode, sleeping=sleeping)
    if task is not None:
        spatial_context.set_task(task)

