"""Unit tests for the family service (plan limits, invitations, 1-user-1-family)."""

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock

import pytest

from app.modules.family.db_models import FamilyDB, FamilyInvitationDB, FamilyMembershipDB
from app.modules.family.exceptions import (
    AlreadyInFamilyError,
    CannotRemoveOwnerError,
    InvitationAlreadyAcceptedError,
    InvitationExpiredError,
    InvitationNotFoundError,
    MemberLimitReachedError,
    NotFamilyOwnerError,
)
from app.modules.family.repository import FamilyRepository
from app.modules.family.service import FamilyService


@pytest.fixture
def mock_repository() -> AsyncMock:
    """Create a mock family repository."""
    return AsyncMock(spec=FamilyRepository)


@pytest.fixture
def family_service(mock_repository: AsyncMock) -> FamilyService:
    """Create FamilyService with a mocked repository."""
    return FamilyService(repository=mock_repository)


def make_family(plan: str = "free", owner_id: str = "owner1") -> FamilyDB:
    return FamilyDB(
        id="fam1",
        name="Kowalscy",
        owner_id=owner_id,
        plan=plan,
        created_at=datetime.now(UTC),
    )


def make_membership(user_id: str = "owner1", role: str = "owner") -> FamilyMembershipDB:
    return FamilyMembershipDB(
        family_id="fam1",
        user_id=user_id,
        role=role,
        created_at=datetime.now(UTC),
    )


def make_invitation(**overrides: object) -> FamilyInvitationDB:
    defaults: dict = {
        "id": "inv1",
        "family_id": "fam1",
        "token": "token123",
        "created_by": "owner1",
        "expires_at": datetime.now(UTC) + timedelta(days=7),
        "accepted_at": None,
        "accepted_by": None,
        "created_at": datetime.now(UTC),
    }
    defaults.update(overrides)
    return FamilyInvitationDB(**defaults)


class TestCreateFamily:
    """Tests for family creation."""

    @pytest.mark.asyncio
    async def test_create_family_defaults_to_free_plan(self, family_service: FamilyService, mock_repository: AsyncMock) -> None:
        mock_repository.get_membership_for_user.return_value = None
        mock_repository.create_family.return_value = (make_family(), make_membership())

        response = await family_service.create_family(user_id="owner1", name="Kowalscy")

        assert response.plan == "free"
        assert response.role == "owner"
        assert response.memberCount == 1
        assert response.memberLimit == 2
        mock_repository.create_family.assert_called_once_with(name="Kowalscy", owner_user_id="owner1", plan="free")

    @pytest.mark.asyncio
    async def test_create_family_rejects_user_already_in_family(self, family_service: FamilyService, mock_repository: AsyncMock) -> None:
        """1 user = 1 family: a member cannot create a second family."""
        mock_repository.get_membership_for_user.return_value = make_membership(user_id="user2", role="member")

        with pytest.raises(AlreadyInFamilyError):
            await family_service.create_family(user_id="user2", name="Druga rodzina")

        mock_repository.create_family.assert_not_called()


class TestInvitationLimits:
    """Tests for plan member limits at invitation creation."""

    @pytest.mark.asyncio
    async def test_free_plan_blocks_invitation_at_two_members(self, family_service: FamilyService, mock_repository: AsyncMock) -> None:
        mock_repository.get_membership_for_user.return_value = make_membership()
        mock_repository.get_family.return_value = make_family(plan="free")
        mock_repository.count_members.return_value = 2

        with pytest.raises(MemberLimitReachedError):
            await family_service.create_invitation("owner1")

        mock_repository.create_invitation.assert_not_called()

    @pytest.mark.asyncio
    async def test_free_plan_allows_invitation_below_limit(self, family_service: FamilyService, mock_repository: AsyncMock) -> None:
        mock_repository.get_membership_for_user.return_value = make_membership()
        mock_repository.get_family.return_value = make_family(plan="free")
        mock_repository.count_members.return_value = 1
        mock_repository.create_invitation.return_value = make_invitation()

        response = await family_service.create_invitation("owner1")

        assert response.token == "token123"
        mock_repository.create_invitation.assert_called_once()

    @pytest.mark.asyncio
    async def test_basic_plan_blocks_invitation_at_five_members(self, family_service: FamilyService, mock_repository: AsyncMock) -> None:
        mock_repository.get_membership_for_user.return_value = make_membership()
        mock_repository.get_family.return_value = make_family(plan="basic")
        mock_repository.count_members.return_value = 5

        with pytest.raises(MemberLimitReachedError):
            await family_service.create_invitation("owner1")

    @pytest.mark.asyncio
    async def test_basic_plan_allows_fifth_member_invitation(self, family_service: FamilyService, mock_repository: AsyncMock) -> None:
        mock_repository.get_membership_for_user.return_value = make_membership()
        mock_repository.get_family.return_value = make_family(plan="basic")
        mock_repository.count_members.return_value = 4
        mock_repository.create_invitation.return_value = make_invitation()

        response = await family_service.create_invitation("owner1")

        assert response.id == "inv1"

    @pytest.mark.asyncio
    async def test_pro_plan_has_no_member_limit(self, family_service: FamilyService, mock_repository: AsyncMock) -> None:
        mock_repository.get_membership_for_user.return_value = make_membership()
        mock_repository.get_family.return_value = make_family(plan="pro")
        mock_repository.count_members.return_value = 100
        mock_repository.create_invitation.return_value = make_invitation()

        response = await family_service.create_invitation("owner1")

        assert response.id == "inv1"

    @pytest.mark.asyncio
    async def test_unknown_plan_falls_back_to_free_limit(self, family_service: FamilyService, mock_repository: AsyncMock) -> None:
        mock_repository.get_membership_for_user.return_value = make_membership()
        mock_repository.get_family.return_value = make_family(plan="enterprise")
        mock_repository.count_members.return_value = 2

        with pytest.raises(MemberLimitReachedError):
            await family_service.create_invitation("owner1")


