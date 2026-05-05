from typing import Optional, List
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.product_repository import ProductRepository
from app.schemas.product import (
    ProductCreate, ProductUpdate, ProductResponse,
    ProductDetailResponse, ProductFilterParams
)
from app.models.product import Product


class ProductService:
    def __init__(self, session: AsyncSession):
        self.repository = ProductRepository(session)

    async def create_product(self, product_data: ProductCreate) -> ProductResponse:
        """Создать новый товар"""
        product = await self.repository.create(product_data.model_dump())
        return ProductResponse.model_validate(product)

    async def get_product(self, product_id: UUID) -> ProductDetailResponse:
        """Получить товар по ID с категорией"""
        product = await self.repository.get_with_category(product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Товар не найден"
            )
        return ProductDetailResponse.model_validate(product)

    async def get_filtered_products(
        self, filters: ProductFilterParams
    ) -> tuple[List[ProductResponse], int]:
        """Получить товары с фильтрацией"""
        products, total = await self.repository.get_filtered(
            category_id=filters.category_id,
            category_slug=filters.category_slug,
            is_available=filters.is_available,
            search=filters.search,
            skip=filters.skip,
            limit=filters.limit
        )
        return [ProductResponse.model_validate(p) for p in products], total

    async def get_products_by_category_slug(
        self, slug: str, skip: int = 0, limit: int = 50
    ) -> tuple[List[ProductResponse], int]:
        """Получить товары по slug категории"""
        products, total = await self.repository.get_by_category_slug(slug, skip, limit)
        return [ProductResponse.model_validate(p) for p in products], total

    async def update_product(
        self, product_id: UUID, product_data: ProductUpdate
    ) -> ProductResponse:
        """Обновить товар"""
        product = await self.repository.get(product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Товар не найден"
            )
        
        update_data = product_data.model_dump(exclude_unset=True)
        updated_product = await self.repository.update(product_id, update_data)
        return ProductResponse.model_validate(updated_product)

    async def delete_product(self, product_id: UUID) -> bool:
        """Удалить товар"""
        if not await self.repository.exists(product_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Товар не найден"
            )
        return await self.repository.delete(product_id)