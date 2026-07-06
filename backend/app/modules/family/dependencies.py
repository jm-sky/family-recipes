"""Shared FastAPI dependencies for resolving the current user's family."""

from typing import Annotated

from fastapi import Depends, HTTPException, status

from app.modules.auth.dependencies import CurrentUser
from app.modules.family.repository import FamilyRepository, get_family_repository


async def get_current_family_id(
    current_user: CurrentUser,
    repo: Annotated[FamilyRepository, Depends(get_family_repository)],
) -> str:
    """Resolve the family_id of the current user.

    All domain endpoints are scoped to the caller's family.

    Raises:
        HTTPException: 403 when the user does not belong to any family.
    """
    membership = await repo.get_membership_for_user(current_user.id)
    if membership is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not belong to any family")
    return membership.family_id


CurrentFamilyId = Annotated[str, Depends(get_current_family_id)]
