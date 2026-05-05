from typing import Optional, List
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.category_repository import CategoryRepository
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse, CategoryWithProducts
from app.models.category import Category


class CategoryService:
    def __init__(self, session: AsyncSession):
        self.repository = CategoryRepository(session)

    async def create_category(self, category_data: CategoryCreate) -> CategoryResponse:
        """Создать новую категорию"""
        # Проверяем уникальность name и slug
        existing_by_name = await self.repository.get_by_name(category_data.name)
        if existing_by_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Категория с именем '{category_data.name}' уже существует"
            )
        
        existing_by_slug = await self.repository.get_by_slug(category_data.slug)
        if existing_by_slug:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Категория с slug '{category_data.slug}' уже существует"
            )
        
        category = await self.repository.create(category_data.model_dump())
        return CategoryResponse.model_validate(category)

    async def get_category(self, category_id: UUID) -> CategoryResponse:
        """Получить категорию по ID"""
        category = await self.repository.get(category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Категория не найдена"
            )
        return CategoryResponse.model_validate(category)

    async def get_category_by_slug(self, slug: str) -> CategoryResponse:
        """Получить категорию по slug"""
        category = await self.repository.get_by_slug(slug)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Категория не найдена"
            )
        return CategoryResponse.model_validate(category)

    async def get_category_with_products(
        self, category_id: UUID
    ) -> CategoryWithProducts:
        """Получить категорию с товарами"""
        category = await self.repository.get_with_products(category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Категория не найдена"
            )
        return CategoryWithProducts.model_validate(category)

    async def get_all_categories(
        self, skip: int = 0, limit: int = 50
    ) -> tuple[List[CategoryResponse], int]:
        """Получить все активные категории"""
        categories, total = await self.repository.get_all_active(skip, limit)
        return [CategoryResponse.model_validate(c) for c in categories], total

    async def update_category(
        self, category_id: UUID, category_data: CategoryUpdate
    ) -> CategoryResponse:
        """Обновить категорию"""
        # Проверяем существование
        category = await self.repository.get(category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Категория не найдена"
            )
        
        update_data = category_data.model_dump(exclude_unset=True)
        
        # Проверяем уникальность при обновлении
        if "name" in update_data and update_data["name"] != category.name:
            existing = await self.repository.get_by_name(update_data["name"])
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Категория с именем '{update_data['name']}' уже существует"
                )
        
        if "slug" in update_data and update_data["slug"] != category.slug:
            existing = await self.repository.get_by_slug(update_data["slug"])
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Категория с slug '{update_data['slug']}' уже существует"
                )
        
        updated_category = await self.repository.update(category_id, update_data)
        return CategoryResponse.model_validate(updated_category)

    async def delete_category(self, category_id: UUID) -> bool:
        """Удалить категорию"""
        if not await self.repository.exists(category_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Категория не найдена"
            )
        return await self.repository.delete(category_id)