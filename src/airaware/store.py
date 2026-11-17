import json
from pathlib import Path
from typing import Any


class DocumentStore:
    def __init__(self, path: str) -> None:
        self._path = Path(path)
        self._records: list[dict[str, Any]] = []
        if self._path.exists():
            raw = json.loads(self._path.read_text(encoding="utf-8"))
            if isinstance(raw, list):
                self._records = raw

    @property
    def is_ready(self) -> bool:
        return len(self._records) >= 5

    def count(self) -> int:
        return len(self._records)

    def list_records(self, q: str | None = None, limit: int = 20) -> list[dict[str, Any]]:
        items = self._records
        if q:
            needle = q.strip().lower()
            items = [r for r in items if needle in json.dumps(r, ensure_ascii=False).lower()]
        return items[:limit]

    def get(self, record_id: str) -> dict[str, Any] | None:
        for record in self._records:
            if str(record.get("id")) == record_id:
                return record
        return None
