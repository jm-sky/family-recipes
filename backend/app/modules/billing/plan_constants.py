"""Plan tiers and Stripe price mapping for family-recipes billing."""

from typing import Literal

from app.core.config import settings

PlanTier = Literal["free", "basic", "pro"]
PaidPlanTier = Literal["basic", "pro"]

PAID_PLAN_TIERS: tuple[str, ...] = ("basic", "pro")
ALL_PLAN_TIERS: tuple[str, ...] = ("free", "basic", "pro")

# System OpenRouter budget (USD / family / calendar month)
PLAN_AI_COST_LIMIT_USD: dict[str, float] = {
    "free": 0.0,
    "basic": 0.50,
    "pro": 2.0,
}


def get_price_id(plan_tier: str, billing_interval: str) -> str | None:
    """Return Stripe price ID for plan + interval, or None if not configured."""
    price_map = {
        "basic": {
            "monthly": settings.stripe.basic_monthly_price_id,
            "annual": settings.stripe.basic_annual_price_id,
        },
        "pro": {
            "monthly": settings.stripe.pro_monthly_price_id,
            "annual": settings.stripe.pro_annual_price_id,
        },
    }
    tier_prices = price_map.get(plan_tier)
    if not tier_prices:
        return None
    return tier_prices.get(billing_interval) or None


def plan_tier_from_price_id(price_id: str) -> str | None:
    """Map Stripe price ID to plan tier."""
    price_map = {
        settings.stripe.basic_monthly_price_id: "basic",
        settings.stripe.basic_annual_price_id: "basic",
        settings.stripe.pro_monthly_price_id: "pro",
        settings.stripe.pro_annual_price_id: "pro",
    }
    # Ignore empty env placeholders colliding on ""
    if not price_id:
        return None
    for configured_id, tier in price_map.items():
        if configured_id and configured_id == price_id:
            return tier
    return None
