from core.companion_protocol import Capability, Device, Transport, make_alarm_task, make_call_task, choose_transport
from core.companion_router import route_task


def test_call_task_defaults_to_android_confirmation():
    task = make_call_task("John")
    assert task.target == Device.ANDROID
    assert task.capability == Capability.PHONE_CALL
    assert task.requires_confirmation is True


def test_alarm_validates_time():
    assert make_alarm_task(6, 30).payload["minute"] == 30


def test_transport_prefers_lan_then_cloud():
    assert choose_transport(android_reachable_locally=True) == Transport.LOCAL
    assert choose_transport(android_reachable_locally=False) == Transport.CLOUD


def test_router_selects_android_cloud_when_remote():
    task = make_call_task("John")
    assert route_task(task, android_reachable_locally=False) == (Device.ANDROID, Transport.CLOUD)
