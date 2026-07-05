"""API routers for family management and invitation acceptance."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.modules.auth.dependencies import CurrentUser
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
from app.modules.family.repository import FamilyRepository, get_family_repository
from app.modules.family.schemas import (
    FamilyCreateRequest,
    FamilyMembersResponse,
    FamilyResponse,
    InvitationResponse,
    InvitationsResponse,
)
from app.modules.family.service import FamilyService

router = APIRouter(prefix="/families", tags=["Families"])
invitations_router = APIRouter(prefix="/invitations", tags=["Families"])


def get_family_service(repo: Annotated[FamilyRepository, Depends(get_family_repository)]) -> FamilyService:
    """FastAPI dependency to obtain the family service."""
    return FamilyService(repository=repo)


FamilyServiceDep = Annotated[FamilyService, Depends(get_family_service)]


@router.post("", status_code=status.HTTP_201_CREATED, response_model=FamilyResponse)
async def create_family(
    payload: FamilyCreateRequest,
    current_user: CurrentUser,
    service: FamilyServiceDep,
) -> FamilyResponse:
    """Create a new family (default plan: free). Creator becomes the owner."""
    try:
        return await service.create_family(user_id=current_user.id, name=payload.name)
    except AlreadyInFamilyError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.get("/me", response_model=FamilyResponse)
async def get_my_family(
    current_user: CurrentUser,
    service: FamilyServiceDep,
) -> FamilyResponse:
    """Get the current user's family with plan, member count and member limit."""
    try:
        return await service.get_my_family(current_user.id)
    except FamilyNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/me/members", response_model=FamilyMembersResponse)
async def list_members(
    current_user: CurrentUser,
    service: FamilyServiceDep,
) -> FamilyMembersResponse:
    """List members of the current user's family."""
    try:
        return await service.list_members(current_user.id)
    except FamilyNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/me/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_member(
    user_id: str,
    current_user: CurrentUser,
    service: FamilyServiceDep,
) -> None:
    """Remove a member from the family (owner only)."""
    try:
        await service.remove_member(user_id=current_user.id, member_user_id=user_id)
    except FamilyNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except NotFamilyOwnerError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except CannotRemoveOwnerError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except MemberNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/me/invitations", status_code=status.HTTP_201_CREATED, response_model=InvitationResponse)
async def create_invitation(
    current_user: CurrentUser,
    service: FamilyServiceDep,
) -> InvitationResponse:
    """Create an invitation link. Returns 403 when the plan member limit is reached."""
    try:
        return await service.create_invitation(current_user.id)
    except FamilyNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except MemberLimitReachedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.get("/me/invitations", response_model=InvitationsResponse)
async def list_invitations(
    current_user: CurrentUser,
    service: FamilyServiceDep,
) -> InvitationsResponse:
    """List active invitations for the current user's family."""
    try:
        return await service.list_invitations(current_user.id)
    except FamilyNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@invitations_router.post("/{token}/accept", response_model=FamilyResponse)
async def accept_invitation(
    token: str,
    current_user: CurrentUser,
    service: FamilyServiceDep,
) -> FamilyResponse:
    """Accept an invitation link (validates plan limit and the 1-user-1-family rule)."""
    try:
        return await service.accept_invitation(token=token, user_id=current_user.id)
    except InvitationNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except InvitationExpiredError as e:
        raise HTTPException(status_code=status.HTTP_410_GONE, detail=str(e))
    except InvitationAlreadyAcceptedError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except AlreadyInFamilyError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except MemberLimitReachedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except FamilyNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
