from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.dependencies import get_db

from app.schemas.orders import (
    OrderCreateRequest,
    OrderResponse,
    OrderStatusUpdateRequest,
    PaymentStatusUpdateRequest,
)

from app.services.orders import OrderService

from app.core.dependencies import (
    get_current_user_id,
)

router = APIRouter(
    prefix="/orders",
    tags=["Orders"],
)


@router.post(
    "/create",
    response_model=OrderResponse,
)
async def create_order(
    payload: OrderCreateRequest,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):

    service = OrderService(db)

    return await service.create_order(
        payload=payload,
        user_id=user_id,
    )


@router.get(
    "/my-orders",
    response_model=list[OrderResponse],
)
async def get_my_orders(
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):

    service = OrderService(db)

    return await service.get_my_orders(
        user_id=user_id,
    )


@router.get(
    "/{order_id}",
    response_model=OrderResponse,
)
async def get_order_by_id(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):

    service = OrderService(db)

    return await service.get_order_by_id(
        order_id=order_id,
        user_id=user_id,
    )


@router.post(
    "/status/update",
    response_model=OrderResponse,
)
async def update_order_status(
    payload: OrderStatusUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user_id),
):

    service = OrderService(db)

    return await service.update_order_status(
        payload=payload,
        changed_by=int(current_user["sub"]),
    )


@router.post(
    "/payment/update",
    response_model=OrderResponse,
)
async def update_payment_status(
    payload: PaymentStatusUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user_id),
):

    service = OrderService(db)

    return await service.update_payment_status(
        payload=payload
    )