class TestAcceptInvitation:
    """Tests for invitation acceptance (limits + 1-user-1-family)."""

    @pytest.mark.asyncio
    async def test_accept_invitation_success(self, family_service: FamilyService, mock_repository: AsyncMock) -> None:
        invitation = make_invitation()
        mock_repository.get_invitation_by_token.return_value = invitation
        mock_repository.get_membership_for_user.return_value = None
        mock_repository.get_family.return_value = make_family(plan="free")
        mock_repository.count_members.side_effect = [1, 2]  # capacity check, then response
        mock_repository.add_member.return_value = make_membership(user_id="user2", role="member")

        response = await family_service.accept_invitation(token="token123", user_id="user2")

        assert response.role == "member"
        assert response.memberCount == 2
        mock_repository.add_member.assert_called_once_with("fam1", "user2", role="member")
        mock_repository.mark_invitation_accepted.assert_called_once_with(invitation, "user2")

    @pytest.mark.asyncio
    async def test_accept_invitation_unknown_token(self, family_service: FamilyService, mock_repository: AsyncMock) -> None:
        mock_repository.get_invitation_by_token.return_value = None

        with pytest.raises(InvitationNotFoundError):
            await family_service.accept_invitation(token="missing", user_id="user2")

    @pytest.mark.asyncio
    async def test_accept_invitation_expired(self, family_service: FamilyService, mock_repository: AsyncMock) -> None:
        mock_repository.get_invitation_by_token.return_value = make_invitation(expires_at=datetime.now(UTC) - timedelta(hours=1))

        with pytest.raises(InvitationExpiredError):
            await family_service.accept_invitation(token="token123", user_id="user2")

    @pytest.mark.asyncio
    async def test_accept_invitation_already_used(self, family_service: FamilyService, mock_repository: AsyncMock) -> None:
        mock_repository.get_invitation_by_token.return_value = make_invitation(accepted_at=datetime.now(UTC), accepted_by="user3")

        with pytest.raises(InvitationAlreadyAcceptedError):
            await family_service.accept_invitation(token="token123", user_id="user2")

    @pytest.mark.asyncio
    async def test_accept_invitation_rejects_member_of_another_family(self, family_service: FamilyService, mock_repository: AsyncMock) -> None:
        """1 user = 1 family: cannot join a second family."""
        mock_repository.get_invitation_by_token.return_value = make_invitation()
        mock_repository.get_membership_for_user.return_value = FamilyMembershipDB(
            family_id="other-family",
            user_id="user2",
            role="member",
            created_at=datetime.now(UTC),
        )

        with pytest.raises(AlreadyInFamilyError):
            await family_service.accept_invitation(token="token123", user_id="user2")

        mock_repository.add_member.assert_not_called()

    @pytest.mark.asyncio
    async def test_accept_invitation_enforces_limit_at_acceptance(self, family_service: FamilyService, mock_repository: AsyncMock) -> None:
        """Even with a valid link, joining fails when the family filled up meanwhile."""
        mock_repository.get_invitation_by_token.return_value = make_invitation()
        mock_repository.get_membership_for_user.return_value = None
        mock_repository.get_family.return_value = make_family(plan="free")
        mock_repository.count_members.return_value = 2

        with pytest.raises(MemberLimitReachedError):
            await family_service.accept_invitation(token="token123", user_id="user2")

        mock_repository.add_member.assert_not_called()


class TestRemoveMember:
    """Tests for member removal rules."""

    @pytest.mark.asyncio
    async def test_only_owner_can_remove_members(self, family_service: FamilyService, mock_repository: AsyncMock) -> None:
        mock_repository.get_membership_for_user.return_value = make_membership(user_id="user2", role="member")
        mock_repository.get_family.return_value = make_family()

        with pytest.raises(NotFamilyOwnerError):
            await family_service.remove_member(user_id="user2", member_user_id="user3")

        mock_repository.remove_member.assert_not_called()

    @pytest.mark.asyncio
    async def test_owner_cannot_be_removed(self, family_service: FamilyService, mock_repository: AsyncMock) -> None:
        mock_repository.get_membership_for_user.return_value = make_membership()
        mock_repository.get_family.return_value = make_family(owner_id="owner1")

        with pytest.raises(CannotRemoveOwnerError):
            await family_service.remove_member(user_id="owner1", member_user_id="owner1")

    @pytest.mark.asyncio
    async def test_owner_removes_member(self, family_service: FamilyService, mock_repository: AsyncMock) -> None:
        mock_repository.get_membership_for_user.return_value = make_membership()
        mock_repository.get_family.return_value = make_family()
        mock_repository.get_membership.return_value = make_membership(user_id="user2", role="member")

        await family_service.remove_member(user_id="owner1", member_user_id="user2")

        mock_repository.remove_member.assert_called_once_with("fam1", "user2")
