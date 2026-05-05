from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID
from decimal import Decimal


class ProductBase(BaseModel):
    category_id: Optional[UUID] = None
    name: str = Field(..., min_length=1, max_length=300)
    slug: Optional[str] = Field(None, max_length=300)
    description: Optional[str] = None
    price: Decimal = Field(..., gt=0)
    image: Optional[str] = Field(None, max_length=500)
    is_available: bool = Field(default=True)
    is_active: bool = Field(default=True)


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    category_id: Optional[UUID] = None
    name: Optional[str] = Field(None, min_length=1, max_length=300)
    slug: Optional[str] = Field(None, max_length=300)
    description: Optional[str] = None
    price: Optional[Decimal] = Field(None, gt=0)
    image: Optional[str] = Field(None, max_length=500)
    is_available: Optional[bool] = None
    is_active: Optional[bool] = None


class ProductResponse(ProductBase):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ProductDetailResponse(ProductResponse):
    category: Optional["CategoryShortResponse"] = None


class CategoryShortResponse(BaseModel):
    id: UUID
    name: str
    slug: str

    class Config:
        from_attributes = True


class ProductListResponse(BaseModel):
    products: list[ProductResponse]
    total: int


class ProductFilterParams(BaseModel):
    category_id: Optional[UUID] = None
    category_slug: Optional[str] = None
    is_available: Optional[bool] = None
    search: Optional[str] = None
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=50, ge=1, le=100)