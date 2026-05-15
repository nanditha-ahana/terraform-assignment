from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user_id, require_manager_or_admin
from app.db.dependencies import get_db
from app.schemas.inventory import (
    StockAdjustRequest,
    StockReserveRequest,
    StockReleaseRequest,
    StockMovementResponse,
    LowStockResponse,
)
from app.schemas.product import InventoryResponse
from app.services.inventory_service import InventoryService

router = APIRouter(prefix="/inventory", tags=["Inventory"])


@router.get("/low-stock", response_model=list[LowStockResponse])
async def get_low_stock(
    db: AsyncSession = Depends(get_db),
    _=Depends(require_manager_or_admin),
):
    """Products at or below their reorder point."""
    svc = InventoryService(db)
    return await svc.get_low_stock_products()


@router.get("/products", response_model=InventoryResponse)
async def get_product_inventory(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user_id),
):
    svc = InventoryService(db)
    return await svc.get_inventory_by_product(product_id)


@router.post("/products-adjust", response_model=InventoryResponse)
async def adjust_stock(
    data: StockAdjustRequest,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
    _=Depends(require_manager_or_admin),
):
    """Manually adjust stock (inbound, write-off, correction)."""
    svc = InventoryService(db)
    return await svc.adjust_stock(data.product_id, data, performed_by=user_id)


@router.post("/reserve", response_model=InventoryResponse, status_code=status.HTTP_200_OK)
async def reserve_stock(
    data: StockReserveRequest,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Reserve stock when an order is placed (called by orders-service)."""
    svc = InventoryService(db)
    return await svc.reserve_stock(data, performed_by=user_id)


@router.post("/release", response_model=InventoryResponse, status_code=status.HTTP_200_OK)
async def release_stock(
    data: StockReleaseRequest,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Fulfil/cancel an order — releases reservation and deducts on-hand."""
    svc = InventoryService(db)
    return await svc.release_stock(data, performed_by=user_id)


@router.get("/movements", response_model=list[StockMovementResponse])
async def get_stock_movements(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_manager_or_admin),
):
    """Audit trail of stock movements for a product."""
    svc = InventoryService(db)
    return await svc.get_stock_movements(product_id)