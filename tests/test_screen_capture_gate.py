"""Regression tests for the direct screen-capture GEV boundary."""
import pytest

from actions import screen_processor
from core.spatial_context import spatial_context


def test_direct_screen_capture_is_denied_when_gev_is_off(monkeypatch):
    spatial_context.set_gev(False)
    monkeypatch.setattr(screen_processor, "_MSS", True)
    with pytest.raises(PermissionError, match="God's Eye View is OFF"):
        screen_processor._capture_screen()


def test_direct_screen_capture_reaches_backend_when_gev_is_on(monkeypatch):
    spatial_context.set_gev(True)
    monkeypatch.setattr(screen_processor, "_MSS", True)
    monkeypatch.setattr(
        screen_processor,
        "_compress",
        lambda data, fmt="PNG": (b"ok", "image/jpeg"),
    )

    class FakeMSS:
        monitors = [{"left": 0, "top": 0, "width": 1, "height": 1}]

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def grab(self, target):
            return type("Shot", (), {"rgb": b"rgb", "size": (1, 1)})()

    # screen_processor imports the mss module directly, so patch the module's
    # constructor rather than expecting a nested screen_processor.mss.mss API.
    monkeypatch.setattr(screen_processor.mss, "mss", lambda: FakeMSS())
    monkeypatch.setattr(screen_processor.mss.tools, "to_png", lambda rgb, size: b"png")

    assert screen_processor._capture_screen() == (b"ok", "image/jpeg")
