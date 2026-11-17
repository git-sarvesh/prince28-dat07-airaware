import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from airaware.api.main import create_app
from airaware.config import Settings

SAMPLE_RECORDS = [
    {
        "id": "001",
        "document": "CPCB NAAQS Notification 2009",
        "city": None,
        "pollutant": "PM2.5",
        "standard_value": 60,
        "averaging_time": "24-hour",
        "target": "60 ug/m3 for Industrial, Residential, Rural and Other Areas",
        "year": 2009,
    },
    {
        "id": "002",
        "document": "CPCB NAAQS Notification 2009",
        "city": None,
        "pollutant": "PM10",
        "standard_value": 100,
        "averaging_time": "24-hour",
        "target": "100 ug/m3 for Industrial, Residential, Rural and Other Areas",
        "year": 2009,
    },
    {
        "id": "003",
        "document": "CPCB NAAQS Notification 2009",
        "city": None,
        "pollutant": "SO2",
        "standard_value": 80,
        "averaging_time": "24-hour",
        "target": "80 ug/m3 for Industrial, Residential, Rural and Other Areas",
        "year": 2009,
    },
    {
        "id": "004",
        "document": "CPCB NAAQS Notification 2009",
        "city": None,
        "pollutant": "CO",
        "standard_value": 2,
        "averaging_time": "8-hour",
        "target": "2 mg/m3 for Industrial, Residential, Rural and Other Areas",
        "year": 2009,
    },
    {
        "id": "005",
        "document": "National Clean Air Programme (NCAP) Guidelines",
        "city": "Chennai",
        "pollutant": "PM10",
        "standard_value": None,
        "averaging_time": "annual",
        "target": "20% to 30% reduction in PM10 concentration by 2024 over 2017-18 baseline",
        "year": 2019,
    },
]


@pytest.fixture()
def data_file(tmp_path: Path) -> Path:
    path = tmp_path / "records.json"
    path.write_text(json.dumps(SAMPLE_RECORDS), encoding="utf-8")
    return path


@pytest.fixture()
def client(data_file: Path) -> TestClient:
    settings = Settings(
        app_name="AirAware-Test",
        app_env="local",
        log_level="WARNING",
        data_file_path=str(data_file),
    )
    app = create_app(settings=settings)
    return TestClient(app)
