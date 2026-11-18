from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from airaware.api.deps import get_session
from airaware.db.models import Document

router = APIRouter(prefix="/documents", tags=["documents"])


def _serialize(doc: Document) -> dict[str, Any]:
    return {
        "id": doc.external_id,
        "title": doc.title,
        "source_url": doc.source_url,
        "licence": doc.licence,
        "doc_type": doc.doc_type,
        "published_on": doc.published_on.isoformat() if doc.published_on else None,
        **(doc.metadata_ or {}),
    }


@router.get("")
async def list_documents(
    q: str | None = Query(default=None, max_length=100),
    limit: int = Query(default=20, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
) -> dict:
    stmt = select(Document).order_by(Document.id)
    if q:
        pattern = f"%{q}%"
        stmt = stmt.where(
            or_(
                Document.title.ilike(pattern),
                Document.external_id.ilike(pattern),
            )
        )
    stmt = stmt.limit(limit)
    docs = (await session.execute(stmt)).scalars().all()
    items = [_serialize(doc) for doc in docs]
    return {"count": len(items), "items": items}


@router.get("/{record_id}")
async def get_document(
    record_id: str,
    session: AsyncSession = Depends(get_session),
) -> dict:
    doc = (
        await session.execute(select(Document).where(Document.external_id == record_id))
    ).scalar_one_or_none()
    if doc is None:
        raise HTTPException(
            status_code=404,
            detail={"code": "not_found", "message": f"Record '{record_id}' does not exist."},
        )
    return _serialize(doc)
