import uuid
from sqlalchemy import String, Integer, Numeric, Boolean, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.db.base import Base
from typing import List, Optional, Any
from decimal import Decimal
from datetime import datetime
import enum


class OrderType(str, enum.Enum):
    RESTAURANT = "restaurant"
    DELIVERY = "delivery"


class OrderStatus(str, enum.Enum):
    NEW = "new"
    CONFIRMED = "confirmed"
    COOKING = "cooking"
    READY = "ready"
    IN_DELIVERY = "in_delivery"
    DELIVERED = "delivered"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Order(Base):
    __tablename__ = "orders"
    
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), 
        nullable=True,
        index=True
    )
    restaurant_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("restaurants.id", ondelete="SET NULL"), 
        nullable=True
    )
    
    # Тип заказа
    order_type: Mapped[OrderType] = mapped_column(
        SQLEnum(OrderType, name="order_type_enum"), 
        nullable=False
    )
    status: Mapped[OrderStatus] = mapped_column(
        SQLEnum(OrderStatus, name="order_status_enum"), 
        default=OrderStatus.NEW,
        nullable=False
    )
    
    # Финансы
    total_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    
    # Адрес доставки
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    address: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    apartment: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    office: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    floor: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    entrance: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    intercom: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Временные метки
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Связи
    user: Mapped[Optional[Any]] = relationship("User", back_populates="orders")
    items: Mapped[List["OrderItem"]] = relationship(
        "OrderItem", back_populates="order", lazy="selectin", cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<Order {self.id} - {self.status.value}>"


class OrderItem(Base):
    __tablename__ = "order_items"
    
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    order_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"), 
        nullable=False,
        index=True
    )
    product_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("products.id", ondelete="SET NULL"), 
        nullable=True
    )
    
    # Сохраняем исторические данные
    product_name: Mapped[str] = mapped_column(String(300), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    
    # Связи
    order: Mapped["Order"] = relationship("Order", back_populates="items")
    product: Mapped[Optional[Any]] = relationship("Product", back_populates="order_items")
    
    @property
    def total(self) -> Decimal:
        """Сумма по позиции"""
        return self.price * self.quantity
    
    def __repr__(self):
        return f"<OrderItem {self.product_name} x{self.quantity}>"