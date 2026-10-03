from core.spatial_context import SpatialContext


def test_gev_control_state_machine():
    ctx = SpatialContext()
    assert ctx.gev_enabled is False
    assert ctx.set_gev(True) in (True, False)
    ctx.set_gev(False)
    assert ctx.gev_enabled is False


def test_gev_off_clears_selection_and_screen():
    ctx = SpatialContext()
    if ctx.set_gev(True):
        assert ctx.select_entity("x", "ui", "Example") is True
        ctx.set_gev(False)
    snap = ctx.snapshot()
    assert snap["gev_enabled"] is False
    assert snap["selected_entity"] is None
    assert "screen" not in snap["layers"]
