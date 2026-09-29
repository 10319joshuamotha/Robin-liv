from core.device_state import DeviceKind, DeviceState, DeviceStateController


def test_pc_sleep_disables_assistant_capabilities_but_keeps_esc_wake():
    pc = DeviceStateController(DeviceKind.PC)

    pc.sleep_pc()

    assert pc.state is DeviceState.SLEEPING
    assert not pc.allows("microphone_processing")
    assert not pc.allows("screen_capture")
    assert not pc.allows("camera_capture")
    assert not pc.allows("assistant_processing")
    assert pc.allows("keyboard_wake")

    pc.wake_pc()
    assert pc.state is DeviceState.ACTIVE
    assert pc.allows("microphone_processing")


def test_phone_private_mode_blocks_screen_only():
    phone = DeviceStateController(DeviceKind.PHONE)

    phone.set_private_mode(True)

    assert phone.state is DeviceState.PRIVATE
    assert not phone.allows("screen_capture")
    assert phone.allows("microphone_processing")
    assert phone.allows("camera_capture")
    assert phone.allows("assistant_processing")

    phone.set_private_mode(False)
    assert phone.state is DeviceState.ACTIVE
    assert phone.allows("screen_capture")


def test_unknown_capability_is_denied():
    pc = DeviceStateController(DeviceKind.PC)
    assert not pc.allows("some_future_capability")
