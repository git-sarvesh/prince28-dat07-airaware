from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from airaware.config import Settings
from airaware.main import create_app


@pytest.fixture()
def client() -> Iterator[TestClient]:
    base = Settings()
    settings = Settings(
        app_name="AirAware-Test",
        app_env="local",
        log_level="WARNING",
        database_url=base.database_url,
    )
    app = create_app(settings=settings)
    with TestClient(app) as test_client:
        yield test_client
