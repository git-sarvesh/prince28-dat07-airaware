from fastapi import APIRouter, Depends, HTTPException, Query

from airaware.api.deps import get_store
from airaware.store import DocumentStore

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("")
def list_documents(
    q: str | None = Query(default=None, max_length=100),
    limit: int = Query(default=20, ge=1, le=100),
    store: DocumentStore = Depends(get_store),
) -> dict:
    items = store.list_records(q=q, limit=limit)
    return {"count": len(items), "items": items}


@router.get("/{record_id}")
def get_document(record_id: str, store: DocumentStore = Depends(get_store)) -> dict:
    record = store.get(record_id)
    if record is None:
        raise HTTPException(
            status_code=404,
            detail={"code": "not_found", "message": f"Record '{record_id}' does not exist."},
        )
    return record
