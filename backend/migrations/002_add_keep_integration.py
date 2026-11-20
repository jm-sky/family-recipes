"""Migration: Add Google Keep integration tables.

Creates keep_connections (per-user Keep account link, encrypted master token)
and keep_list_mirrors (per-user shopping list -> Keep checklist note mapping).
See docs/plans/2026-07-07-keep-export.md for the full spec.

Usage:
    python migrations/002_add_keep_integration.py upgrade
    python migrations/002_add_keep_integration.py downgrade
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text

from app.core.database import engine


async def table_exists(conn, table_name: str) -> bool:
    result = await conn.execute(
        text(
            """
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name = :table_name
            );
        """
        ),
        {"table_name": table_name},
    )
    return result.scalar() is True


async def upgrade() -> None:
    print("Adding Google Keep integration tables...")

    async with engine.begin() as conn:
        if not await table_exists(conn, "keep_connections"):
            await conn.execute(
                text(
                    """
                    CREATE TABLE keep_connections (
                        id VARCHAR(36) PRIMARY KEY,
                        user_id VARCHAR(36) NOT NULL UNIQUE REFERENCES users(id),
                        google_email VARCHAR(255) NOT NULL,
                        encrypted_master_token TEXT NOT NULL,
                        device_id VARCHAR(64) NOT NULL,
                        created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                        updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                        last_sync_at TIMESTAMPTZ NULL,
                        last_error TEXT NULL
                    );
                """
                )
            )
            print("✓ Created keep_connections table")

        if not await table_exists(conn, "keep_list_mirrors"):
            await conn.execute(
                text(
                    """
                    CREATE TABLE keep_list_mirrors (
                        id VARCHAR(36) PRIMARY KEY,
                        user_id VARCHAR(36) NOT NULL REFERENCES users(id),
                        shopping_list_id VARCHAR(36) NOT NULL REFERENCES shopping_lists(id),
                        keep_note_id VARCHAR(128) NOT NULL,
                        auto_sync BOOLEAN NOT NULL DEFAULT true,
                        last_pushed_at TIMESTAMPTZ NULL,
                        created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                        UNIQUE (user_id, shopping_list_id)
                    );
                """
                )
            )
            print("✓ Created keep_list_mirrors table")


async def downgrade() -> None:
    print("Removing Google Keep integration tables...")

    async with engine.begin() as conn:
        if await table_exists(conn, "keep_list_mirrors"):
            await conn.execute(text("DROP TABLE IF EXISTS keep_list_mirrors;"))
            print("✓ Dropped keep_list_mirrors table")

        if await table_exists(conn, "keep_connections"):
            await conn.execute(text("DROP TABLE IF EXISTS keep_connections;"))
            print("✓ Dropped keep_connections table")


async def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Add Google Keep integration tables")
    parser.add_argument("action", choices=["upgrade", "downgrade"])
    args = parser.parse_args()

    if args.action == "upgrade":
        await upgrade()
    else:
        await downgrade()

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
