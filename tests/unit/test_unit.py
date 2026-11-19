from collections.abc import AsyncIterator

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError
from sqlalchemy.exc import ArgumentError

from airaware.api.deps import get_session
from airaware.config import Settings
from airaware.main import create_app


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
