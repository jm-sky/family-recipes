"""Repository for family, membership and invitation operations."""

import logging
from datetime import UTC, datetime

from fastapi import Depends
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.id_utils import generate_id
from app.core.database import get_db
from app.modules.auth.db_models import UserDB
from app.modules.family.db_models import FamilyDB, FamilyInvitationDB, FamilyMembershipDB

logger = logging.getLogger(__name__)


class FamilyRepository:
    """Data access layer for families, memberships and invitations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ==================== Families ====================

    async def get_family(self, family_id: str) -> FamilyDB | None:
        result = await self.db.execute(select(FamilyDB).where(FamilyDB.id == family_id))
        return result.scalar_one_or_none()

    async def get_membership_for_user(self, user_id: str) -> FamilyMembershipDB | None:
        result = await self.db.execute(select(FamilyMembershipDB).where(FamilyMembershipDB.user_id == user_id))
        return result.scalar_one_or_none()

    async def get_membership(self, family_id: str, user_id: str) -> FamilyMembershipDB | None:
        result = await self.db.execute(
            select(FamilyMembershipDB).where(
                FamilyMembershipDB.family_id == family_id,
                FamilyMembershipDB.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def count_members(self, family_id: str) -> int:
        result = await self.db.execute(select(func.count()).select_from(FamilyMembershipDB).where(FamilyMembershipDB.family_id == family_id))
        return int(result.scalar_one())

    async def create_family(self, *, name: str, owner_user_id: str, plan: str) -> tuple[FamilyDB, FamilyMembershipDB]:
        family_id = generate_id()
        family = FamilyDB(
            id=family_id,
            name=name,
            owner_id=owner_user_id,
            plan=plan,
        )
        membership = FamilyMembershipDB(
            family_id=family_id,
            user_id=owner_user_id,
            role="owner",
        )
        self.db.add(family)
        self.db.add(membership)
        await self.db.commit()
        await self.db.refresh(family)
        return family, membership

    async def add_member(self, family_id: str, user_id: str, role: str = "member") -> FamilyMembershipDB:
        membership = FamilyMembershipDB(
            family_id=family_id,
            user_id=user_id,
            role=role,
        )
        self.db.add(membership)
        await self.db.commit()
        await self.db.refresh(membership)
        return membership

    async def remove_member(self, family_id: str, user_id: str) -> None:
        await self.db.execute(
            delete(FamilyMembershipDB).where(
                FamilyMembershipDB.family_id == family_id,
                FamilyMembershipDB.user_id == user_id,
            )
        )
        await self.db.commit()

    async def list_members(self, family_id: str) -> list[tuple[FamilyMembershipDB, UserDB]]:
        stmt = select(FamilyMembershipDB, UserDB).join(UserDB, UserDB.id == FamilyMembershipDB.user_id).where(FamilyMembershipDB.family_id == family_id).order_by(FamilyMembershipDB.created_at)
        result = await self.db.execute(stmt)
        return [(row[0], row[1]) for row in result.all()]

    # ==================== Invitations ====================

    async def create_invitation(self, *, family_id: str, token: str, created_by: str, expires_at: datetime | None) -> FamilyInvitationDB:
        invitation = FamilyInvitationDB(
            id=generate_id(),
            family_id=family_id,
            token=token,
            created_by=created_by,
            expires_at=expires_at,
        )
        self.db.add(invitation)
        await self.db.commit()
        await self.db.refresh(invitation)
        return invitation

    async def get_invitation_by_token(self, token: str) -> FamilyInvitationDB | None:
        result = await self.db.execute(select(FamilyInvitationDB).where(FamilyInvitationDB.token == token))
        return result.scalar_one_or_none()

    async def list_active_invitations(self, family_id: str) -> list[FamilyInvitationDB]:
        now = datetime.now(UTC)
        stmt = (
            select(FamilyInvitationDB)
            .where(
                FamilyInvitationDB.family_id == family_id,
                FamilyInvitationDB.accepted_at.is_(None),
                (FamilyInvitationDB.expires_at.is_(None)) | (FamilyInvitationDB.expires_at > now),
            )
            .order_by(FamilyInvitationDB.created_at.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def mark_invitation_accepted(self, invitation: FamilyInvitationDB, user_id: str) -> FamilyInvitationDB:
        invitation.accepted_at = datetime.now(UTC)
        invitation.accepted_by = user_id
        await self.db.commit()
        await self.db.refresh(invitation)
        return invitation


def get_family_repository(db: AsyncSession = Depends(get_db)) -> FamilyRepository:
    """FastAPI dependency to obtain a family repository."""
    return FamilyRepository(db)
