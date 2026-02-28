import uvicorn
from fastapi import FastAPI
from api import router
from lifespan import lifespan

app = FastAPI(
    title="Users API",
    description="Мікросервіс для створення користувачів",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=5000)
