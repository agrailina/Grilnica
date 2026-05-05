from typing import Optional
from uuid import UUID
from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.repositories.user import UserRepository
from app.models.user import User


async def get_current_user(
    request: Request,
    session: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """Получить текущего пользователя из сессии.
    Возвращает None если пользователь не авторизован.
    Не выбрасывает ошибку - для страниц, где авторизация не обязательна."""
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    
    repo = UserRepository(session)
    user = await repo.get_by_id(UUID(user_id))
    return user


async def require_user(
    request: Request,
    session: AsyncSession = Depends(get_db)
) -> User:
    """Получить текущего пользователя или выбросить 401.
    Для защищенных эндпоинтов."""
    user = await get_current_user(request, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Необходима авторизация"
        )
    return user