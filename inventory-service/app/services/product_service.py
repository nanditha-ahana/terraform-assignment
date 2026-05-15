from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.product import Product, Category
from app.models.inventory import Inventory
from app.schemas.product import (
    ProductCreateRequest,
    ProductResponse,
    ProductUpdateRequest,
    ProductListResponse,
    CategoryCreateRequest,
    CategoryUpdateRequest,
)


class ProductService:
    def __init__(self, db: AsyncSession):
        self.db = db

    # ── Categories ────────────────────────────────────────────────────────────

    async def create_category(self, data: CategoryCreateRequest) -> Category:
        result = await self.db.execute(select(Category).where(Category.name == data.name))
        if result.scalar_one_or_none():
            raise HTTPException(status_code=409, detail="Category already exists")
        cat = Category(**data.model_dump())
        self.db.add(cat)
        await self.db.flush()
        await self.db.refresh(cat)
        return cat

    async def list_categories(self) -> list[Category]:
        result = await self.db.execute(select(Category).order_by(Category.name))
        return list(result.scalars().all())

    async def update_category(self, category_id: int, data: CategoryUpdateRequest) -> Category:
        result = await self.db.execute(select(Category).where(Category.id == category_id))
        cat = result.scalar_one_or_none()
        if not cat:
            raise HTTPException(status_code=404, detail="Category not found")
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(cat, field, value)
        await self.db.flush()
        await self.db.refresh(cat)
        return cat

    async def delete_category(self, category_id: int) -> None:
        result = await self.db.execute(select(Category).where(Category.id == category_id))
        cat = result.scalar_one_or_none()
        if not cat:
            raise HTTPException(status_code=404, detail="Category not found")
        await self.db.delete(cat)
        await self.db.flush()

    # ── Products ──────────────────────────────────────────────────────────────

    async def get_product(self, product_id: int) -> Product:
        result = await self.db.execute(
            select(Product)
            .options(selectinload(Product.inventory))
            .where(Product.id == product_id)
        )
        product = result.scalar_one_or_none()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return product

    async def list_products(
        self,
        page: int = 1,
        page_size: int = 20,
        category_id: Optional[int] = None,
        is_active: Optional[bool] = None,
        search: Optional[str] = None,
    ) -> ProductListResponse:
        query = select(Product).options(selectinload(Product.inventory))
        count_query = select(func.count()).select_from(Product)

        if category_id:
            query = query.where(Product.category_id == category_id)
            count_query = count_query.where(Product.category_id == category_id)
        if is_active is not None:
            query = query.where(Product.is_active == is_active)
            count_query = count_query.where(Product.is_active == is_active)
        if search:
            like = f"%{search}%"
            query = query.where(Product.name.ilike(like) | Product.sku.ilike(like))
            count_query = count_query.where(Product.name.ilike(like) | Product.sku.ilike(like))

        total = (await self.db.execute(count_query)).scalar() or 0
        offset = (page - 1) * page_size
        result = await self.db.execute(query.offset(offset).limit(page_size).order_by(Product.id))
        products = result.scalars().all()
        return ProductListResponse(total=total, 
                                   page=page, 
                                   page_size=page_size, 
                                   items=[ProductResponse.model_validate(p) for p in products])

    async def create_product(self, data: ProductCreateRequest) -> Product:
        # SKU uniqueness
        result = await self.db.execute(select(Product).where(Product.sku == data.sku))
        if result.scalar_one_or_none():
            raise HTTPException(status_code=409, detail="SKU already exists")

        product_data = data.model_dump(exclude={"initial_stock", "reorder_point", "reorder_quantity", "warehouse_location"})
        product = Product(**product_data)
        self.db.add(product)
        await self.db.flush()

        inventory = Inventory(
            product_id=product.id,
            quantity_on_hand=data.initial_stock,
            reorder_point=data.reorder_point,
            reorder_quantity=data.reorder_quantity,
            warehouse_location=data.warehouse_location,
        )
        self.db.add(inventory)
        await self.db.flush()
        await self.db.refresh(product)
        return product

    async def update_product(self, product_id: int, data: ProductUpdateRequest) -> Product:
        product = await self.get_product(product_id)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(product, field, value)
        await self.db.flush()
        await self.db.refresh(product)
        return product

    async def delete_product(self, product_id: int) -> None:
        product = await self.get_product(product_id)
        await self.db.delete(product)
        await self.db.flush()