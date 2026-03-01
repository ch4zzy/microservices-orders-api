import uvicorn
from fastapi import FastAPI
from loguru import logger
from prometheus_fastapi_instrumentator import Instrumentator

from utils.logging import logger
from api import router
from lifespan import lifespan

app = FastAPI(
    title="Orders API",
    description="Мікросервіс для створення замовлень",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(router)

instrumentator = Instrumentator(
    should_group_status_codes=False,
    should_ignore_untemplated=True,
    should_respect_env_var=True,
    should_instrument_requests_inprogress=True,
    excluded_handlers=["/metrics"],
    env_var_name="ENABLE_METRICS",
)
instrumentator.instrument(app).expose(app, endpoint="/metrics")


@app.get("/health")
def health_check():
    logger.info("Health check endpoint called")
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=5000)
