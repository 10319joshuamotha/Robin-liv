"""Routing helpers for Robin's hybrid Windows/Android assistant."""

from .companion_protocol import Capability, CompanionTask, Device, Transport, choose_transport

ANDROID_CAPABILITIES = {
    Capability.PHONE_CALL,
    Capability.PHONE_MESSAGE,
    Capability.PHONE_ALARM,
    Capability.PHONE_REMINDER,
    Capability.PHONE_NOTIFICATION,
    Capability.PHONE_CONTACTS,
    Capability.PHONE_VOICE,
}


def route_task(task: CompanionTask, *, android_reachable_locally: bool) -> tuple[Device, Transport]:
    if task.target == Device.ANDROID and task.capability in ANDROID_CAPABILITIES:
        return Device.ANDROID, choose_transport(android_reachable_locally=android_reachable_locally)
    if task.target == Device.WINDOWS:
        return Device.WINDOWS, Transport.LOCAL
    raise ValueError("Unsupported companion task target/capability")
