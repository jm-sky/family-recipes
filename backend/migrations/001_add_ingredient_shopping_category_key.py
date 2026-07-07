"""Migration: Add shopping_category_key to ingredients table.

Backfills values from the canonical seed dataset by ingredient name.

Usage:
    python migrations/001_add_ingredient_shopping_category_key.py upgrade
    python migrations/001_add_ingredient_shopping_category_key.py downgrade
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text

from app.core.database import engine
from app.modules.ingredients.seed_data import INGREDIENTS

_CATEGORY_BY_NAME = {seed["name"]: seed["shopping_category_key"] for seed in INGREDIENTS}


async def column_exists(conn, table_name: str, column_name: str) -> bool:
    result = await conn.execute(
        text(
            """
            SELECT EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_schema = 'public'
                AND table_name = :table_name
                AND column_name = :column_name
            );
        """
        ),
        {"table_name": table_name, "column_name": column_name},
    )
    return result.scalar() is True


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
    print("Adding shopping_category_key to ingredients...")

    async with engine.begin() as conn:
        if not await table_exists(conn, "ingredients"):
            print("ingredients table does not exist, skipping...")
            return

        if not await column_exists(conn, "ingredients", "shopping_category_key"):
            await conn.execute(
                text(
                    """
                    ALTER TABLE ingredients
                    ADD COLUMN shopping_category_key VARCHAR(64);
                """
                )
            )
            print("✓ Added shopping_category_key column")

        for name, category_key in _CATEGORY_BY_NAME.items():
            await conn.execute(
                text(
                    """
                    UPDATE ingredients
                    SET shopping_category_key = :category_key
                    WHERE name = :name;
                """
                ),
                {"name": name, "category_key": category_key},
            )

    print("✓ Backfilled shopping_category_key from seed dataset")


async def downgrade() -> None:
    print("Removing shopping_category_key from ingredients...")

    async with engine.begin() as conn:
        if await column_exists(conn, "ingredients", "shopping_category_key"):
            await conn.execute(
                text(
                    """
                    ALTER TABLE ingredients
                    DROP COLUMN IF EXISTS shopping_category_key;
                """
                )
            )
            print("✓ Removed shopping_category_key column")


async def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Add shopping_category_key to ingredients")
    parser.add_argument("action", choices=["upgrade", "downgrade"])
    args = parser.parse_args()

    if args.action == "upgrade":
        await upgrade()
    else:
        await downgrade()

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
