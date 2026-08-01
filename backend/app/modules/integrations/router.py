"""Router for Google Keep integration endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.modules.auth.dependencies import CurrentUser
from app.modules.integrations.exceptions import (
    KeepAuthenticationError,
    KeepMirrorNotFoundError,
    KeepNotConnectedError,
)
from app.modules.integrations.keep_client import KeepClient
from app.modules.integrations.keep_sync_service import KeepSyncService
from app.modules.integrations.repository import IntegrationsRepository
from app.modules.integrations.schemas import (
    KeepConnectRequest,
    KeepMirrorCreateRequest,
    KeepMirrorResponse,
    KeepMirrorsResponse,
    KeepMirrorUpdateRequest,
    KeepStatusResponse,
    KeepSyncAllResponse,
)
from app.modules.shopping.repository import ShoppingRepository


def require_keep_enabled() -> None:
    """Reject requests when Google Keep sync is disabled globally."""
    if not settings.keep.enabled:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Google Keep sync is disabled")


router = APIRouter(prefix="/integrations/keep", tags=["integrations-keep"], dependencies=[Depends(require_keep_enabled)])


def get_keep_sync_service(db: Annotated[AsyncSession, Depends(get_db)]) -> KeepSyncService:
    """Build the Keep sync service with its repository dependencies."""
    return KeepSyncService(
        repository=IntegrationsRepository(db),
        shopping_repository=ShoppingRepository(db),
        keep_client=KeepClient(),
    )


KeepSyncServiceDep = Annotated[KeepSyncService, Depends(get_keep_sync_service)]


def _not_found(exc: Exception) -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


def _bad_request(exc: Exception) -> HTTPException:
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.get("/status", response_model=KeepStatusResponse)
async def get_status(current_user: CurrentUser, service: KeepSyncServiceDep) -> KeepStatusResponse:
    """Get the current user's Google Keep connection status."""
    return await service.get_status(current_user.id)


@router.post("/connect", response_model=KeepStatusResponse)
async def connect(payload: KeepConnectRequest, current_user: CurrentUser, service: KeepSyncServiceDep) -> KeepStatusResponse:
    """Link (or relink) the user's Google Keep account via a manually-obtained master token."""
    try:
        return await service.connect(current_user.id, payload)
    except KeepAuthenticationError as e:
        raise _bad_request(e)


@router.delete("/disconnect")
async def disconnect(current_user: CurrentUser, service: KeepSyncServiceDep) -> dict[str, str]:
    """Remove the user's Keep connection and all mirrors (notes stay in Keep)."""
    await service.disconnect(current_user.id)
    return {"message": "Google Keep disconnected"}


@router.get("/mirrors", response_model=KeepMirrorsResponse)
async def list_mirrors(current_user: CurrentUser, service: KeepSyncServiceDep) -> KeepMirrorsResponse:
    """List the user's shopping-list <-> Keep note mirrors."""
    return KeepMirrorsResponse(mirrors=await service.list_mirrors(current_user.id))


@router.post("/mirrors", response_model=KeepMirrorResponse)
async def create_mirror(payload: KeepMirrorCreateRequest, current_user: CurrentUser, service: KeepSyncServiceDep) -> KeepMirrorResponse:
    """Create a new Keep checklist note mirroring a shopping list, and push it once."""
    try:
        return await service.create_mirror(current_user.id, payload.shopping_list_id)
    except KeepNotConnectedError as e:
        raise _bad_request(e)
    except KeepAuthenticationError as e:
        raise _bad_request(e)


@router.delete("/mirrors/{mirror_id}")
async def delete_mirror(mirror_id: str, current_user: CurrentUser, service: KeepSyncServiceDep) -> dict[str, str]:
    """Remove a mirror (the Keep note itself is left untouched)."""
    try:
        await service.delete_mirror(current_user.id, mirror_id)
    except KeepMirrorNotFoundError as e:
        raise _not_found(e)
    return {"message": "Mirror removed"}


@router.patch("/mirrors/{mirror_id}", response_model=KeepMirrorResponse)
async def update_mirror(mirror_id: str, payload: KeepMirrorUpdateRequest, current_user: CurrentUser, service: KeepSyncServiceDep) -> KeepMirrorResponse:
    """Update a mirror's auto-sync flag."""
    try:
        return await service.update_mirror(current_user.id, mirror_id, payload.auto_sync)
    except KeepMirrorNotFoundError as e:
        raise _not_found(e)


@router.post("/mirrors/{mirror_id}/sync", response_model=KeepMirrorResponse)
async def sync_mirror(mirror_id: str, current_user: CurrentUser, service: KeepSyncServiceDep) -> KeepMirrorResponse:
    """Push the current state of a shopping list to its Keep mirror now."""
    try:
        return await service.sync_mirror_by_id(current_user.id, mirror_id)
    except KeepMirrorNotFoundError as e:
        raise _not_found(e)
    except KeepNotConnectedError as e:
        raise _bad_request(e)


@router.post("/sync-all", response_model=KeepSyncAllResponse)
async def sync_all(current_user: CurrentUser, service: KeepSyncServiceDep) -> KeepSyncAllResponse:
    """Push all of the user's auto-sync mirrors, collecting per-mirror errors."""
    return KeepSyncAllResponse(results=await service.sync_all(current_user.id))
