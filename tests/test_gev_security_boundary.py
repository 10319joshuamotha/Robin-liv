"""Security regression tests for the GEV action boundary."""

from pathlib import Path

from actions import screen_observation
from core.spatial_context import SpatialContext, spatial_context


def test_direct_screen_observation_is_denied_when_gev_is_off(monkeypatch):
    spatial_context.set_gev(False)
    called = False

    class FakePyAutoGUI:
        @staticmethod
        def screenshot(path):
            nonlocal called
            called = True

    monkeypatch.setattr(screen_observation, "pyautogui", FakePyAutoGUI)
    result = screen_observation.observe_screen({"path": str(Path.home() / "Desktop" / "x.png")})
    assert "blocked" in result.lower()
    assert called is False


def test_turning_gev_off_cannot_leave_visual_context_active():
    ctx = SpatialContext()
    # This test is independent of the physical screen capability.
    ctx._gev_enabled = True
    ctx._layers["screen"].enabled = True
    ctx._layers["screen"].records = [{"kind": "observation"}]
    ctx._selected = None
    ctx.set_gev(False)
    snap = ctx.snapshot()
    assert snap["gev_enabled"] is False
    assert "screen" not in snap["layers"]


def test_screen_observation_has_no_continuous_monitoring_metadata():
    assert screen_observation.TOOL["behavior"] == "BLOCKING"
    assert screen_observation.TOOL["scheduling"] == "INTERRUPT"
    assert screen_observation.TOOL["capability"] == "screen"
