import uuid
from sqlalchemy import String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.db.base import Base
from typing import Optional, Any
from datetime import datetime


class LegalEntity(Base):
    __tablename__ = "legal_entities"
    
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False,
        index=True
    )
    
    # Данные организации
    company_name: Mapped[str] = mapped_column(String(300), nullable=False)
    inn: Mapped[str] = mapped_column(String(12), nullable=False, index=True)
    email_for_invoice: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Статус
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Временные метки
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    
    # Связи
    user: Mapped[Any] = relationship("User", back_populates="legal_entities")
    
    def __repr__(self):
        return f"<LegalEntity {self.company_name} (ИНН: {self.inn})>"