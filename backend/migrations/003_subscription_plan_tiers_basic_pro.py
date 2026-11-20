"""Migration: billing tables + plan_tier free/basic/pro.

Creates subscriptions / stripe_webhook_events / subscription_history if missing
(family-recipes never had gear-stack migration 047). Aligns plan_tier CHECK with
monetization plan (docs/plans/2026-08-03-monetization-stripe.md).

Usage:
    python migrations/003_subscription_plan_tiers_basic_pro.py upgrade
    python migrations/003_subscription_plan_tiers_basic_pro.py downgrade
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
    return bool(result.scalar())


async def upgrade() -> None:
    print("Ensuring billing tables + plan_tier free/basic/pro...")

    async with engine.begin() as conn:
        if not await table_exists(conn, "subscriptions"):
            await conn.execute(
                text(
                    """
                    CREATE TABLE subscriptions (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        user_id VARCHAR(36) NOT NULL UNIQUE,
                        stripe_customer_id VARCHAR(255),
                        stripe_subscription_id VARCHAR(255) UNIQUE,
                        stripe_price_id VARCHAR(255),
                        plan_tier VARCHAR(20) NOT NULL DEFAULT 'free',
                        billing_interval VARCHAR(10),
                        status VARCHAR(20) NOT NULL DEFAULT 'active',
                        current_period_start TIMESTAMP WITH TIME ZONE,
                        current_period_end TIMESTAMP WITH TIME ZONE,
                        cancel_at_period_end BOOLEAN DEFAULT FALSE,
                        canceled_at TIMESTAMP WITH TIME ZONE,
                        is_grandfathered BOOLEAN DEFAULT FALSE,
                        created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                        updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                        CONSTRAINT fk_subscriptions_user
                            FOREIGN KEY (user_id)
                            REFERENCES users(id)
                            ON DELETE CASCADE,
                        CONSTRAINT valid_plan_tier
                            CHECK (plan_tier IN ('free', 'basic', 'pro')),
                        CONSTRAINT valid_billing_interval
                            CHECK (billing_interval IN ('month', 'year')),
                        CONSTRAINT valid_status
                            CHECK (status IN ('active', 'canceled', 'past_due', 'unpaid', 'incomplete', 'trialing'))
                    )
                    """
                )
            )
            await conn.execute(text("CREATE INDEX idx_subscriptions_user_id ON subscriptions(user_id)"))
            await conn.execute(text("CREATE INDEX idx_subscriptions_stripe_customer_id ON subscriptions(stripe_customer_id)"))
            await conn.execute(text("CREATE INDEX idx_subscriptions_stripe_subscription_id ON subscriptions(stripe_subscription_id)"))
            await conn.execute(text("CREATE INDEX idx_subscriptions_plan_tier ON subscriptions(plan_tier)"))
            await conn.execute(text("CREATE INDEX idx_subscriptions_status ON subscriptions(status)"))
            print("✓ Created subscriptions table")
        else:
            await conn.execute(
                text(
                    """
                    UPDATE subscriptions
                    SET plan_tier = 'pro'
                    WHERE plan_tier = 'pro_plus';
                    """
                )
            )
            await conn.execute(text("ALTER TABLE subscriptions DROP CONSTRAINT IF EXISTS valid_plan_tier;"))
            await conn.execute(
                text(
                    """
                    ALTER TABLE subscriptions
                    ADD CONSTRAINT valid_plan_tier
                    CHECK (plan_tier IN ('free', 'basic', 'pro'));
                    """
                )
            )
            print("✓ Updated subscriptions.valid_plan_tier → free/basic/pro")

        if not await table_exists(conn, "stripe_webhook_events"):
            await conn.execute(
                text(
                    """
                    CREATE TABLE stripe_webhook_events (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        stripe_event_id VARCHAR(255) NOT NULL UNIQUE,
                        event_type VARCHAR(100) NOT NULL,
                        payload JSONB NOT NULL,
                        processed BOOLEAN NOT NULL DEFAULT FALSE,
                        processed_at TIMESTAMP WITH TIME ZONE,
                        error_message TEXT,
                        created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
                    )
                    """
                )
            )
            await conn.execute(text("CREATE INDEX idx_webhook_events_event_id ON stripe_webhook_events(stripe_event_id)"))
            await conn.execute(text("CREATE INDEX idx_webhook_events_processed ON stripe_webhook_events(processed)"))
            await conn.execute(text("CREATE INDEX idx_webhook_events_event_type ON stripe_webhook_events(event_type)"))
            print("✓ Created stripe_webhook_events table")

        if not await table_exists(conn, "subscription_history"):
            await conn.execute(
                text(
                    """
                    CREATE TABLE subscription_history (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        subscription_id UUID,
                        user_id VARCHAR(36) NOT NULL,
                        event_type VARCHAR(50) NOT NULL,
                        old_status VARCHAR(20),
                        new_status VARCHAR(20) NOT NULL,
                        old_plan_tier VARCHAR(20),
                        new_plan_tier VARCHAR(20) NOT NULL,
                        event_metadata JSONB,
                        created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                        CONSTRAINT fk_subscription_history_subscription
                            FOREIGN KEY (subscription_id)
                            REFERENCES subscriptions(id)
                            ON DELETE CASCADE,
                        CONSTRAINT fk_subscription_history_user
                            FOREIGN KEY (user_id)
                            REFERENCES users(id)
                            ON DELETE CASCADE
                    )
                    """
                )
            )
            await conn.execute(text("CREATE INDEX idx_subscription_history_subscription_id ON subscription_history(subscription_id)"))
            await conn.execute(text("CREATE INDEX idx_subscription_history_user_id ON subscription_history(user_id)"))
            await conn.execute(text("CREATE INDEX idx_subscription_history_event_type ON subscription_history(event_type)"))
            print("✓ Created subscription_history table")

    print("Done.")


async def downgrade() -> None:
    print("Downgrade not supported for billing table creation (keeps tables).")
    print("To revert plan_tier CHECK only when table pre-existed with legacy constraint, run SQL manually.")


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in ("upgrade", "downgrade"):
        print("Usage: python migrations/003_subscription_plan_tiers_basic_pro.py [upgrade|downgrade]")
        sys.exit(1)
    asyncio.run(upgrade() if sys.argv[1] == "upgrade" else downgrade())
