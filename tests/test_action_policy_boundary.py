from core.action_loader import _capability_for_action
from core.robin_policy import Capability


def test_capability_classification_uses_tokens_not_substrings():
    assert _capability_for_action("open_payment") is Capability.FINANCE
    assert _capability_for_action("open_pictures_folder") is Capability.GALLERY
    # A harmless name containing a sensitive word as a substring must not be classified.
    assert _capability_for_action("repayment_status") is None


def test_explicit_capability_overrides_legacy_name_mapping():
    assert _capability_for_action("custom_tool", "screen") is Capability.SCREEN


def test_invalid_explicit_capability_is_not_accepted():
    assert _capability_for_action("custom_tool", "not_a_capability") is None
