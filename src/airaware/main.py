from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from airaware.api.errors import install_error_handlers
from airaware.api.middleware import RequestLogMiddleware
from airaware.api.routes import documents, health
from airaware.config import Settings
from airaware.db.session import make_engine, make_sessionmaker
from airaware.logging_setup import setup_logging


def create_app(settings: Settings | None = None) -> FastAPI:
    cfg = settings or Settings()
    setup_logging(cfg.log_level)

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        engine = make_engine(cfg)
        app.state.engine = engine
        app.state.sessionmaker = make_sessionmaker(engine)
        try:
            yield
        finally:
            await engine.dispose()

    app = FastAPI(title=cfg.app_name, version="0.1.0", lifespan=lifespan)
    app.state.settings = cfg

    app.add_middleware(RequestLogMiddleware)
    install_error_handlers(app)

    app.include_router(health.router)
    app.include_router(documents.router, prefix="/v1")
    return app
