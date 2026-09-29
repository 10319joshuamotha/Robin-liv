from core.robin_policy import AuthorizationLevel, Capability, RobinPolicy


def test_finance_is_always_denied():
    policy = RobinPolicy()
    decision = policy.decide(
        Capability.FINANCE,
        authenticated=True,
        confirmed=True,
        multi_step_verified=True,
    )
    assert decision.allowed is False
    assert decision.required_authorization is AuthorizationLevel.NONE


def test_gallery_requires_explicit_one_shot_grant():
    policy = RobinPolicy()
    denied = policy.decide(Capability.GALLERY, authenticated=True)
    assert denied.allowed is False

    granted = policy.decide(
        Capability.GALLERY,
        authenticated=True,
        confirmed=True,
        explicit_media_grant=True,
    )
    assert granted.allowed is True
    assert granted.one_shot is True


def test_private_mode_blocks_screen():
    policy = RobinPolicy()
    decision = policy.decide(
        Capability.SCREEN,
        authenticated=True,
        private_mode=True,
    )
    assert decision.allowed is False
