import uuid
from sqlalchemy import String, Text, Boolean, DateTime, ForeignKey, Integer, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.db.base import Base
from typing import List, Optional, Any
from datetime import datetime
import enum


class ContactMethod(str, enum.Enum):
    SITE = "site"
    WHATSAPP = "whatsapp"
    TELEGRAM = "telegram"


class TicketStatus(str, enum.Enum):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


class SupportTicket(Base):
    __tablename__ = "support_tickets"
    
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), 
        nullable=True
    )
    restaurant_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("restaurants.id", ondelete="SET NULL"), 
        nullable=True
    )
    
    # Контактные данные
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    
    # Обращение
    subject: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Метаданные
    contact_method: Mapped[ContactMethod] = mapped_column(
        SQLEnum(ContactMethod, name="contact_method_enum"), 
        default=ContactMethod.SITE,
        nullable=False
    )
    status: Mapped[TicketStatus] = mapped_column(
        SQLEnum(TicketStatus, name="ticket_status_enum"), 
        default=TicketStatus.NEW,
        nullable=False
    )
    
    # Временные метки
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Связи
    user: Mapped[Optional[Any]] = relationship("User", back_populates="support_tickets")
    restaurant: Mapped[Optional[Any]] = relationship(
        "Restaurant", back_populates="support_tickets"
    )
    attachments: Mapped[List["SupportAttachment"]] = relationship(
        "SupportAttachment", back_populates="ticket", lazy="selectin", cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<SupportTicket #{self.id} - {self.status.value}>"


class SupportAttachment(Base):
    __tablename__ = "support_attachments"
    
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    ticket_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("support_tickets.id", ondelete="CASCADE"), 
        nullable=False,
        index=True
    )
    
    # Информация о файле
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_type: Mapped[str] = mapped_column(String(50), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)  # Размер в байтах
    
    # Временные метки
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    # Связи
    ticket: Mapped["SupportTicket"] = relationship("SupportTicket", back_populates="attachments")
    
    def __repr__(self):
        return f"<SupportAttachment {self.file_name} ({self.file_size} bytes)>"