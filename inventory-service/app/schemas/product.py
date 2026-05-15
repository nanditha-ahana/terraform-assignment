from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal


class CategoryBase(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    is_active: bool = True


class CategoryCreateRequest(CategoryBase):
    pass


class CategoryUpdateRequest(BaseModel):
    category_id: int
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    is_active: Optional[bool] = None


class CategoryResponse(CategoryBase):
    model_config = {"from_attributes": True}
    id: int


class ProductBase(BaseModel):
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    sku: str = Field(..., max_length=100)
    price: Decimal = Field(..., gt=0)
    cost_price: Optional[Decimal] = None
    category_id: Optional[int] = None
    is_active: bool = True
    image_url: Optional[str] = None
    weight: Optional[Decimal] = None
    unit: str = "piece"


class ProductCreateRequest(ProductBase):
    initial_stock: int = Field(0, ge=0)
    reorder_point: int = Field(10, ge=0)
    reorder_quantity: int = Field(50, ge=1)
    warehouse_location: Optional[str] = None


class ProductUpdateRequest(BaseModel):
    product_id: int
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    price: Optional[Decimal] = Field(None, gt=0)
    cost_price: Optional[Decimal] = None
    category_id: Optional[int] = None
    is_active: Optional[bool] = None
    image_url: Optional[str] = None
    weight: Optional[Decimal] = None
    unit: Optional[str] = None


class InventoryResponse(BaseModel):
    model_config = {"from_attributes": True}
    id: int
    product_id: int
    quantity_on_hand: int
    quantity_reserved: int
    quantity_available: int
    reorder_point: int
    reorder_quantity: int
    warehouse_location: Optional[str] = None


class ProductResponse(ProductBase):
    model_config = {"from_attributes": True}
    id: int
    inventory: Optional[InventoryResponse] = None


class ProductListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[ProductResponse]