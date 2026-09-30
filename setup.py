"""
Robin — one-time setup.

Installs the Python dependencies for the current operating system. Optional
voice/browser components remain optional so the base assistant can start even
when a large model or browser download is unavailable.
"""
import platform
import subprocess
import sys
from pathlib import Path

OS = platform.system()
HERE = Path(__file__).resolve().parent
MIN_PY = (3, 11)
MAX_PY = (3, 13)


def _run(label: str, args: list[str]) -> None:
    print(f"\n▶ {label}")
    subprocess.run(args, check=True)


def _check_python() -> None:
    v = sys.version_info[:2]
    if v < MIN_PY:
        print(f"\n❌ Python {v[0]}.{v[1]} detected — Robin needs at least Python {MIN_PY[0]}.{MIN_PY[1]}.")
        sys.exit(1)
    if v > MAX_PY:
        print(f"\n⚠️ Python {v[0]}.{v[1]} is newer than the tested range ({MAX_PY[0]}.{MAX_PY[1]}). Continuing.")


def _check_assets() -> None:
    face = HERE / "core" / "face_model.obj"
    if not face.exists() or face.stat().st_size < 4096:
        print("\n⚠️ core/face_model.obj is missing or truncated; the avatar will use its fallback renderer.")


def main() -> None:
    print(f"⚙ Robin setup — detected OS: {OS or 'unknown'}, Python {sys.version_info[0]}.{sys.version_info[1]}")
    _check_python()
    _run("Installing Python dependencies (OS-specific extras auto-filtered)…",
         [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

    try:
        _run("Installing Playwright browsers (chromium + firefox)…",
             [sys.executable, "-m", "playwright", "install", "chromium", "firefox"])
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"\n⚠️ Playwright browsers were not installed ({e}). Browser automation can be retried later.")

    _check_assets()

    if OS == "Windows":
        try:
            import win32com.client  # noqa: F401
        except ImportError:
            print("\n⚠️ pywin32 is not registered correctly; desktop shortcut features may use a fallback.")

    print("\n✅ Robin setup complete!")
    print("   1) Launch it: python main.py")
    print("   2) Configure the selected AI provider in the app.")
    print("   3) Offline voice/wake-word components can be enabled when their local models are installed.")


if __name__ == "__main__":
    main()
