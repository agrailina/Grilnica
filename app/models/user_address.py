import uuid
from sqlalchemy import String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.db.base import Base
from typing import Optional, Any
from datetime import datetime


class UserAddress(Base):
    __tablename__ = "user_addresses"
    
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False,
        index=True
    )
    
    # Адрес
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    street: Mapped[str] = mapped_column(String(300), nullable=False)
    apartment: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    floor: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    entrance: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    intercom: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    comment: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Статус
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Временные метки
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    
    # Связи
    user: Mapped[Any] = relationship("User", back_populates="addresses")
    
    @property
    def full_address(self) -> str:
        """Полный адрес одной строкой"""
        parts = [f"г. {self.city}", self.street]
        if self.apartment:
            parts.append(f"кв. {self.apartment}")
        if self.entrance:
            parts.append(f"подъезд {self.entrance}")
        if self.floor:
            parts.append(f"этаж {self.floor}")
        return ", ".join(parts)
    
    def __repr__(self):
        return f"<UserAddress {self.full_address}>"