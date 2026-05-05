from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from datetime import date, datetime
from uuid import UUID
import enum


class Gender(str, enum.Enum):
    MALE = "male"
    FEMALE = "female"


class UserCreate(BaseModel):
    """Схема для создания пользователя"""
    phone: str
    
    @validator('phone')
    def validate_phone(cls, v):
        # Очищаем от всего кроме цифр и +
        cleaned = ''.join(c for c in v if c.isdigit() or c == '+')
        if not cleaned.startswith('+7') or len(cleaned) != 12:
            raise ValueError('Номер телефона должен быть в формате +7XXXXXXXXXX')
        return cleaned


class UserUpdate(BaseModel):
    """Схема для обновления данных пользователя"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    birth_date: Optional[date] = None
    gender: Optional[Gender] = None
    
    @validator('email')
    def validate_email(cls, v):
        if v is not None and '@' not in v:
            raise ValueError('Некорректный email')
        return v


class UserResponse(BaseModel):
    """Схема для ответа с данными пользователя"""
    id: UUID
    phone: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    birth_date: Optional[date] = None
    gender: Optional[Gender] = None
    is_profile_complete: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """Схема для входа"""
    phone: str
    
    @validator('phone')
    def validate_phone(cls, v):
        cleaned = ''.join(c for c in v if c.isdigit() or c == '+')
        if not cleaned.startswith('+7') or len(cleaned) != 12:
            raise ValueError('Номер телефона должен быть в формате +7XXXXXXXXXX')
        return cleaned