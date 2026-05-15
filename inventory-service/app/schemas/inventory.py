from pydantic import BaseModel, Field
from typing import Optional


class StockAdjustRequest(BaseModel):
    product_id: int
    quantity: int = Field(..., description="Positive to add, negative to remove")
    note: Optional[str] = None
    reference_id: Optional[str] = None
    reference_type: Optional[str] = None


class StockReserveRequest(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0)
    reference_id: str
    reference_type: str = "order"


class StockReleaseRequest(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0)
    reference_id: str


class StockMovementResponse(BaseModel):
    model_config = {"from_attributes": True}
    id: int
    inventory_id: int
    movement_type: str
    quantity: int
    reference_id: Optional[str] = None
    reference_type: Optional[str] = None
    note: Optional[str] = None
    performed_by: Optional[int] = None


class LowStockResponse(BaseModel):
    product_id: int
    product_name: str
    sku: str
    quantity_on_hand: int
    reorder_point: int
    quantity_available: int