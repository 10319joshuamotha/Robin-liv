from core.spatial_context import SpatialContext


def active_context() -> SpatialContext:
    context = SpatialContext()
    assert context.set_gev(True)
    return context


def test_task_and_selection_are_available_when_active():
    context = active_context()
    context.set_task("rename the selected folder")
    assert context.select_entity("folder-1", "folder", "Robin")

    snapshot = context.snapshot()
    assert snapshot["task"] == "rename the selected folder"
    assert snapshot["selected_entity"]["label"] == "Robin"
    assert snapshot["layers"]["selection"]["enabled"] is True


def test_private_mode_clears_visual_and_selection_context():
    context = active_context()
    context.set_task("work privately")
    assert context.select_entity("tab-1", "browser_tab", "Private tab")

    context.set_privacy(private_mode=True)
    snapshot = context.snapshot()

    assert snapshot["private_mode"] is True
    assert snapshot["selected_entity"] is None
    assert "screen" not in snapshot["layers"]
    assert "selection" not in snapshot["layers"]
    assert "Private mode: ON" in context.prompt_context()


def test_pc_sleep_clears_visual_context_and_blocks_selection():
    context = active_context()
    context.set_layer("screen", [{"kind": "desktop_observation"}])
    assert context.select_entity("window-1", "window", "Browser")

    context.set_privacy(private_mode=False, sleeping=True)

    assert context.select_entity("window-2", "window", "Another") is False
    snapshot = context.snapshot()
    assert snapshot["sleeping"] is True
    assert "screen" not in snapshot["layers"]
    assert "selection" not in snapshot["layers"]
