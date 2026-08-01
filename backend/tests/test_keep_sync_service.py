"""Unit tests for the Google Keep sync service."""

from datetime import UTC, datetime
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.modules.integrations.db_models import KeepConnectionDB, KeepListMirrorDB
from app.modules.integrations.exceptions import (
    KeepAuthenticationError,
    KeepMirrorNotFoundError,
    KeepNotConnectedError,
)
from app.modules.integrations.keep_client import KeepClient
from app.modules.integrations.keep_sync_service import KeepSyncService, format_item_line
from app.modules.integrations.repository import IntegrationsRepository
from app.modules.integrations.schemas import KeepConnectRequest
from app.modules.integrations.utils.encryption import encrypt_master_token
from app.modules.shopping.db_models import ShoppingListItemDB
from app.modules.shopping.repository import ShoppingRepository


class TestFormatItemLine:
    """Tests for the Keep checklist line formatter."""

    def test_bare_name(self) -> None:
        assert format_item_line("mleko", None, None) == "mleko"

    def test_with_quantity_only(self) -> None:
        assert format_item_line("jajka", Decimal("6"), None) == "jajka 6"

    def test_with_unit_only(self) -> None:
        assert format_item_line("maka", None, "szklanki") == "maka szklanki"

    def test_with_quantity_and_unit(self) -> None:
        assert format_item_line("mleko", Decimal("1"), "l") == "mleko 1 l"

    def test_strips_trailing_zeros_and_decimal_point(self) -> None:
        assert format_item_line("maka", Decimal("2.00"), "szklanki") == "maka 2 szklanki"

    def test_keeps_meaningful_decimals(self) -> None:
        assert format_item_line("maslo", Decimal("0.50"), "kg") == "maslo 0.5 kg"


@pytest.fixture
def mock_repository() -> AsyncMock:
    return AsyncMock(spec=IntegrationsRepository)


@pytest.fixture
def mock_shopping_repository() -> AsyncMock:
    return AsyncMock(spec=ShoppingRepository)


@pytest.fixture
def mock_keep_client() -> MagicMock:
    """KeepClient methods are synchronous (called via asyncio.to_thread), not async."""
    return MagicMock(spec=KeepClient)


@pytest.fixture
def sync_service(
    mock_repository: AsyncMock,
    mock_shopping_repository: AsyncMock,
    mock_keep_client: MagicMock,
) -> KeepSyncService:
    return KeepSyncService(
        repository=mock_repository,
        shopping_repository=mock_shopping_repository,
        keep_client=mock_keep_client,
    )


@pytest.fixture
def sample_connection() -> KeepConnectionDB:
    return KeepConnectionDB(
        id="conn1",
        user_id="user1",
        google_email="user@gmail.com",
        encrypted_master_token=encrypt_master_token("real-master-token"),
        device_id="deadbeef",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
        last_sync_at=None,
        last_error=None,
    )


@pytest.fixture
def sample_mirror() -> KeepListMirrorDB:
    return KeepListMirrorDB(
        id="mirror1",
        user_id="user1",
        shopping_list_id="list1",
        keep_note_id="note1",
        auto_sync=True,
        last_pushed_at=None,
        created_at=datetime.now(UTC),
    )


def _sample_item(name: str, *, quantity: Decimal | None = None, unit: str | None = None, checked: bool = False) -> ShoppingListItemDB:
    return ShoppingListItemDB(
        id=f"item-{name}",
        list_id="list1",
        name=name,
        category_id=None,
        ingredient_id=None,
        quantity=quantity,
        unit=unit,
        is_checked=checked,
        source_recipe_id=None,
        position=0,
        created_by="user1",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
        deleted_at=None,
    )


class TestConnect:
    """Tests for linking a Google Keep account."""

    @pytest.mark.asyncio
    async def test_connect_creates_new_connection(
        self,
        sync_service: KeepSyncService,
        mock_repository: AsyncMock,
        mock_keep_client: MagicMock,
    ) -> None:
        mock_repository.get_connection.return_value = None
        created = KeepConnectionDB(
            id="conn1",
            user_id="user1",
            google_email="user@gmail.com",
            encrypted_master_token="x",
            device_id="abc123",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
            last_sync_at=None,
            last_error=None,
        )
        mock_repository.create_connection.return_value = created

        payload = KeepConnectRequest(email="user@gmail.com", master_token="sometoken12", device_id="abc123")
        result = await sync_service.connect("user1", payload)

        mock_keep_client.authenticate.assert_called_once_with("user@gmail.com", "sometoken12", "abc123")
        mock_repository.create_connection.assert_called_once()
        assert result.connected is True
        assert result.google_email == "user@gmail.com"

    @pytest.mark.asyncio
    async def test_connect_relinks_existing_connection(
        self,
        sync_service: KeepSyncService,
        mock_repository: AsyncMock,
        sample_connection: KeepConnectionDB,
    ) -> None:
        mock_repository.get_connection.return_value = sample_connection

        payload = KeepConnectRequest(email="user@gmail.com", master_token="newtoken1234", device_id="deadbeef")
        await sync_service.connect("user1", payload)

        mock_repository.update_connection_credentials.assert_called_once()
        mock_repository.create_connection.assert_not_called()

    @pytest.mark.asyncio
    async def test_connect_propagates_authentication_error(
        self,
        sync_service: KeepSyncService,
        mock_repository: AsyncMock,
        mock_keep_client: MagicMock,
    ) -> None:
        mock_repository.get_connection.return_value = None
        mock_keep_client.authenticate.side_effect = KeepAuthenticationError("bad token")

        payload = KeepConnectRequest(email="user@gmail.com", master_token="badtoken123", device_id="abc123")
        with pytest.raises(KeepAuthenticationError):
            await sync_service.connect("user1", payload)


