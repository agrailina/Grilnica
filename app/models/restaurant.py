# app/models/restaurant.py
import uuid
from sqlalchemy import String, Float, Boolean, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.db.base import Base
from typing import List, Optional, Any
from datetime import datetime
import enum


class ScheduleType(str, enum.Enum):
    DAILY = "daily"
    AROUND_CLOCK = "around_clock"


class Restaurant(Base):
    __tablename__ = "restaurants"
    
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    city_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("cities.id", ondelete="CASCADE"), nullable=False)
    
    # Основная информация
    address: Mapped[str] = mapped_column(String(300), nullable=False, index=True)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    schedule_type: Mapped[ScheduleType] = mapped_column(
        SQLEnum(ScheduleType, name="schedule_type_enum"), 
        default=ScheduleType.DAILY,
        nullable=False
    )
    work_hours: Mapped[str] = mapped_column(String(100), nullable=False)  # "09:00-23:00"
    
    # Наличие категорий блюд (флаги)
    has_shawarma: Mapped[bool] = mapped_column(Boolean, default=True)
    has_hotdogs: Mapped[bool] = mapped_column(Boolean, default=True)
    has_wings: Mapped[bool] = mapped_column(Boolean, default=True)
    has_pizza: Mapped[bool] = mapped_column(Boolean, default=True)
    has_lunches: Mapped[bool] = mapped_column(Boolean, default=True)
    has_soups: Mapped[bool] = mapped_column(Boolean, default=False)
    has_salads: Mapped[bool] = mapped_column(Boolean, default=False)
    has_hot_snacks: Mapped[bool] = mapped_column(Boolean, default=True)
    has_japanese: Mapped[bool] = mapped_column(Boolean, default=False)
    has_wok: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Фото ресторана
    image: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Статус
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    
    # Связи
    city: Mapped[Any] = relationship("City", back_populates="restaurants")
    support_tickets: Mapped[List[Any]] = relationship(
        "SupportTicket", back_populates="restaurant"
    )
    
    @property
    def available_categories(self) -> List[str]:
        """Возвращает список доступных категорий для ресторана"""
        categories = []
        if self.has_shawarma: categories.append("shawarma")
        if self.has_hotdogs: categories.append("hotdogs")
        if self.has_wings: categories.append("wings")
        if self.has_pizza: categories.append("pizza")
        if self.has_lunches: categories.append("lunches")
        if self.has_soups: categories.append("soups")
        if self.has_salads: categories.append("salads")
        if self.has_hot_snacks: categories.append("hot_snacks")
        if self.has_japanese: categories.append("japanese")
        if self.has_wok: categories.append("wok")
        return categories
    
    def __repr__(self):
        return f"<Restaurant {self.address}>"