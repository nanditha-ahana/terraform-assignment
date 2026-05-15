from typing import Optional
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.inventory import Inventory, StockMovement
from app.models.product import Product
from app.schemas.inventory import StockAdjustRequest, StockReserveRequest, StockReleaseRequest, LowStockResponse


class InventoryService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_inventory_by_product(self, product_id: int) -> Inventory:
        result = await self.db.execute(
            select(Inventory).where(Inventory.product_id == product_id)
        )
        inv = result.scalar_one_or_none()
        if not inv:
            raise HTTPException(status_code=404, detail="Inventory record not found for product")
        return inv

    async def adjust_stock(
        self,
        product_id: int,
        data: StockAdjustRequest,
        performed_by: int,
    ) -> Inventory:
        result = await self.db.execute(
            select(Inventory.quantity_on_hand).where(Inventory.product_id == product_id)
        )
        new_qty = result.scalar() or 0

        inv = await self.get_inventory_by_product(product_id)

        if new_qty + data.quantity < 0:
            raise HTTPException(status_code=400, detail="Insufficient stock — quantity cannot go below 0")

        setattr(inv, "quantity_on_hand", new_qty)
        movement = StockMovement(
            inventory_id=inv.id,
            movement_type="in" if data.quantity > 0 else "out",
            quantity=abs(data.quantity),
            reference_id=data.reference_id,
            reference_type=data.reference_type,
            note=data.note,
            performed_by=performed_by,
        )
        self.db.add(movement)
        await self.db.flush()
        await self.db.refresh(inv)
        return inv

    async def reserve_stock(self, data: StockReserveRequest, performed_by: int) -> Inventory:
        inv = await self.get_inventory_by_product(data.product_id)
        result = await self.db.execute(
            select(Inventory.quantity_on_hand - Inventory.quantity_reserved)
            .where(Inventory.product_id == inv.product_id)
        )
        available = result.scalar_one()
        if available < data.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Only {available} units available; requested {data.quantity}",
            )
            
        setattr(inv, "quantity_reserved", inv.quantity_reserved + data.quantity)
        movement = StockMovement(
            inventory_id=inv.id,
            movement_type="reserve",
            quantity=data.quantity,
            reference_id=data.reference_id,
            reference_type=data.reference_type,
            performed_by=performed_by,
        )
        self.db.add(movement)
        await self.db.flush()
        await self.db.refresh(inv)
        return inv

    async def release_stock(self, data: StockReleaseRequest, performed_by: int) -> Inventory:
        inv = await self.get_inventory_by_product(data.product_id)
        result = await self.db.execute(
            select(Inventory.quantity_reserved).where(Inventory.product_id == inv.product_id)
        )
        quantity_reserved = result.scalar_one() or 0

        if quantity_reserved < data.quantity:
            raise HTTPException(status_code=400, detail="Cannot release more than reserved quantity")
        
        setattr(inv, "quantity_reserved", inv.quantity_reserved - data.quantity)
        setattr(inv, "quantity_on_hand", inv.quantity_on_hand - data.quantity)  # Fulfillment: deduct from on-hand too
        movement = StockMovement(
            inventory_id=inv.id,
            movement_type="release",
            quantity=data.quantity,
            reference_id=data.reference_id,
            performed_by=performed_by,
        )
        self.db.add(movement)
        await self.db.flush()
        await self.db.refresh(inv)
        return inv

    async def get_stock_movements(
        self, product_id: int, limit: int = 50
    ) -> list[StockMovement]:
        inv = await self.get_inventory_by_product(product_id)
        result = await self.db.execute(
            select(StockMovement)
            .where(StockMovement.inventory_id == inv.id)
            .order_by(StockMovement.id.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_low_stock_products(self) -> list[LowStockResponse]:
        result = await self.db.execute(
            select(Inventory, Product)
            .join(Product, Inventory.product_id == Product.id)
            .where(Inventory.quantity_on_hand <= Inventory.reorder_point)
            .where(Product.is_active.is_(True))
        )
        rows = result.all()
        return [
            LowStockResponse(
                product_id=product.id,
                product_name=product.name,
                sku=product.sku,
                quantity_on_hand=inv.quantity_on_hand,
                reorder_point=inv.reorder_point,
                quantity_available=inv.quantity_on_hand - inv.quantity_reserved,
            )
            for inv, product in rows
        ]