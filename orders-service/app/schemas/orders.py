from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal
from datetime import datetime

from app.models.orders import OrderStatus, PaymentStatus


class OrderItemRequest(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0)


class ShippingAddressRequest(BaseModel):
    name: str
    address_line1: str
    address_line2: Optional[str] = None
    city: str
    state: str
    country: str
    postal_code: str


class OrderCreateRequest(BaseModel):
    items: list[OrderItemRequest] = Field(..., min_length=1)
    shipping_address: ShippingAddressRequest
    notes: Optional[str] = None


class OrderStatusUpdateRequest(BaseModel):
    order_id: int
    status: OrderStatus
    note: Optional[str] = None
    tracking_number: Optional[str] = None


class PaymentStatusUpdateRequest(BaseModel):
    order_id: int
    payment_status: PaymentStatus


class OrderItemResponse(BaseModel):
    model_config = {"from_attributes": True}
    id: int
    product_id: int
    product_name: str
    product_sku: str
    unit_price: Decimal
    quantity: int
    total_price: Decimal


class OrderStatusHistoryResponse(BaseModel):
    model_config = {"from_attributes": True}
    id: int
    from_status: Optional[str] = None
    to_status: str
    changed_by: Optional[int] = None
    note: Optional[str] = None
    created_at: datetime


class OrderResponse(BaseModel):
    model_config = {"from_attributes": True}
    id: int
    order_number: str
    user_id: int
    status: str
    payment_status: str
    subtotal: Decimal
    discount_amount: Decimal
    tax_amount: Decimal
    shipping_amount: Decimal
    total_amount: Decimal
    shipping_name: Optional[str] = None
    shipping_address_line1: Optional[str] = None
    shipping_address_line2: Optional[str] = None
    shipping_city: Optional[str] = None
    shipping_state: Optional[str] = None
    shipping_country: Optional[str] = None
    shipping_postal_code: Optional[str] = None
    notes: Optional[str] = None
    tracking_number: Optional[str] = None
    items: list[OrderItemResponse] = []
    status_history: list[OrderStatusHistoryResponse] = []
    created_at: datetime
    updated_at: datetime


class OrderListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[OrderResponse]