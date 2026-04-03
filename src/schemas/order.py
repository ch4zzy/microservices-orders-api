from typing import Optional

from pydantic import BaseModel


class OrderBase(BaseModel):
    name: str
    quantity: int


class OrderResponse(OrderBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True


class OrderCreate(OrderBase):
    user_id : int


class OrderPut(OrderBase):
    ...


class OrderPatch(BaseModel):
    name: Optional[str] = None
    quantity: Optional[int] = None


class OrderList(BaseModel):
    orders: list[OrderResponse]
