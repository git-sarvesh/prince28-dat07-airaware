from fastapi import FastAPI

from airaware.api.errors import install_error_handlers
from airaware.api.middleware import RequestLogMiddleware
from airaware.api.routes import documents, health
from airaware.config import Settings
from airaware.logging_setup import setup_logging
from airaware.store import DocumentStore


def create_app(settings: Settings | None = None) -> FastAPI:
    cfg = settings or Settings()
    setup_logging(cfg.log_level)

    app = FastAPI(title=cfg.app_name, version="0.1.0")
    app.state.settings = cfg
    app.state.store = DocumentStore(cfg.data_file_path)

    app.add_middleware(RequestLogMiddleware)
    install_error_handlers(app)

    app.include_router(health.router)
    app.include_router(documents.router, prefix="/v1")
    return app
