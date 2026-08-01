"""Pydantic schemas for the integrations module (Google Keep sync) API."""

from datetime import datetime

from pydantic import BaseModel, Field


class KeepStatusResponse(BaseModel):
    """Current state of the user's Google Keep connection."""

    connected: bool = Field(..., description="Whether the user has an active Keep connection")
    google_email: str | None = Field(None, alias="googleEmail", serialization_alias="googleEmail")
    last_sync_at: datetime | None = Field(None, alias="lastSyncAt", serialization_alias="lastSyncAt")
    last_error: str | None = Field(None, alias="lastError", serialization_alias="lastError")

    model_config = {"populate_by_name": True}


class KeepConnectRequest(BaseModel):
    """Request to link a Google Keep account via a manually-obtained master token."""

    email: str = Field(..., min_length=3, max_length=255, description="Google account email")
    master_token: str = Field(..., alias="masterToken", serialization_alias="masterToken", min_length=10, description="gpsoauth master token")
    device_id: str | None = Field(None, alias="deviceId", serialization_alias="deviceId", description="Device ID for gkeepapi (generated if omitted)")

    model_config = {"populate_by_name": True}


class KeepMirrorCreateRequest(BaseModel):
    """Request to mirror a shopping list into a new Keep checklist note."""

    shopping_list_id: str = Field(..., alias="shoppingListId", serialization_alias="shoppingListId")
    create_new_note: bool = Field(default=True, alias="createNewNote", serialization_alias="createNewNote")

    model_config = {"populate_by_name": True}


class KeepMirrorUpdateRequest(BaseModel):
    """Request to update a mirror's auto-sync setting."""

    auto_sync: bool = Field(..., alias="autoSync", serialization_alias="autoSync")

    model_config = {"populate_by_name": True}


class KeepMirrorResponse(BaseModel):
    """A shopping list <-> Keep checklist note mirror."""

    id: str = Field(..., description="Mirror ID")
    shopping_list_id: str = Field(..., alias="shoppingListId", serialization_alias="shoppingListId")
    keep_note_id: str = Field(..., alias="keepNoteId", serialization_alias="keepNoteId")
    auto_sync: bool = Field(..., alias="autoSync", serialization_alias="autoSync")
    last_pushed_at: datetime | None = Field(None, alias="lastPushedAt", serialization_alias="lastPushedAt")

    model_config = {"populate_by_name": True}


class KeepMirrorsResponse(BaseModel):
    """List of the user's Keep mirrors."""

    mirrors: list[KeepMirrorResponse] = Field(default_factory=list)


class KeepSyncAllResultItem(BaseModel):
    """Outcome of pushing a single mirror during a sync-all run."""

    mirror_id: str = Field(..., alias="mirrorId", serialization_alias="mirrorId")
    success: bool = Field(...)
    error: str | None = Field(None)

    model_config = {"populate_by_name": True}


class KeepSyncAllResponse(BaseModel):
    """Result of pushing all of a user's auto-sync mirrors."""

    results: list[KeepSyncAllResultItem] = Field(default_factory=list)
