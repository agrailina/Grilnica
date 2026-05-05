from typing import Optional
from fastapi import Request, HTTPException, status
from app.models.user import User
from app.db.session import AsyncSessionLocal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


async def get_optional_user(request: Request) -> Optional[User]:
    """
    Получить текущего пользователя, если он авторизован.
    Не выбрасывает ошибку, если пользователь не авторизован.
    """
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(User).where(User.id == user_id)
            )
            user = result.scalar_one_or_none()
            return user
    except Exception:
        return None


async def require_user(request: Request) -> User:
    """
    Получить текущего пользователя (обязательная авторизация).
    Выбрасывает 401, если пользователь не авторизован.
    """
    user = await get_optional_user(request)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Необходима авторизация"
        )
    return user


async def get_db():
    """Зависимость для получения сессии БД"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()