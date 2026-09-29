from core.robin_runtime_state import AnimationMode, RobinRuntimeState, RuntimeMode


def test_sleep_stops_work_and_sets_sleep_animation():
    state = RobinRuntimeState()
    state.begin_task("rename folder")
    state.sleep()
    assert state.mode is RuntimeMode.SLEEPING
    assert state.animation is AnimationMode.SLEEPING
    assert state.current_task is None


def test_private_mode_hides_animation_and_wakes_cleanly():
    state = RobinRuntimeState()
    state.private_mode_on()
    assert state.mode is RuntimeMode.PHONE_PRIVATE
    assert state.animation is AnimationMode.HIDDEN
    state.private_mode_off()
    assert state.mode is RuntimeMode.ACTIVE
    assert state.animation is AnimationMode.IDLE


def test_animation_off_is_hidden_even_for_tasks():
    state = RobinRuntimeState()
    state.set_animation_enabled(False)
    state.begin_task("open folder")
    assert state.animation is AnimationMode.HIDDEN
