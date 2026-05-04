import uuid
from sqlalchemy import String, Integer, Numeric, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.db.base import Base
from typing import List, Optional, Any
from decimal import Decimal
from datetime import datetime


class Cart(Base):
    __tablename__ = "carts"
    
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=True,
        index=True
    )
    session_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    
    # Статус
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Временные метки
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    
    # Связи
    user: Mapped[Optional[Any]] = relationship("User", back_populates="carts")
    items: Mapped[List["CartItem"]] = relationship(
        "CartItem", back_populates="cart", lazy="selectin", cascade="all, delete-orphan"
    )
    
    @property
    def total_price(self) -> Decimal:
        """Общая сумма корзины"""
        return sum(item.total for item in self.items)
    
    @property
    def total_items(self) -> int:
        """Общее количество товаров"""
        return sum(item.quantity for item in self.items)
    
    def __repr__(self):
        return f"<Cart {self.id} - {self.total_items} items>"


class CartItem(Base):
    __tablename__ = "cart_items"
    
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    cart_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("carts.id", ondelete="CASCADE"), 
        nullable=False,
        index=True
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"), 
        nullable=False
    )
    
    # Данные товара
    quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    
    # Временные метки
    added_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    
    # Связи
    cart: Mapped["Cart"] = relationship("Cart", back_populates="items")
    product: Mapped[Any] = relationship("Product", back_populates="cart_items")
    
    @property
    def total(self) -> Decimal:
        """Сумма по позиции"""
        return self.price * self.quantity
    
    def __repr__(self):
        return f"<CartItem x{self.quantity} - {self.total}₽>"