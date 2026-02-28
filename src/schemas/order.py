from typing import Optional

from pydantic import BaseModel


class OrderBase(BaseModel):
    user_id: int
    name: str
    quantity: int


class OrderResponse(OrderBase):
    id: int

    class Config:
        from_attributes = True


class OrderCreate(OrderBase):
    ...


class OrderPut(OrderBase):
    ...


class OrderPatch(BaseModel):
    name: Optional[str] = None
    quantity: Optional[int] = None
    user_id: Optional[int] = None


class OrderList(BaseModel):
    orders: list[OrderResponse]

