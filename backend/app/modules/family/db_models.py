"""Database models for families, memberships and invitations."""

from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class FamilyDB(Base):
    """Family entity - a group of users sharing recipes and shopping lists."""

    __tablename__ = "families"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    owner_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    plan: Mapped[str] = mapped_column(String(16), default="free", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)


class FamilyMembershipDB(Base):
    """Association table mapping users to families with roles."""

    __tablename__ = "family_memberships"

    family_id: Mapped[str] = mapped_column(String(36), ForeignKey("families.id"), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), primary_key=True)
    role: Mapped[str] = mapped_column(String(32), default="member", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)


class FamilyInvitationDB(Base):
    """Invitation link allowing a user to join a family."""

    __tablename__ = "family_invitations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    family_id: Mapped[str] = mapped_column(String(36), ForeignKey("families.id"), nullable=False, index=True)
    token: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    created_by: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    accepted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    accepted_by: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
