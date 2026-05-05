from typing import Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User


class UserRepository:
    """Репозиторий для работы с пользователями"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_phone(self, phone: str) -> Optional[User]:
        """Получить пользователя по номеру телефона"""
        result = await self.session.execute(
            select(User).where(User.phone == phone)
        )
        return result.scalar_one_or_none()
    
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Получить пользователя по ID"""
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def create(self, phone: str) -> User:
        """Создать нового пользователя"""
        user = User(phone=phone)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user
    
    async def update(self, user: User, update_data: dict) -> User:
        """Обновить данные пользователя"""
        for key, value in update_data.items():
            if value is not None and hasattr(user, key):
                setattr(user, key, value)
        
        # Проверяем заполненность профиля
        if user.first_name and user.last_name and user.birth_date:
            user.is_profile_complete = True
        
        await self.session.commit()
        await self.session.refresh(user)
        return user
    
    async def get_or_create(self, phone: str) -> tuple[User, bool]:
        """Получить существующего или создать нового пользователя.
        Возвращает (пользователь, создан_ли_новый)"""
        user = await self.get_by_phone(phone)
        if user:
            return user, False
        
        user = await self.create(phone)
        return user, True