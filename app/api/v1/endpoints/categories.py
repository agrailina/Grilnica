from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.schemas.category import (
    CategoryCreate, CategoryUpdate, CategoryResponse,
    CategoryWithProducts, CategoryListResponse
)
from app.services.category_service import CategoryService

router = APIRouter(prefix="/categories", tags=["categories"])


@router.post("/", response_model=CategoryResponse, status_code=201)
async def create_category(
    category_data: CategoryCreate,
    db: AsyncSession = Depends(get_db)
):
    """Создать новую категорию"""
    service = CategoryService(db)
    return await service.create_category(category_data)


@router.get("/", response_model=CategoryListResponse)
async def get_categories(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Получить список категорий"""
    service = CategoryService(db)
    categories, total = await service.get_all_categories(skip, limit)
    return CategoryListResponse(categories=categories, total=total)


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Получить категорию по ID"""
    service = CategoryService(db)
    return await service.get_category(category_id)


@router.get("/slug/{slug}", response_model=CategoryResponse)
async def get_category_by_slug(
    slug: str,
    db: AsyncSession = Depends(get_db)
):
    """Получить категорию по slug"""
    service = CategoryService(db)
    return await service.get_category_by_slug(slug)


@router.get("/{category_id}/products", response_model=CategoryWithProducts)
async def get_category_with_products(
    category_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Получить категорию с товарами"""
    service = CategoryService(db)
    return await service.get_category_with_products(category_id)


@router.patch("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: UUID,
    category_data: CategoryUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Обновить категорию"""
    service = CategoryService(db)
    return await service.update_category(category_id, category_data)


@router.delete("/{category_id}", status_code=204)
async def delete_category(
    category_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Удалить категорию"""
    service = CategoryService(db)
    await service.delete_category(category_id)
    return None