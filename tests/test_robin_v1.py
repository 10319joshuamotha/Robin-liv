from core.robin_policy import Capability, RobinPolicy
from core.robin_v1 import RobinRuntime, RuntimeMode


def test_finance_is_hard_denied_even_when_verified():
    decision = RobinPolicy().decide(
        Capability.FINANCE,
        authenticated=True,
        confirmed=True,
        multi_step_verified=True,
    )
    assert decision.allowed is False


def test_gallery_is_one_shot():
    runtime = RobinRuntime()
    runtime.authenticate()
    denied = runtime.authorize(Capability.GALLERY)
    assert denied.allowed is False
    allowed = runtime.authorize(Capability.GALLERY, confirmed=True, explicit_media_grant=True)
    assert allowed.allowed is True
    assert allowed.one_shot is True


def test_pc_sleep_blocks_runtime_work():
    runtime = RobinRuntime()
    runtime.authenticate()
    runtime.sleep_pc()
    assert runtime.snapshot().mode is RuntimeMode.SLEEPING
    try:
        runtime.begin_task("open a folder")
    except PermissionError:
        pass
    else:
        raise AssertionError("sleeping Robin must reject tasks")


def test_animation_can_be_disabled_independently():
    runtime = RobinRuntime()
    runtime.set_animation(False)
    assert runtime.snapshot().animation_enabled is False


def test_phone_private_mode_blocks_screen():
    runtime = RobinRuntime()
    runtime.authenticate()
    runtime.set_phone_private(True)
    decision = runtime.authorize(Capability.SCREEN)
    assert decision.allowed is False
