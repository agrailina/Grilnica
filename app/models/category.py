import uuid
from sqlalchemy import String, Integer, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.db.base import Base
from typing import List, Optional, Any
from datetime import datetime


class Category(Base):
    __tablename__ = "categories"
    
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    
    # Основное
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    icon: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Порядок отображения
    order: Mapped[int] = mapped_column(Integer, default=0)
    
    # Статус
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    
    # Связи
    products: Mapped[List[Any]] = relationship(
        "Product", back_populates="category", lazy="selectin"
    )
    
    def __repr__(self):
        return f"<Category {self.name}>"