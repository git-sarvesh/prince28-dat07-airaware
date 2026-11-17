from fastapi import Request

from airaware.config import Settings
from airaware.store import DocumentStore


def get_settings(request: Request) -> Settings:
    return request.app.state.settings


def get_store(request: Request) -> DocumentStore:
    return request.app.state.store
