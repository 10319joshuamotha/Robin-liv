"""Central safety policy for Robin's high-risk capabilities.

This module is deliberately model-independent. The LLM may request an action,
but it cannot bypass these policy decisions.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from time import monotonic


class RiskDomain(str, Enum):
    NORMAL = "normal"
    FINANCIAL = "financial"
    CREDENTIAL = "credential"
    GALLERY = "gallery"
    SCREEN = "screen"
    SYSTEM = "system"


class AuthorizationStage(int, Enum):
    NONE = 0
    IDENTITY = 1
    INTENT = 2
    FINAL_CONFIRMATION = 3


@dataclass
class OneShotGrant:
    resource_id: str
    created_at: float
    expires_after_task: bool = True


class SecurityPolicy:
    """Non-bypassable policy decisions for sensitive Robin capabilities."""

    def __init__(self) -> None:
        self._financial_stage = AuthorizationStage.NONE
        self._gallery_grant: OneShotGrant | None = None

    def requires_authorization(self, domain: RiskDomain) -> bool:
        return domain in {
            RiskDomain.FINANCIAL,
            RiskDomain.CREDENTIAL,
            RiskDomain.GALLERY,
            RiskDomain.SCREEN,
            RiskDomain.SYSTEM,
        }

    def financial_authorized(self) -> bool:
        return self._financial_stage is AuthorizationStage.FINAL_CONFIRMATION

    def advance_financial_verification(self, stage: AuthorizationStage) -> None:
        """Advance only one stage at a time; never accept a skipped stage."""

        if stage is AuthorizationStage.NONE:
            self._financial_stage = AuthorizationStage.NONE
            return
        if stage.value != self._financial_stage.value + 1:
            raise ValueError("Financial verification stages must be completed in order")
        self._financial_stage = stage

    def reset_financial_verification(self) -> None:
        self._financial_stage = AuthorizationStage.NONE

    def grant_one_shot_gallery_access(self, resource_id: str) -> None:
        if not resource_id:
            raise ValueError("A specific gallery resource is required")
        self._gallery_grant = OneShotGrant(resource_id=resource_id, created_at=monotonic())

    def gallery_allowed(self, resource_id: str) -> bool:
        grant = self._gallery_grant
        return grant is not None and grant.resource_id == resource_id

    def consume_gallery_grant(self, resource_id: str) -> bool:
        if not self.gallery_allowed(resource_id):
            return False
        self._gallery_grant = None
        return True

    def revoke_gallery_access(self) -> None:
        self._gallery_grant = None
