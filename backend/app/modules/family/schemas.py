"""Pydantic schemas for family endpoints."""

from datetime import datetime

from pydantic import BaseModel, Field


class FamilyCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)


class FamilyResponse(BaseModel):
    id: str
    name: str
    plan: str
    role: str
    memberCount: int
    memberLimit: int | None = None  # None = unlimited
    createdAt: datetime


class FamilyMemberResponse(BaseModel):
    userId: str
    name: str
    email: str
    role: str
    joinedAt: datetime


class FamilyMembersResponse(BaseModel):
    members: list[FamilyMemberResponse]


class InvitationResponse(BaseModel):
    id: str
    token: str
    expiresAt: datetime | None = None
    createdAt: datetime


class InvitationsResponse(BaseModel):
    invitations: list[InvitationResponse]


class InvitationPreviewResponse(BaseModel):
    familyName: str
    expiresAt: datetime | None = None
