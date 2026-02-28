from collections.abc import AsyncGenerator

import httpx
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from core.config import settings


def _get_state_service(request: Request, service_name: str):
    if not hasattr(request.app.state, service_name):
        raise HTTPException(
            status_code=500,
            detail=f"Service '{service_name}' is not initialized in app state."
        )
    return getattr(request.app.state, service_name)


async def get_db_session(request: Request) -> AsyncGenerator[AsyncSession, None]:
    _get_state_service(request, "db")
    db_manager = request.app.state.db

    async with db_manager.session() as session:
        yield session


async def get_users_client():
    async with httpx.AsyncClient(
        base_url=f"http://{settings.USERS_SERVICE_HOST}:{settings.USERS_SERVICE_PORT}",
        timeout=60.0
    ) as client:
        yield client
