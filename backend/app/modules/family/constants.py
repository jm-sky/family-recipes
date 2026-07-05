"""Constants for the family module."""

# Member limits per plan; None means unlimited
PLAN_MEMBER_LIMITS: dict[str, int | None] = {
    "free": 2,
    "basic": 5,
    "pro": None,
}

DEFAULT_PLAN = "free"

# Invitation link validity
INVITATION_EXPIRES_DAYS = 7
