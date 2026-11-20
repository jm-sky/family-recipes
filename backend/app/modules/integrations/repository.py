"""Repository for the integrations module (Google Keep sync)."""

from datetime import UTC, datetime

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.id_utils import generate_id
from app.core.database import get_db
from app.modules.integrations.db_models import KeepConnectionDB, KeepListMirrorDB


class IntegrationsRepository:
    """Data access layer for Keep connections and list mirrors."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ==================== Connections ====================

    async def get_connection(self, user_id: str) -> KeepConnectionDB | None:
        stmt = select(KeepConnectionDB).where(KeepConnectionDB.user_id == user_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_connection(
        self,
        *,
        user_id: str,
        google_email: str,
        encrypted_master_token: str,
        device_id: str,
    ) -> KeepConnectionDB:
        connection = KeepConnectionDB(
            id=generate_id(),
            user_id=user_id,
            google_email=google_email,
            encrypted_master_token=encrypted_master_token,
            device_id=device_id,
        )
        self.db.add(connection)
        await self.db.commit()
        await self.db.refresh(connection)
        return connection

    async def update_connection_credentials(
        self,
        connection: KeepConnectionDB,
        *,
        google_email: str,
        encrypted_master_token: str,
        device_id: str,
    ) -> None:
        connection.google_email = google_email
        connection.encrypted_master_token = encrypted_master_token
        connection.device_id = device_id
        connection.updated_at = datetime.now(UTC)
        await self.db.commit()

    async def update_connection_sync_result(
        self,
        connection: KeepConnectionDB,
        *,
        last_error: str | None,
    ) -> None:
        connection.last_sync_at = datetime.now(UTC)
        connection.last_error = last_error
        await self.db.commit()

    async def delete_connection(self, connection: KeepConnectionDB) -> None:
        await self.db.delete(connection)
        await self.db.commit()

    # ==================== Mirrors ====================

    async def list_mirrors(self, user_id: str) -> list[KeepListMirrorDB]:
        stmt = select(KeepListMirrorDB).where(KeepListMirrorDB.user_id == user_id).order_by(KeepListMirrorDB.created_at)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def list_auto_sync_mirrors(self, user_id: str) -> list[KeepListMirrorDB]:
        stmt = select(KeepListMirrorDB).where(KeepListMirrorDB.user_id == user_id, KeepListMirrorDB.auto_sync.is_(True))
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_mirror(self, mirror_id: str, user_id: str) -> KeepListMirrorDB | None:
        stmt = select(KeepListMirrorDB).where(KeepListMirrorDB.id == mirror_id, KeepListMirrorDB.user_id == user_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_mirror_by_list(self, shopping_list_id: str, user_id: str) -> KeepListMirrorDB | None:
        stmt = select(KeepListMirrorDB).where(
            KeepListMirrorDB.shopping_list_id == shopping_list_id,
            KeepListMirrorDB.user_id == user_id,
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_mirror(
        self,
        *,
        user_id: str,
        shopping_list_id: str,
        keep_note_id: str,
    ) -> KeepListMirrorDB:
        mirror = KeepListMirrorDB(
            id=generate_id(),
            user_id=user_id,
            shopping_list_id=shopping_list_id,
            keep_note_id=keep_note_id,
        )
        self.db.add(mirror)
        await self.db.commit()
        await self.db.refresh(mirror)
        return mirror

    async def update_mirror_auto_sync(self, mirror: KeepListMirrorDB, auto_sync: bool) -> None:
        mirror.auto_sync = auto_sync
        await self.db.commit()

    async def touch_mirror_pushed(self, mirror: KeepListMirrorDB) -> None:
        mirror.last_pushed_at = datetime.now(UTC)
        await self.db.commit()

    async def delete_mirror(self, mirror: KeepListMirrorDB) -> None:
        await self.db.delete(mirror)
        await self.db.commit()


def get_integrations_repository(db: AsyncSession = Depends(get_db)) -> IntegrationsRepository:
    """FastAPI dependency to obtain an integrations repository."""
    return IntegrationsRepository(db)
