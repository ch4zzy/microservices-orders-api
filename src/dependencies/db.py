import json
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import AsyncGenerator

import pydantic.json
from loguru import logger
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from core.config import settings


@dataclass
class DatabaseConfig:
    host: str = settings.POSTGRES_HOST
    port: int = settings.POSTGRES_PORT
    database: str = settings.POSTGRES_DB
    user: str = settings.POSTGRES_USER
    password: str = settings.POSTGRES_PASSWORD

    @property
    def url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.user}:{self.password}"
            f"@{self.host}:{self.port}/{self.database}"
        )


def _custom_json_serializer(*args, **kwargs) -> str:
    return json.dumps(*args, default=pydantic.json.pydantic_encoder, **kwargs)


class DatabaseManager:
    def __init__(self, config: DatabaseConfig):
        self.config = config

        self.engine: AsyncEngine = create_async_engine(
            self.config.url,
            poolclass=NullPool,
            echo=False,
            json_serializer=_custom_json_serializer,
        )

        self.session_factory = async_sessionmaker(
            bind=self.engine,
            expire_on_commit=False,
            autoflush=False,
            class_=AsyncSession
        )

    async def connect(self):
        try:
            async with self.engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            logger.info(f"Database connection established: {self.config.host}:{self.config.port}")

        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise e

    async def close(self):
        await self.engine.dispose()
        logger.info("Database connection closed.")


    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        async with self.session_factory() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
