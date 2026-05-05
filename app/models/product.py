import uuid
from sqlalchemy import String, Text, Numeric, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.db.base import Base
from typing import Optional, Any
from decimal import Decimal
from datetime import datetime


class Product(Base):
    __tablename__ = "products"
    
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    category_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("categories.id", ondelete="SET NULL"), 
        nullable=True
    )
    
    # Основное
    name: Mapped[str] = mapped_column(String(300), nullable=False, index=True)
    slug: Mapped[Optional[str]] = mapped_column(String(300), unique=True, nullable=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    
    # Медиа
    image: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Наличие
    is_available: Mapped[bool] = mapped_column(Boolean, default=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Временные метки
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    
    # Связи
    category: Mapped[Optional[Any]] = relationship("Category", back_populates="products")
    cart_items: Mapped[list[Any]] = relationship("CartItem", back_populates="product")
    order_items: Mapped[list[Any]] = relationship("OrderItem", back_populates="product")
    
    def __repr__(self):
        return f"<Product {self.name} - {self.price}₽>"