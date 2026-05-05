from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.schemas.product import (
    ProductCreate, ProductUpdate, ProductResponse,
    ProductDetailResponse, ProductListResponse,
    ProductFilterParams
)
from app.services.product_service import ProductService

router = APIRouter(prefix="/products", tags=["products"])


@router.post("/", response_model=ProductResponse, status_code=201)
async def create_product(
    product_data: ProductCreate,
    db: AsyncSession = Depends(get_db)
):
    """Создать новый товар"""
    service = ProductService(db)
    return await service.create_product(product_data)


@router.get("/", response_model=ProductListResponse)
async def get_products(
    category_id: Optional[UUID] = Query(None),
    category_slug: Optional[str] = Query(None),
    is_available: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Получить список товаров с фильтрацией"""
    filters = ProductFilterParams(
        category_id=category_id,
        category_slug=category_slug,
        is_available=is_available,
        search=search,
        skip=skip,
        limit=limit
    )
    service = ProductService(db)
    products, total = await service.get_filtered_products(filters)
    return ProductListResponse(products=products, total=total)


# ВАЖНО: этот маршрут ДОЛЖЕН быть перед /{product_id}!
@router.get("/by-category/{slug}", response_model=ProductListResponse)
async def get_products_by_category(
    slug: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Получить товары по slug категории"""
    service = ProductService(db)
    products, total = await service.get_products_by_category_slug(slug, skip, limit)
    return ProductListResponse(products=products, total=total)


# Этот маршрут должен быть ПОСЛЕДНИМ среди GET!
@router.get("/{product_id}", response_model=ProductDetailResponse)
async def get_product(
    product_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Получить товар по ID"""
    service = ProductService(db)
    return await service.get_product(product_id)


@router.patch("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: UUID,
    product_data: ProductUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Обновить товар"""
    service = ProductService(db)
    return await service.update_product(product_id, product_data)


@router.delete("/{product_id}", status_code=204)
async def delete_product(
    product_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Удалить товар"""
    service = ProductService(db)
    await service.delete_product(product_id)
    return None