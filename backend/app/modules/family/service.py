"""Business logic for the family module.

Enforces the MVP rules:
- 1 user = 1 family (a user can belong to exactly one family),
- member limits per plan (free: 2, basic: 5, pro: unlimited),
- invitations respect the plan limit both at creation and at acceptance.
"""

import logging
import secrets
from datetime import UTC, datetime, timedelta

from app.modules.family.constants import DEFAULT_PLAN, INVITATION_EXPIRES_DAYS, PLAN_MEMBER_LIMITS
from app.modules.family.db_models import FamilyDB, FamilyMembershipDB
from app.modules.family.exceptions import (
    AlreadyInFamilyError,
    CannotRemoveOwnerError,
    FamilyNotFoundError,
    InvitationAlreadyAcceptedError,
    InvitationExpiredError,
    InvitationNotFoundError,
    MemberLimitReachedError,
    MemberNotFoundError,
    NotFamilyOwnerError,
)
from app.modules.family.repository import FamilyRepository
from app.modules.family.schemas import (
    FamilyMemberResponse,
    FamilyMembersResponse,
    FamilyResponse,
    InvitationResponse,
    InvitationsResponse,
)

logger = logging.getLogger(__name__)


class FamilyService:
    """Service layer for family operations."""

    def __init__(self, repository: FamilyRepository):
        self.repository = repository

    # ==================== Families ====================

    async def create_family(self, *, user_id: str, name: str) -> FamilyResponse:
        """Create a new family with the current user as owner.

        Raises:
            AlreadyInFamilyError: If the user already belongs to a family.
        """
        existing = await self.repository.get_membership_for_user(user_id)
        if existing:
            raise AlreadyInFamilyError("User already belongs to a family")

        family, membership = await self.repository.create_family(
            name=name,
            owner_user_id=user_id,
            plan=DEFAULT_PLAN,
        )
        logger.info("Family %s created by user %s", family.id, user_id)
        return self._to_family_response(family, membership, member_count=1)

    async def get_my_family(self, user_id: str) -> FamilyResponse:
        """Get the current user's family with plan, member count and limit.

        Raises:
            FamilyNotFoundError: If the user has no family.
        """
        family, membership = await self._require_family(user_id)
        member_count = await self.repository.count_members(family.id)
        return self._to_family_response(family, membership, member_count=member_count)

    async def list_members(self, user_id: str) -> FamilyMembersResponse:
        """List members of the current user's family."""
        family, _ = await self._require_family(user_id)
        rows = await self.repository.list_members(family.id)
        return FamilyMembersResponse(
            members=[
                FamilyMemberResponse(
                    userId=user.id,
                    name=user.name,
                    email=user.email,
                    role=membership.role,
                    joinedAt=membership.created_at,
                )
                for membership, user in rows
            ]
        )

    async def remove_member(self, *, user_id: str, member_user_id: str) -> None:
        """Remove a member from the family (owner only).

        Raises:
            NotFamilyOwnerError: If the requesting user is not the owner.
            CannotRemoveOwnerError: If trying to remove the owner.
            MemberNotFoundError: If the target user is not a member.
        """
        family, membership = await self._require_family(user_id)
        if membership.role != "owner":
            raise NotFamilyOwnerError("Only the family owner can remove members")
        if member_user_id == family.owner_id:
            raise CannotRemoveOwnerError("The family owner cannot be removed")

        target = await self.repository.get_membership(family.id, member_user_id)
        if not target:
            raise MemberNotFoundError(f"User {member_user_id} is not a member of this family")

        await self.repository.remove_member(family.id, member_user_id)
        logger.info("User %s removed from family %s by owner %s", member_user_id, family.id, user_id)

    # ==================== Invitations ====================

    async def create_invitation(self, user_id: str) -> InvitationResponse:
        """Create an invitation link for the current user's family.

        Raises:
            MemberLimitReachedError: If the plan member limit is already reached.
        """
        family, _ = await self._require_family(user_id)
        await self._ensure_member_capacity(family)

        token = secrets.token_urlsafe(32)
        expires_at = datetime.now(UTC) + timedelta(days=INVITATION_EXPIRES_DAYS)
        invitation = await self.repository.create_invitation(
            family_id=family.id,
            token=token,
            created_by=user_id,
            expires_at=expires_at,
        )
        logger.info("Invitation %s created for family %s by user %s", invitation.id, family.id, user_id)
        return InvitationResponse(
            id=invitation.id,
            token=invitation.token,
            expiresAt=invitation.expires_at,
            createdAt=invitation.created_at,
        )

    async def list_invitations(self, user_id: str) -> InvitationsResponse:
        """List active (not accepted, not expired) invitations for the user's family."""
        family, _ = await self._require_family(user_id)
        invitations = await self.repository.list_active_invitations(family.id)
        return InvitationsResponse(
            invitations=[
                InvitationResponse(
                    id=inv.id,
                    token=inv.token,
                    expiresAt=inv.expires_at,
                    createdAt=inv.created_at,
                )
                for inv in invitations
            ]
        )

    async def accept_invitation(self, *, token: str, user_id: str) -> FamilyResponse:
        """Accept an invitation link and join the family.

        Validates the plan member limit and the "1 user = 1 family" rule.

        Raises:
            InvitationNotFoundError: If the token does not exist.
            InvitationExpiredError: If the invitation has expired.
            InvitationAlreadyAcceptedError: If the invitation was already used.
            AlreadyInFamilyError: If the user already belongs to a family.
            MemberLimitReachedError: If the family is at its plan limit.
            FamilyNotFoundError: If the invitation's family no longer exists.
        """
        invitation = await self.repository.get_invitation_by_token(token)
        if not invitation:
            raise InvitationNotFoundError("Invitation not found")
        if invitation.accepted_at is not None:
            raise InvitationAlreadyAcceptedError("Invitation has already been used")
        if invitation.expires_at is not None and invitation.expires_at <= datetime.now(UTC):
            raise InvitationExpiredError("Invitation has expired")

        existing = await self.repository.get_membership_for_user(user_id)
        if existing:
            raise AlreadyInFamilyError("User already belongs to a family")

        family = await self.repository.get_family(invitation.family_id)
        if not family:
            raise FamilyNotFoundError("Family for this invitation no longer exists")

        await self._ensure_member_capacity(family)

        membership = await self.repository.add_member(family.id, user_id, role="member")
        await self.repository.mark_invitation_accepted(invitation, user_id)
        member_count = await self.repository.count_members(family.id)
        logger.info("User %s joined family %s via invitation %s", user_id, family.id, invitation.id)
        return self._to_family_response(family, membership, member_count=member_count)

    # ==================== Helpers ====================

    async def _require_family(self, user_id: str) -> tuple[FamilyDB, FamilyMembershipDB]:
        membership = await self.repository.get_membership_for_user(user_id)
        if not membership:
            raise FamilyNotFoundError("User does not belong to any family")
        family = await self.repository.get_family(membership.family_id)
        if not family:
            raise FamilyNotFoundError("Family not found")
        return family, membership

    async def _ensure_member_capacity(self, family: FamilyDB) -> None:
        limit = PLAN_MEMBER_LIMITS.get(family.plan, PLAN_MEMBER_LIMITS[DEFAULT_PLAN])
        if limit is None:
            return
        member_count = await self.repository.count_members(family.id)
        if member_count >= limit:
            raise MemberLimitReachedError(f"Plan '{family.plan}' allows at most {limit} members")

    def _to_family_response(self, family: FamilyDB, membership: FamilyMembershipDB, *, member_count: int) -> FamilyResponse:
        return FamilyResponse(
            id=family.id,
            name=family.name,
            plan=family.plan,
            role=membership.role,
            memberCount=member_count,
            memberLimit=PLAN_MEMBER_LIMITS.get(family.plan, PLAN_MEMBER_LIMITS[DEFAULT_PLAN]),
            createdAt=family.created_at,
        )
