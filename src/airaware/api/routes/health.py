from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from airaware.api.deps import get_settings, get_store
from airaware.config import Settings
from airaware.store import DocumentStore

router = APIRouter(tags=["system"])


@router.get("/health")
def health(settings: Settings = Depends(get_settings)) -> dict:
    return {"status": "ok", "service": settings.app_name, "env": settings.app_env}


@router.get("/ready")
def ready(store: DocumentStore = Depends(get_store)):
    if not store.is_ready:
        return JSONResponse(
            status_code=503,
            content={
                "status": "not_ready",
                "reason": f"need at least 5 records, found {store.count()}",
            },
        )
    return {"status": "ready", "records": store.count()}
