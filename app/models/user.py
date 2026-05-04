import uuid
from sqlalchemy import String, Date, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.db.base import Base
from typing import List, Optional, Any
from datetime import datetime, date
import enum


class Gender(str, enum.Enum):
    MALE = "male"
    FEMALE = "female"


class User(Base):
    __tablename__ = "users"
    
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    
    # Авторизация
    phone: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    password_hash: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Личные данные
    first_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    birth_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    birth_date_locked: Mapped[bool] = mapped_column(Boolean, default=False)  # Запрет изменения ДР
    gender: Mapped[Optional[Gender]] = mapped_column(
        SQLEnum(Gender, name="gender_enum"), 
        nullable=True
    )
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    
    # Статус
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    is_profile_complete: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Временные метки
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Связи
    addresses: Mapped[List[Any]] = relationship(
        "UserAddress", back_populates="user", lazy="selectin", cascade="all, delete-orphan"
    )
    legal_entities: Mapped[List[Any]] = relationship(
        "LegalEntity", back_populates="user", lazy="selectin", cascade="all, delete-orphan"
    )
    carts: Mapped[List[Any]] = relationship(
        "Cart", back_populates="user", lazy="selectin", cascade="all, delete-orphan"
    )
    orders: Mapped[List[Any]] = relationship(
        "Order", back_populates="user", lazy="selectin"
    )
    support_tickets: Mapped[List[Any]] = relationship(
        "SupportTicket", back_populates="user"
    )
    
    @property
    def full_name(self) -> str:
        """Полное имя пользователя"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name or self.last_name or "Гость"
    
    def __repr__(self):
        return f"<User {self.phone}>"