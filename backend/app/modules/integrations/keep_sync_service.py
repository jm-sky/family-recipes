"""Service for one-way shopping list -> Google Keep sync."""

import asyncio
from decimal import Decimal

from app.modules.integrations.db_models import KeepConnectionDB, KeepListMirrorDB
from app.modules.integrations.exceptions import KeepMirrorNotFoundError, KeepNotConnectedError
from app.modules.integrations.keep_client import KeepClient, generate_device_id
from app.modules.integrations.repository import IntegrationsRepository
from app.modules.integrations.schemas import (
    KeepConnectRequest,
    KeepMirrorResponse,
    KeepStatusResponse,
    KeepSyncAllResultItem,
)
from app.modules.integrations.utils.encryption import decrypt_master_token, encrypt_master_token
from app.modules.shopping.repository import ShoppingRepository


def format_item_line(name: str, quantity: Decimal | None, unit: str | None) -> str:
    """Format a shopping item as a single Keep checklist line.

    Examples: "mleko", "mleko 1", "maka 2 szklanki" (trailing zeros/decimal
    point stripped from quantity, per docs/plans/2026-07-07-keep-export.md).

    Args:
        name: Item name
        quantity: Optional quantity
        unit: Optional unit

    Returns:
        Formatted checklist line
    """
    if quantity is None and not unit:
        return name.strip()
    parts = [name.strip()]
    if quantity is not None:
        parts.append(str(quantity).rstrip("0").rstrip("."))
    if unit:
        parts.append(unit)
    return " ".join(parts)


