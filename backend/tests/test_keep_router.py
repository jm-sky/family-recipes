"""Integration tests for the Google Keep integration router.

Focused on the feature-flag gate (KEEP_SYNC_ENABLED) and basic wiring — not
real Google Keep protocol behavior, which requires a live account (see
docs/plans/2026-07-07-keep-export.md verification section).
"""

from collections.abc import Generator
from datetime import UTC, datetime

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.core.config import settings
from app.core.csrf import CSRF_COOKIE_NAME, CSRF_HEADER_NAME
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.integrations.router import get_keep_sync_service
from app.modules.integrations.schemas import KeepStatusResponse
from main import app


def _csrf_headers(client: TestClient) -> dict[str, str]:
    response = client.get("/api/auth/csrf-token")
    assert response.status_code == status.HTTP_200_OK
    token = response.cookies.get(CSRF_COOKIE_NAME) or response.json()["csrf_token"]
    return {CSRF_HEADER_NAME: token}


@pytest.fixture
def sample_user() -> User:
    return User(
        id="user-123",
        email="test@example.com",
        name="Test User",
        hashedPassword="hashed",
        isActive=True,
        isEmailVerified=True,
        createdAt=datetime.now(UTC),
    )


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


class TestFeatureFlagGate:
    """When KEEP_SYNC_ENABLED=false, every endpoint must 503."""

    def test_status_endpoint_503_when_disabled(self, client: TestClient, monkeypatch: pytest.MonkeyPatch, sample_user: User) -> None:
        monkeypatch.setattr(settings.keep, "enabled", False)
        app.dependency_overrides[get_current_user] = lambda: sample_user

        response = client.get("/api/integrations/keep/status")

        assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE

    def test_connect_endpoint_503_when_disabled(self, client: TestClient, monkeypatch: pytest.MonkeyPatch, sample_user: User) -> None:
        monkeypatch.setattr(settings.keep, "enabled", False)
        app.dependency_overrides[get_current_user] = lambda: sample_user

        response = client.post(
            "/api/integrations/keep/connect",
            json={"email": "user@gmail.com", "masterToken": "sometoken12"},
            headers=_csrf_headers(client),
        )

        assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE


class TestStatusEndpoint:
    """With the flag enabled, /status should reflect the service response."""

    def test_status_returns_service_result(self, client: TestClient, monkeypatch: pytest.MonkeyPatch, sample_user: User) -> None:
        monkeypatch.setattr(settings.keep, "enabled", True)
        app.dependency_overrides[get_current_user] = lambda: sample_user

        async def fake_get_status(user_id: str) -> KeepStatusResponse:
            assert user_id == sample_user.id
            return KeepStatusResponse(connected=False, google_email=None, last_sync_at=None, last_error=None)

        class FakeService:
            get_status = staticmethod(fake_get_status)

        app.dependency_overrides[get_keep_sync_service] = lambda: FakeService()

        response = client.get("/api/integrations/keep/status")

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "connected": False,
            "googleEmail": None,
            "lastSyncAt": None,
            "lastError": None,
        }