class TestDisconnect:
    """Tests for unlinking a Google Keep account."""

    @pytest.mark.asyncio
    async def test_disconnect_removes_connection_and_mirrors(
        self,
        sync_service: KeepSyncService,
        mock_repository: AsyncMock,
        sample_connection: KeepConnectionDB,
        sample_mirror: KeepListMirrorDB,
    ) -> None:
        mock_repository.get_connection.return_value = sample_connection
        mock_repository.list_mirrors.return_value = [sample_mirror]

        await sync_service.disconnect("user1")

        mock_repository.delete_mirror.assert_called_once_with(sample_mirror)
        mock_repository.delete_connection.assert_called_once_with(sample_connection)

    @pytest.mark.asyncio
    async def test_disconnect_noop_when_not_connected(
        self,
        sync_service: KeepSyncService,
        mock_repository: AsyncMock,
    ) -> None:
        mock_repository.get_connection.return_value = None

        await sync_service.disconnect("user1")

        mock_repository.delete_connection.assert_not_called()


class TestPushList:
    """Tests for the core full-push sync."""

    @pytest.mark.asyncio
    async def test_push_list_maps_items_and_rebuilds_checklist(
        self,
        sync_service: KeepSyncService,
        mock_repository: AsyncMock,
        mock_shopping_repository: AsyncMock,
        mock_keep_client: MagicMock,
        sample_connection: KeepConnectionDB,
        sample_mirror: KeepListMirrorDB,
    ) -> None:
        mock_repository.get_connection.return_value = sample_connection
        mock_repository.get_mirror_by_list.return_value = sample_mirror
        mock_shopping_repository.list_items.return_value = [
            _sample_item("mleko", quantity=Decimal("1.00"), unit="l"),
            _sample_item("jajka", checked=True),
        ]
        mock_note = MagicMock()
        mock_keep_client.get_note.return_value = mock_note

        result = await sync_service.push_list("user1", "list1")

        mock_keep_client.rebuild_checklist.assert_called_once_with(
            mock_note,
            [("mleko 1 l", False), ("jajka", True)],
        )
        mock_keep_client.sync.assert_called_once()
        mock_repository.update_connection_sync_result.assert_called_once_with(sample_connection, last_error=None)
        mock_repository.touch_mirror_pushed.assert_called_once_with(sample_mirror)
        assert result.id == sample_mirror.id

    @pytest.mark.asyncio
    async def test_push_list_raises_when_not_connected(
        self,
        sync_service: KeepSyncService,
        mock_repository: AsyncMock,
    ) -> None:
        mock_repository.get_connection.return_value = None

        with pytest.raises(KeepNotConnectedError):
            await sync_service.push_list("user1", "list1")

    @pytest.mark.asyncio
    async def test_push_list_raises_when_no_mirror(
        self,
        sync_service: KeepSyncService,
        mock_repository: AsyncMock,
        sample_connection: KeepConnectionDB,
    ) -> None:
        mock_repository.get_connection.return_value = sample_connection
        mock_repository.get_mirror_by_list.return_value = None

        with pytest.raises(KeepMirrorNotFoundError):
            await sync_service.push_list("user1", "list1")

    @pytest.mark.asyncio
    async def test_push_list_records_error_and_reraises(
        self,
        sync_service: KeepSyncService,
        mock_repository: AsyncMock,
        mock_shopping_repository: AsyncMock,
        mock_keep_client: MagicMock,
        sample_connection: KeepConnectionDB,
        sample_mirror: KeepListMirrorDB,
    ) -> None:
        mock_repository.get_connection.return_value = sample_connection
        mock_repository.get_mirror_by_list.return_value = sample_mirror
        mock_shopping_repository.list_items.return_value = []
        mock_keep_client.get_note.side_effect = RuntimeError("Keep note not found")

        with pytest.raises(RuntimeError):
            await sync_service.push_list("user1", "list1")

        mock_repository.update_connection_sync_result.assert_called_once_with(sample_connection, last_error="Keep note not found")
