from fastapi import APIRouter

from api.v1.order import router as order_router

router = APIRouter(prefix="/v1", tags=["v1"])
router.include_router(order_router)
