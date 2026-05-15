from decimal import Decimal
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.orders import (
    Order,
    OrderItem,
    OrderStatus,
    PaymentStatus,
    OrderStatusHistory,
)

from app.schemas.orders import (
    OrderCreateRequest,
    OrderStatusUpdateRequest,
    PaymentStatusUpdateRequest,
)


class OrderService:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_order_by_id(
        self,
        order_id: int,
        user_id: int,
        is_admin: bool = False,
    ) -> Order:

        stmt = (
            select(Order)
            .options(
                selectinload(Order.items),
                selectinload(Order.status_history),
            )
            .where(Order.id == order_id)
        )

        if not is_admin:
            stmt = stmt.where(Order.user_id == user_id)

        result = await self.db.execute(stmt)

        order = result.scalar_one_or_none()

        if not order:
            raise HTTPException(
                status_code=404,
                detail=f"Order not found {order_id}",
            )

        return order

    async def create_order(
        self,
        payload: OrderCreateRequest,
        user_id: int,
    ) -> Order:

        subtotal = Decimal("0.00")

        order = Order(
            order_number=f"ORD-{uuid4().hex[:10].upper()}",
            user_id=user_id,
            status=OrderStatus.pending.value,
            payment_status=PaymentStatus.unpaid.value,
            subtotal=0,
            discount_amount=0,
            tax_amount=0,
            shipping_amount=0,
            total_amount=0,
            shipping_name=payload.shipping_address.name,
            shipping_address_line1=payload.shipping_address.address_line1,
            shipping_address_line2=payload.shipping_address.address_line2,
            shipping_city=payload.shipping_address.city,
            shipping_state=payload.shipping_address.state,
            shipping_country=payload.shipping_address.country,
            shipping_postal_code=payload.shipping_address.postal_code,
            notes=payload.notes,
        )

        self.db.add(order)

        await self.db.flush()

        for item in payload.items:

            # Fetch product details from inventory/product service

            mock_price = Decimal("100.00")

            total_price = mock_price * item.quantity

            subtotal += total_price

            order_item = OrderItem(
                order_id=order.id,
                product_id=item.product_id,
                product_name=f"Product-{item.product_id}",
                product_sku=f"SKU-{item.product_id}",
                unit_price=mock_price,
                quantity=item.quantity,
                total_price=total_price,
            )

            self.db.add(order_item)

        setattr(order, "subtotal", subtotal)
        setattr(order, "tax_amount", subtotal * Decimal("0.18"))
        setattr(order, "shipping_amount", Decimal("50.00"))

        setattr(order, "total_amount", (
            order.subtotal
            + order.tax_amount
            + order.shipping_amount
        ))

        status_history = OrderStatusHistory(
            order_id=order.id,
            from_status=None,
            to_status=OrderStatus.pending.value,
            changed_by=user_id,
            note="Order created",
        )

        self.db.add(status_history)

        await self.db.commit()

        await self.db.refresh(order)

        return order

    async def get_my_orders(
        self,
        user_id: int,
    ) -> list[Order]:

        result = await self.db.execute(
            select(Order)
            .options(
                selectinload(Order.items),
                selectinload(Order.status_history),
            )
            .where(Order.user_id == user_id)
            .order_by(Order.id.desc())
        )

        return list(result.scalars().all())

    async def update_order_status(
        self,
        payload: OrderStatusUpdateRequest,
        changed_by: int,
    ) -> Order:

        result = await self.db.execute(
            select(Order).where(Order.id == payload.order_id)
        )

        order = result.scalar_one_or_none()

        if not order:
            raise HTTPException(
                status_code=404,
                detail="Order not found",
            )

        previous_status = order.status

        setattr(order, "status", payload.status.value)

        if payload.tracking_number:
            setattr(order, "tracking_number", payload.tracking_number)

        history = OrderStatusHistory(
            order_id=order.id,
            from_status=previous_status,
            to_status=payload.status.value,
            changed_by=changed_by,
            note=payload.note,
        )

        self.db.add(history)

        await self.db.commit()

        await self.db.refresh(order)

        return order

    async def update_payment_status(
        self,
        payload: PaymentStatusUpdateRequest,
    ) -> Order:

        result = await self.db.execute(
            select(Order).where(Order.id == payload.order_id)
        )

        order = result.scalar_one_or_none()

        if not order:
            raise HTTPException(
                status_code=404,
                detail="Order not found",
            )

        setattr(
            order,
            "payment_status",
            payload.payment_status.value,
        )

        await self.db.commit()

        await self.db.refresh(order)

        return order