import httpx
from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api.dependencies import get_db_session, get_users_client
from database.models import Order
from schemas.order import OrderList, OrderResponse, OrderCreate, OrderPut, OrderPatch

router = APIRouter(prefix="/order", tags=["order"])


@router.get(
    "/list",
    response_model=OrderList,
    status_code=status.HTTP_200_OK
)
async def list_orders(
        session: AsyncSession = Depends(get_db_session),
):
    orders = await session.execute(select(Order))
    orders = orders.scalars().all()
    return OrderList(orders=orders)


@router.get(
    "/{order_id}",
    response_model=OrderResponse,
    status_code=status.HTTP_200_OK
)
async def get_order(
        order_id: int,
        session: AsyncSession = Depends(get_db_session),
):
    order = await session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.post(
    "",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_order(
        order: OrderCreate,
        session: AsyncSession = Depends(get_db_session),
        users_client: httpx.AsyncClient = Depends(get_users_client)
):
    user_response = await users_client.get(f"api/v1/user/{order.user_id}")

    if user_response.status_code == 404:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist")

    user_response.raise_for_status()

    new_order = Order(
        **order.model_dump()
    )

    session.add(new_order)
    try:
        await session.commit()
        await session.refresh(new_order)
        return new_order
    except:
        await session.rollback()
        raise


@router.put(
    "/{order_id}",
    response_model=OrderResponse,
    status_code=status.HTTP_200_OK
)
async def update_order(
        order_id: int,
        order_data: OrderPut,
        session: AsyncSession = Depends(get_db_session),
):
    order = await session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if order.user_id != order_data.user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    update_data = order_data.model_dump(exclude={"user_id"})

    for field, value in update_data.items():
        setattr(order, field, value)

    try:
        await session.commit()
        await session.refresh(order)
        return order

    except:
        await session.rollback()
        raise


@router.patch(
    "/{order_id}",
    response_model=OrderResponse,
    status_code=status.HTTP_200_OK
)
async def partial_update_order(
        order_id: int,
        order_data: OrderPatch,
        session: AsyncSession = Depends(get_db_session),
):
    order = await session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if order.user_id != order_data.user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    update_data = order_data.model_dump(
        exclude_unset=True,
        exclude={"user_id"}
    )

    for field, value in update_data.items():
        setattr(order, field, value)
    for field, value in update_data.items():
        setattr(order, field, value)

    try:
        await session.commit()
        await session.refresh(order)
        return order

    except:
        await session.rollback()
        raise


@router.delete(
    "/{order_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_order(
        order_id: int,
        session: AsyncSession = Depends(get_db_session),
):
    order = await session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    await session.delete(order)
    await session.commit()
