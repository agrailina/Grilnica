from typing import Optional, List
from uuid import UUID
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.category import Category
from app.repositories.base import BaseRepository


class CategoryRepository(BaseRepository[Category]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Category)

    async def get_by_slug(self, slug: str) -> Optional[Category]:
        """Получить категорию по slug"""
        query = select(Category).where(Category.slug == slug)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_with_products(
        self, category_id: UUID, only_active: bool = True
    ) -> Optional[Category]:
        """Получить категорию с товарами"""
        query = select(Category).options(
            selectinload(Category.products)
        ).where(Category.id == category_id)
        
        if only_active:
            query = query.where(Category.is_active == True)
        
        result = await self.session.execute(query)
        category = result.scalar_one_or_none()
        
        if category and only_active:
            category.products = [
                p for p in category.products 
                if p.is_active and p.is_available
            ]
        
        return category

    async def get_all_active(
        self, skip: int = 0, limit: int = 50
    ) -> tuple[List[Category], int]:
        """Получить все активные категории с пагинацией"""
        # Получаем общее количество
        count_query = select(func.count()).where(Category.is_active == True)
        count_result = await self.session.execute(count_query)
        total = count_result.scalar()

        # Получаем данные
        query = (
            select(Category)
            .where(Category.is_active == True)
            .order_by(Category.order, Category.name)
            .offset(skip)
            .limit(limit)
        )
        
        result = await self.session.execute(query)
        categories = result.scalars().all()

        return list(categories), total

    async def get_by_name(self, name: str) -> Optional[Category]:
        """Получить категорию по имени"""
        query = select(Category).where(Category.name == name)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()