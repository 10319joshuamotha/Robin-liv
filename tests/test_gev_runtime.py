"""Regression tests for Robin's on-demand God's Eye View gate."""
from core.spatial_context import SpatialContext


def test_gev_is_off_by_default():
    ctx = SpatialContext()
    assert ctx.gev_enabled is False
    assert "GEV: OFF" in ctx.prompt_context()


def test_screen_layer_requires_explicit_gev():
    ctx = SpatialContext()
    ctx.set_layer("screen", [{"kind": "visual_observation"}])
    assert ctx.snapshot()["layers"].get("screen") is None

    ctx.set_gev(True)
    ctx.set_layer("screen", [{"kind": "visual_observation"}])
    assert ctx.snapshot()["layers"]["screen"]["records"]


def test_turning_gev_off_clears_visual_context():
    ctx = SpatialContext()
    ctx.set_gev(True)
    assert ctx.select_entity("1", "ui_element", "Folder") is True
    ctx.set_layer("screen", [{"description": "Folder"}])
    ctx.set_gev(False)
    snap = ctx.snapshot()
    assert snap["gev_enabled"] is False
    assert snap["selected_entity"] is None
    assert "screen" not in snap["layers"]
    assert "selection" not in snap["layers"]


def test_private_mode_overrides_gev():
    ctx = SpatialContext()
    ctx.set_gev(True)
    ctx.set_privacy(private_mode=True)
    assert ctx.select_entity("1", "ui_element", "Folder") is False
    assert ctx.snapshot()["layers"].get("screen") is None


def test_sleep_overrides_gev():
    ctx = SpatialContext()
    ctx.set_gev(True)
    ctx.set_privacy(private_mode=False, sleeping=True)
    assert ctx.select_entity("1", "ui_element", "Folder") is False
    assert ctx.snapshot()["layers"].get("selection") is None
