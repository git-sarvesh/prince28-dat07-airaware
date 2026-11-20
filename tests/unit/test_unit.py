from collections.abc import AsyncIterator

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError
from sqlalchemy.exc import ArgumentError

from airaware.api.deps import get_session
from airaware.config import Settings
from airaware.main import create_app


def test_health_returns_default_version() -> None:
    app = create_app(
        Settings(
            _env_file=None,
            app_name="airaware",
            app_env="test",
            log_level="WARNING",
        )
    )
    res = TestClient(app).get("/health")
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "ok"
    assert body["env"] == "test"
    assert body["version"] == "dev"


def test_health_reports_configured_git_sha() -> None:
    sha = "abc123def456"
    app = create_app(
        Settings(
            _env_file=None,
            app_name="airaware",
            app_env="production",
            log_level="WARNING",
            git_sha=sha,
        )
    )
    res = TestClient(app).get("/health")
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "ok"
    assert body["env"] == "production"
    assert body["version"] == sha


def test_ready_returns_503_when_records_missing() -> None:
    class _EmptyResult:
        def scalar_one(self) -> int:
            return 0

    class _EmptySession:
        async def execute(self, _stmt) -> _EmptyResult:
            return _EmptyResult()

    async def _override_session() -> AsyncIterator[_EmptySession]:
        yield _EmptySession()

    app = create_app(
        Settings(
            app_name="AirAware-Test",
            app_env="local",
            log_level="WARNING",
        )
    )
    app.dependency_overrides[get_session] = _override_session
    res = TestClient(app).get("/ready")
    assert res.status_code == 503
    assert res.json()["status"] == "not_ready"


def test_settings_rejects_empty_database_url() -> None:
    with pytest.raises((ValidationError, ValueError, ArgumentError)):
        Settings(_env_file=None, database_url="")
