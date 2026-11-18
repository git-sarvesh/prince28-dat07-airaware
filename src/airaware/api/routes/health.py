from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from airaware.api.deps import get_session, get_settings
from airaware.config import Settings
from airaware.db.models import Document

router = APIRouter(tags=["system"])


@router.get("/health")
def health(settings: Settings = Depends(get_settings)) -> dict:
    return {"status": "ok", "service": settings.app_name, "env": settings.app_env}


@router.get("/ready")
async def ready(session: AsyncSession = Depends(get_session)):
    try:
        count = (await session.execute(select(func.count()).select_from(Document))).scalar_one()
    except Exception as exc:
        return JSONResponse(
            status_code=503,
            content={"status": "not_ready", "reason": f"database unavailable: {exc}"},
        )

    if count < 5:
        return JSONResponse(
            status_code=503,
            content={
                "status": "not_ready",
                "reason": f"need at least 5 records, found {count}",
            },
        )
    return {"status": "ready", "records": count}
