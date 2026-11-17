from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from airaware.api.main import create_app
from airaware.config import Settings


def test_health_ok(client: TestClient) -> None:
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok", "service": "AirAware-Test", "env": "local"}
    assert "X-Request-Id" in res.headers


def test_ready_ok_when_five_records_present(client: TestClient) -> None:
    res = client.get("/ready")
    assert res.status_code == 200
    assert res.json() == {"status": "ready", "records": 5}


def test_ready_returns_503_when_records_missing(tmp_path: Path) -> None:
    empty = tmp_path / "empty.json"
    empty.write_text("[]", encoding="utf-8")
    app = create_app(
        Settings(
            app_name="AirAware-Test",
            app_env="local",
            log_level="WARNING",
            data_file_path=str(empty),
        )
    )
    res = TestClient(app).get("/ready")
    assert res.status_code == 503
    assert res.json()["status"] == "not_ready"


def test_list_documents_returns_all(client: TestClient) -> None:
    res = client.get("/v1/documents")
    assert res.status_code == 200
    body = res.json()
    assert body["count"] == 5
    assert len(body["items"]) == 5


def test_list_documents_search_filters(client: TestClient) -> None:
    res = client.get("/v1/documents", params={"q": "Chennai"})
    assert res.status_code == 200
    body = res.json()
    assert body["count"] == 1
    assert body["items"][0]["id"] == "005"


def test_list_documents_invalid_limit_returns_error_shape(client: TestClient) -> None:
    res = client.get("/v1/documents", params={"limit": 0})
    assert res.status_code == 422
    err = res.json()["error"]
    assert err["code"] == "validation_error"
    assert "request_id" in err


def test_get_document_by_id(client: TestClient) -> None:
    res = client.get("/v1/documents/001")
    assert res.status_code == 200
    assert res.json()["pollutant"] == "PM2.5"


def test_get_document_not_found_has_request_id(client: TestClient) -> None:
    res = client.get("/v1/documents/999", headers={"X-Request-Id": "req-abc"})
    assert res.status_code == 404
    assert res.json() == {
        "error": {
            "code": "not_found",
            "message": "Record '999' does not exist.",
            "request_id": "req-abc",
        }
    }


def test_settings_fail_fast_when_required_var_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("APP_NAME", raising=False)
    monkeypatch.delenv("DATA_FILE_PATH", raising=False)
    with pytest.raises(ValidationError):
        Settings(_env_file=None)
