from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.core.dependencies import get_current_user_id, require_manager_or_admin
from app.db.dependencies import get_db
from app.schemas.product import (
    ProductCreateRequest,
    ProductUpdateRequest,
    ProductResponse,
    ProductListResponse,
    CategoryCreateRequest,
    CategoryUpdateRequest,
    CategoryResponse,
)
from app.services.product_service import ProductService

router = APIRouter(prefix="/products", tags=["Products"])


# ── Categories ────────────────────────────────────────────────────────────────

@router.get("/categories", response_model=list[CategoryResponse])
async def list_categories(db: AsyncSession = Depends(get_db), _=Depends(get_current_user_id)):
    svc = ProductService(db)
    return await svc.list_categories()


@router.post("/categories", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    data: CategoryCreateRequest,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_manager_or_admin),
):
    svc = ProductService(db)
    return await svc.create_category(data)


@router.post("/categories-update", response_model=CategoryResponse)
async def update_category(
    data: CategoryUpdateRequest,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_manager_or_admin),
):
    svc = ProductService(db)
    category_id = data.category_id
    return await svc.update_category(category_id, data)


@router.post("/categories-delete", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_manager_or_admin),
):
    svc = ProductService(db)
    await svc.delete_category(category_id)


# ── Products ──────────────────────────────────────────────────────────────────

@router.get("/list-products", response_model=ProductListResponse)
async def list_products(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category_id: Optional[int] = Query(None),
    is_active: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user_id),
):
    svc = ProductService(db)
    return await svc.list_products(page=page, page_size=page_size, category_id=category_id, is_active=is_active, search=search)


@router.post("/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    data: ProductCreateRequest,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_manager_or_admin),
):
    svc = ProductService(db)
    return await svc.create_product(data)


@router.get("/get-product-by-id", response_model=ProductResponse)
async def get_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user_id),
):
    svc = ProductService(db)
    return await svc.get_product(product_id)


@router.post("/update-product", response_model=ProductResponse)
async def update_product(
    data: ProductUpdateRequest,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_manager_or_admin),
):
    svc = ProductService(db)
    product_id = data.product_id
    return await svc.update_product(product_id, data)


@router.post("/delete-product", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_manager_or_admin),
):
    svc = ProductService(db)
    await svc.delete_product(product_id)