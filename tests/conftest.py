import os
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from airaware.config import Settings
from airaware.main import create_app


@pytest.fixture()
def client() -> Iterator[TestClient]:
    db_url = os.environ.get("TEST_DATABASE_URL") or Settings().database_url
    settings = Settings(
        _env_file=None,
        app_name="AirAware-Test",
        app_env="local",
        log_level="WARNING",
        database_url=db_url,
    )
    app = create_app(settings=settings)
    with TestClient(app) as test_client:
        yield test_client
