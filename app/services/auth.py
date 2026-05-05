from typing import Optional
from uuid import UUID
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate, UserUpdate, UserResponse


class AuthService:
    """Сервис авторизации"""
    
    def __init__(self, session: AsyncSession):
        self.repo = UserRepository(session)
    
    async def login_or_register(self, phone: str) -> dict:
        """Вход или регистрация пользователя по телефону"""
        user, is_new = await self.repo.get_or_create(phone)
        
        return {
            "user": UserResponse.from_orm(user),
            "is_new": is_new,
            "message": "Регистрация успешна" if is_new else "Вход выполнен"
        }
    
    async def get_user(self, user_id: UUID) -> Optional[UserResponse]:
        """Получить пользователя по ID"""
        user = await self.repo.get_by_id(user_id)
        if user:
            return UserResponse.from_orm(user)
        return None
    
    async def update_user(self, user_id: UUID, update_data: UserUpdate) -> Optional[UserResponse]:
        """Обновить данные пользователя"""
        user = await self.repo.get_by_id(user_id)
        if not user:
            return None
        
        # Проверяем, заблокирована ли дата рождения
        update_dict = update_data.dict(exclude_unset=True)
        if user.birth_date_locked and 'birth_date' in update_dict:
            # Если дата рождения уже установлена и заблокирована
            if user.birth_date is not None:
                del update_dict['birth_date']
        
        # Если устанавливаем дату рождения впервые, блокируем её
        if 'birth_date' in update_dict and update_dict['birth_date'] is not None:
            update_dict['birth_date_locked'] = True
        
        user = await self.repo.update(user, update_dict)
        return UserResponse.from_orm(user)


async def get_auth_service(session: AsyncSession = Depends(get_db)) -> AuthService:
    """Зависимость для получения сервиса авторизации"""
    return AuthService(session)