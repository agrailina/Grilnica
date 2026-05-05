from typing import Optional, List, Tuple
from uuid import UUID
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.product import Product
from app.repositories.base import BaseRepository


class ProductRepository(BaseRepository[Product]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Product)

    async def get_with_category(self, product_id: UUID) -> Optional[Product]:
        """Получить товар с категорией"""
        query = (
            select(Product)
            .options(selectinload(Product.category))
            .where(Product.id == product_id)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_filtered(
        self,
        category_id: Optional[UUID] = None,
        category_slug: Optional[str] = None,
        is_available: Optional[bool] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
        only_active: bool = True
    ) -> Tuple[List[Product], int]:
        """Получить товары с фильтрацией и пагинацией"""
        conditions = []
        
        if only_active:
            conditions.append(Product.is_active == True)
        
        if category_id:
            conditions.append(Product.category_id == category_id)
        
        if category_slug:
            query = (
                select(Product)
                .options(selectinload(Product.category))
                .join(Product.category)
                .where(Product.category.has(slug=category_slug))
            )
            if only_active:
                query = query.where(Product.is_active == True)
            if is_available is not None:
                query = query.where(Product.is_available == is_available)
            if search:
                query = query.where(
                    Product.name.ilike(f"%{search}%")
                )
            
            # Считаем общее количество
            count_query = select(func.count()).select_from(query.subquery())
            count_result = await self.session.execute(count_query)
            total = count_result.scalar()
            
            # Применяем пагинацию
            query = query.order_by(Product.created_at).offset(skip).limit(limit)
            result = await self.session.execute(query)
            products = result.scalars().all()
            
            return list(products), total
        
        if is_available is not None:
            conditions.append(Product.is_available == is_available)
        
        if search:
            conditions.append(
                or_(
                    Product.name.ilike(f"%{search}%"),
                    Product.description.ilike(f"%{search}%")
                )
            )
        
        # Базовый запрос
        base_query = select(Product).options(selectinload(Product.category))
        
        if conditions:
            base_query = base_query.where(and_(*conditions))
        
        # Считаем общее количество
        count_query = select(func.count()).select_from(base_query.subquery())
        count_result = await self.session.execute(count_query)
        total = count_result.scalar()
        
        # Применяем пагинацию
        query = base_query.order_by(Product.name).offset(skip).limit(limit)
        result = await self.session.execute(query)
        products = result.scalars().all()
        
        return list(products), total

    async def get_by_category_slug(
        self, slug: str, skip: int = 0, limit: int = 50
    ) -> Tuple[List[Product], int]:
        """Получить товары по slug категории"""
        return await self.get_filtered(
            category_slug=slug,
            skip=skip,
            limit=limit
        )