class KeepSyncService:
    """Orchestrates Keep connections and one-way list->note pushes."""

    def __init__(
        self,
        repository: IntegrationsRepository,
        shopping_repository: ShoppingRepository,
        keep_client: KeepClient,
    ):
        self.repository = repository
        self.shopping_repository = shopping_repository
        self.keep_client = keep_client

    def _to_status(self, connection: KeepConnectionDB | None) -> KeepStatusResponse:
        if connection is None:
            return KeepStatusResponse.model_validate({"connected": False, "googleEmail": None, "lastSyncAt": None, "lastError": None})
        return KeepStatusResponse.model_validate(
            {
                "connected": True,
                "googleEmail": connection.google_email,
                "lastSyncAt": connection.last_sync_at,
                "lastError": connection.last_error,
            }
        )

    def _to_mirror_response(self, mirror: KeepListMirrorDB) -> KeepMirrorResponse:
        return KeepMirrorResponse.model_validate(
            {
                "id": mirror.id,
                "shoppingListId": mirror.shopping_list_id,
                "keepNoteId": mirror.keep_note_id,
                "autoSync": mirror.auto_sync,
                "lastPushedAt": mirror.last_pushed_at,
            }
        )

    async def get_status(self, user_id: str) -> KeepStatusResponse:
        """Get the user's current Keep connection status."""
        connection = await self.repository.get_connection(user_id)
        return self._to_status(connection)

    async def connect(self, user_id: str, payload: KeepConnectRequest) -> KeepStatusResponse:
        """Link (or relink) the user's Google Keep account.

        Validates the master token by authenticating against Google before
        persisting it encrypted.

        Args:
            user_id: User ID
            payload: Email, master token, optional device ID

        Returns:
            Updated connection status

        Raises:
            KeepAuthenticationError: If the master token is rejected by Google
        """
        device_id = payload.device_id or generate_device_id()
        await asyncio.to_thread(self.keep_client.authenticate, payload.email, payload.master_token, device_id)

        encrypted = encrypt_master_token(payload.master_token)
        existing = await self.repository.get_connection(user_id)
        if existing:
            await self.repository.update_connection_credentials(
                existing,
                google_email=payload.email,
                encrypted_master_token=encrypted,
                device_id=device_id,
            )
            connection = existing
        else:
            connection = await self.repository.create_connection(
                user_id=user_id,
                google_email=payload.email,
                encrypted_master_token=encrypted,
                device_id=device_id,
            )
        return self._to_status(connection)

    async def disconnect(self, user_id: str) -> None:
        """Remove the user's Keep connection and all of their mirrors.

        Does not delete the notes from Google Keep itself.

        Args:
            user_id: User ID
        """
        connection = await self.repository.get_connection(user_id)
        if not connection:
            return
        for mirror in await self.repository.list_mirrors(user_id):
            await self.repository.delete_mirror(mirror)
        await self.repository.delete_connection(connection)

    async def list_mirrors(self, user_id: str) -> list[KeepMirrorResponse]:
        """List the user's shopping-list <-> Keep note mirrors."""
        mirrors = await self.repository.list_mirrors(user_id)
        return [self._to_mirror_response(m) for m in mirrors]

    async def create_mirror(self, user_id: str, shopping_list_id: str) -> KeepMirrorResponse:
        """Create a new Keep checklist note for a shopping list and do the first push.

        Args:
            user_id: User ID
            shopping_list_id: Shopping list to mirror

        Returns:
            The created mirror

        Raises:
            KeepNotConnectedError: If the user has no Keep connection
        """
        connection = await self.repository.get_connection(user_id)
        if not connection:
            raise KeepNotConnectedError(f"User {user_id} has no Google Keep connection")

        shopping_list = await self.shopping_repository.get_list(shopping_list_id, connection.user_id)
        title = f"Zakupy: {shopping_list.name}" if shopping_list else "Zakupy"

        master_token = decrypt_master_token(connection.encrypted_master_token)
        keep = await asyncio.to_thread(self.keep_client.authenticate, connection.google_email, master_token, connection.device_id)
        note = await asyncio.to_thread(self.keep_client.find_or_create_note, keep, title)
        await asyncio.to_thread(self.keep_client.sync, keep)

        mirror = await self.repository.create_mirror(
            user_id=user_id,
            shopping_list_id=shopping_list_id,
            keep_note_id=note.id,
        )
        await self.push_list(user_id, shopping_list_id)
        return self._to_mirror_response(mirror)

    async def update_mirror(self, user_id: str, mirror_id: str, auto_sync: bool) -> KeepMirrorResponse:
        """Update a mirror's auto-sync flag.

        Raises:
            KeepMirrorNotFoundError: If the mirror doesn't exist for this user
        """
        mirror = await self.repository.get_mirror(mirror_id, user_id)
        if not mirror:
            raise KeepMirrorNotFoundError(f"Mirror {mirror_id} not found")
        await self.repository.update_mirror_auto_sync(mirror, auto_sync)
        return self._to_mirror_response(mirror)

    async def delete_mirror(self, user_id: str, mirror_id: str) -> None:
        """Delete a mirror (the Keep note itself is left untouched).

        Raises:
            KeepMirrorNotFoundError: If the mirror doesn't exist for this user
        """
        mirror = await self.repository.get_mirror(mirror_id, user_id)
        if not mirror:
            raise KeepMirrorNotFoundError(f"Mirror {mirror_id} not found")
        await self.repository.delete_mirror(mirror)

    async def push_list(self, user_id: str, shopping_list_id: str) -> KeepMirrorResponse:
        """Push the current state of a shopping list to its Keep mirror (full rebuild).

        Args:
            user_id: User ID
            shopping_list_id: Shopping list to push

        Returns:
            The mirror, with updated last_pushed_at

        Raises:
            KeepNotConnectedError: If the user has no Keep connection
            KeepMirrorNotFoundError: If no mirror exists for this list
        """
        connection = await self.repository.get_connection(user_id)
        if not connection:
            raise KeepNotConnectedError(f"User {user_id} has no Google Keep connection")

        mirror = await self.repository.get_mirror_by_list(shopping_list_id, user_id)
        if not mirror:
            raise KeepMirrorNotFoundError(f"No Keep mirror for list {shopping_list_id}")

        try:
            items = await self.shopping_repository.list_items(shopping_list_id)
            lines = [(format_item_line(item.name, item.quantity, item.unit), item.is_checked) for item in items]

            master_token = decrypt_master_token(connection.encrypted_master_token)
            keep = await asyncio.to_thread(self.keep_client.authenticate, connection.google_email, master_token, connection.device_id)
            note = await asyncio.to_thread(self.keep_client.get_note, keep, mirror.keep_note_id)
            await asyncio.to_thread(self.keep_client.rebuild_checklist, note, lines)
            await asyncio.to_thread(self.keep_client.sync, keep)
        except Exception as e:
            await self.repository.update_connection_sync_result(connection, last_error=str(e))
            raise

        await self.repository.update_connection_sync_result(connection, last_error=None)
        await self.repository.touch_mirror_pushed(mirror)
        return self._to_mirror_response(mirror)

    async def sync_mirror_by_id(self, user_id: str, mirror_id: str) -> KeepMirrorResponse:
        """Push a mirror's list now, looked up by mirror ID.

        Raises:
            KeepMirrorNotFoundError: If the mirror doesn't exist for this user
            KeepNotConnectedError: If the user has no Keep connection
        """
        mirror = await self.repository.get_mirror(mirror_id, user_id)
        if not mirror:
            raise KeepMirrorNotFoundError(f"Mirror {mirror_id} not found")
        return await self.push_list(user_id, mirror.shopping_list_id)

    async def sync_all(self, user_id: str) -> list[KeepSyncAllResultItem]:
        """Push all of a user's auto-sync mirrors, collecting per-mirror errors.

        Args:
            user_id: User ID

        Returns:
            Per-mirror success/error results
        """
        results: list[KeepSyncAllResultItem] = []
        for mirror in await self.repository.list_auto_sync_mirrors(user_id):
            try:
                await self.push_list(user_id, mirror.shopping_list_id)
                results.append(KeepSyncAllResultItem.model_validate({"mirrorId": mirror.id, "success": True, "error": None}))
            except Exception as e:
                results.append(KeepSyncAllResultItem.model_validate({"mirrorId": mirror.id, "success": False, "error": str(e)}))
        return results
