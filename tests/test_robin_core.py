import tempfile
import unittest
from pathlib import Path

from core.animation_state import AnimationController, AnimationState
from core.device_state import DeviceKind, DeviceState, DeviceStateController
from core.memory_schema import MemoryKind, MemoryRecord, UserProfile
from core.robin_policy import AuthorizationLevel, Capability, RobinPolicy
from core.storage_manager import create_external_marker, discover
from core.performance_profile import for_desktop


class RobinCoreTests(unittest.TestCase):
    def test_pc_sleep_blocks_processing_but_keeps_escape(self):
        c = DeviceStateController(DeviceKind.PC)
        c.sleep_pc()
        self.assertEqual(c.state, DeviceState.SLEEPING)
        self.assertFalse(c.allows("microphone_processing"))
        self.assertFalse(c.allows("assistant_processing"))
        self.assertTrue(c.allows("keyboard_wake"))
        c.wake_pc()
        self.assertTrue(c.allows("microphone_processing"))

    def test_phone_private_blocks_screen(self):
        c = DeviceStateController(DeviceKind.PHONE)
        c.set_private_mode(True)
        self.assertFalse(c.allows("screen_capture"))
        self.assertTrue(c.allows("microphone_processing"))

    def test_policy_finance_requires_multistep(self):
        p = RobinPolicy()
        d = p.decide(Capability.FINANCE, authenticated=True)
        self.assertFalse(d.allowed)
        self.assertEqual(d.required_authorization, AuthorizationLevel.MULTI_STEP)
        self.assertTrue(p.decide(Capability.FINANCE, authenticated=True, multi_step_verified=True).allowed)

    def test_gallery_is_one_shot(self):
        p = RobinPolicy()
        d = p.decide(Capability.GALLERY, authenticated=True, explicit_media_grant=True)
        self.assertTrue(d.allowed)
        self.assertTrue(d.one_shot)

    def test_memory_is_user_scoped_and_deletable(self):
        profile = UserProfile("joshua", "Joshua")
        m = MemoryRecord(MemoryKind.PREFERENCE, "language", "English", owner_id="joshua")
        profile.add_memory(m)
        self.assertEqual(len(profile.active_memories()), 1)
        self.assertTrue(profile.forget(m.id))
        self.assertEqual(profile.active_memories(), [])

    def test_external_drive_uses_marker(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            usb = root / "usb"
            create_external_marker(usb)
            roots = discover(root / "core", [usb])
            self.assertEqual(roots.external, usb)

    def test_animation_toggle_and_task_state(self):
        a = AnimationController()
        self.assertEqual(a.state, AnimationState.IDLE)
        a.begin_task("rename folder")
        self.assertEqual(a.state, AnimationState.EXECUTING)
        a.set_enabled(False)
        self.assertEqual(a.state, AnimationState.HIDDEN)
        a.set_enabled(True)
        self.assertEqual(a.state, AnimationState.IDLE)

    def test_low_resource_profile_is_conservative(self):
        p = for_desktop(ram_gb=8, gpu_memory_gb=2)
        self.assertLessEqual(p.animation_fps, 24)
        self.assertFalse(p.screen_polling)
        self.assertEqual(p.background_workers, 1)


if __name__ == "__main__":
    unittest.main()
