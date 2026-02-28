from contextlib import asynccontextmanager

from fastapi import FastAPI
from loguru import logger

from dependencies.db import DatabaseManager, DatabaseConfig


@asynccontextmanager
async def lifespan(app: FastAPI):
    db_manager = DatabaseManager(DatabaseConfig())
    await db_manager.connect()

    app.state.db = db_manager

    logger.info("[Lifespan] Services initialized and attached to app.state.")

    yield

    logger.info("[Lifespan] Shutting down services.")

    await db_manager.close()
