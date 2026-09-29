"""Central policy gates for Robin's high-risk capabilities.

Policy decisions live here so UI, tools, voice commands and future clients can
share the same deny-by-default rules. This module does not perform actions.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class AuthorizationLevel(str, Enum):
    NONE = "none"
    USER = "user"
    CONFIRMED = "confirmed"
    MULTI_STEP = "multi_step"


class Capability(str, Enum):
    GALLERY = "gallery"
    SCREEN = "screen"
    FILES = "files"
    FINANCE = "finance"
    CREDENTIALS = "credentials"
    PHONE_CONTROL = "phone_control"
    PC_CONTROL = "pc_control"


@dataclass(frozen=True)
class PolicyDecision:
    allowed: bool
    reason: str
    required_authorization: AuthorizationLevel
    one_shot: bool = False


class RobinPolicy:
    """Deny-by-default policy for sensitive capabilities.

    Finance is a hard prohibition: no voice confirmation, biometric confirmation,
    or three-step verification can authorize it. Gallery access is the opposite:
    it is denied by default but can be granted for one explicitly named picture
    or tab, matching Robin's requested privacy model.
    """

    def decide(
        self,
        capability: Capability,
        *,
        authenticated: bool,
        confirmed: bool = False,
        multi_step_verified: bool = False,
        private_mode: bool = False,
        explicit_media_grant: bool = False,
    ) -> PolicyDecision:
        # Money/payment/banking operations are completely forbidden.
        if capability is Capability.FINANCE:
            return PolicyDecision(
                False,
                "Financial and payment operations are permanently forbidden by Robin policy.",
                AuthorizationLevel.NONE,
            )

        if not authenticated:
            return PolicyDecision(False, "User authentication is required.", AuthorizationLevel.USER)

        if capability is Capability.CREDENTIALS and not confirmed:
            return PolicyDecision(False, "Credential use requires explicit confirmation.", AuthorizationLevel.CONFIRMED)

        if capability is Capability.SCREEN and private_mode:
            return PolicyDecision(False, "Phone Private Mode blocks screen access.", AuthorizationLevel.USER)

        if capability is Capability.GALLERY:
            if not explicit_media_grant:
                return PolicyDecision(False, "Gallery access requires an explicit picture/tab grant.", AuthorizationLevel.CONFIRMED)
            return PolicyDecision(True, "Explicit media grant accepted for this task only.", AuthorizationLevel.CONFIRMED, one_shot=True)

        if capability in {Capability.PHONE_CONTROL, Capability.PC_CONTROL} and not confirmed:
            return PolicyDecision(False, "Device control requires explicit confirmation.", AuthorizationLevel.CONFIRMED)

        return PolicyDecision(True, "Capability permitted by current policy.", AuthorizationLevel.USER)
