from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.services.category_service import CategoryService
from app.services.product_service import ProductService
from app.schemas.product import ProductFilterParams

router = APIRouter(tags=["pages"])

# Настройка шаблонов
templates = Jinja2Templates(directory="app/frontend/templates")


@router.get("/category/{slug}", response_class=HTMLResponse)
async def category_page(
    request: Request,
    slug: str,
    db: AsyncSession = Depends(get_db)
):
    """Страница категории с товарами"""
    category_service = CategoryService(db)
    product_service = ProductService(db)
    
    # Получаем категорию
    category = await category_service.get_category_by_slug(slug)
    
    # Получаем товары категории
    filters = ProductFilterParams(
        category_slug=slug,
        is_available=True,
        limit=100
    )
    products, total = await product_service.get_filtered_products(filters)
    
    return templates.TemplateResponse(
        "menu/category.html",
        {
            "request": request,
            "category": category,
            "products": products,
            "total": total
        }
    )


@router.get("/product/{product_id}", response_class=HTMLResponse)
async def product_detail_page(
    request: Request,
    product_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Детальная страница товара"""
    from uuid import UUID
    
    product_service = ProductService(db)
    product = await product_service.get_product(UUID(product_id))
    
    return templates.TemplateResponse(
        "menu/product_detail.html",
        {
            "request": request,
            "product": product
        }
    )