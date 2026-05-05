from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.services.auth import AuthService, get_auth_service
from app.api.deps import require_user
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=dict)
async def login(
    user_data: UserCreate,
    request: Request,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Вход или регистрация по номеру телефона"""
    result = await auth_service.login_or_register(user_data.phone)
    
    # Сохраняем user_id в сессии
    request.session["user_id"] = str(result["user"].id)
    
    return result


@router.post("/logout")
async def logout(request: Request):
    """Выход из аккаунта"""
    request.session.clear()
    return {"message": "Выход выполнен"}


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(require_user)):
    """Получить данные текущего пользователя"""
    return UserResponse.from_orm(current_user)


@router.put("/me", response_model=UserResponse)
async def update_me(
    update_data: UserUpdate,
    current_user: User = Depends(require_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Обновить данные текущего пользователя"""
    updated_user = await auth_service.update_user(current_user.id, update_data)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    return updated_user


@router.get("/check")
async def check_auth(current_user: User = Depends(require_user)):
    """Проверка авторизации (для фронтенда)"""
    return {
        "authenticated": True,
        "user": UserResponse.from_orm(current_user).dict()
    }