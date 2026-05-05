from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.api.v1.router import api_router
from app.db.base import Base
from app.db.session import engine
from app.api.deps import get_db
from app.services.product_service import ProductService
from app.schemas.product import ProductFilterParams


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Grilnica API with PostgreSQL",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url=None,
)

# Middleware
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY,
    session_cookie="grilnica_session",
    max_age=60 * 60 * 24 * 30,
)

if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix="/api/v1")

BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = BASE_DIR / "app" / "frontend" / "templates"
STATIC_DIR = BASE_DIR / "app" / "frontend" / "src"

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

if STATIC_DIR.exists():
    app.mount("/src", StaticFiles(directory=str(STATIC_DIR)), name="src")


# ========== ПРЯМОЙ ЭНДПОИНТ ДЛЯ КОМБО ==========
@app.get("/api/v1/combo-products")
async def get_combo(db: AsyncSession = Depends(get_db)):
    """Получить товары Комбо в правильном порядке"""
    try:
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload
        from app.models.product import Product
        from app.models.category import Category
        
        # Прямой SQL-запрос с правильной сортировкой
        query = (
            select(Product)
            .options(selectinload(Product.category))
            .join(Product.category)
            .where(Category.slug == "combo")
            .where(Product.is_active == True)
            .where(Product.is_available == True)
            .order_by(Product.created_at.asc())  # Сортировка по дате создания
            .limit(50)
        )
        
        result = await db.execute(query)
        products = result.scalars().all()
        
        return {
            "products": [
                {
                    "id": str(p.id),
                    "name": p.name,
                    "slug": p.slug if hasattr(p, 'slug') and p.slug else '',
                    "description": p.description or "",
                    "price": str(p.price),
                    "image": p.image or "",
                }
                for p in products
            ],
            "total": len(products)
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse({"error": str(e), "products": [], "total": 0})
    
# Добавьте страницу для /menu/combo/{slug}
@app.get("/menu/combo/{product_slug}", response_class=HTMLResponse)
async def menu_combo_product(request: Request, product_slug: str):
    return templates.TemplateResponse(request, "product-detail.html")


# Добавьте API для получения товара по slug
@app.get("/api/v1/product-by-slug/{slug}")
async def get_product_by_slug(slug: str, db: AsyncSession = Depends(get_db)):
    """Получить товар по slug"""
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload
    from app.models.product import Product
    
    try:
        # Загружаем товар вместе с категорией
        query = (
            select(Product)
            .options(selectinload(Product.category))
            .where(Product.slug == slug)
        )
        result = await db.execute(query)
        product = result.scalar_one_or_none()
        
        if not product:
            return JSONResponse({"error": "Товар не найден"}, status_code=404)
        
        # Формируем ответ вручную,以避免 ошибок сериализации
        response_data = {
            "id": str(product.id),
            "name": product.name,
            "slug": product.slug if hasattr(product, 'slug') and product.slug else "",
            "description": product.description or "",
            "price": str(product.price),
            "image": product.image or "",
            "is_available": product.is_available if hasattr(product, 'is_available') else True,
        }
        
        # Добавляем категорию, если есть
        if product.category:
            response_data["category"] = {
                "id": str(product.category.id),
                "name": product.category.name,
                "slug": product.category.slug,
            }
        else:
            response_data["category"] = {
                "id": None,
                "name": "Комбо",
                "slug": "combo",
            }
        
        return response_data
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse({"error": str(e)}, status_code=500)


# ========== СТРАНИЦЫ ==========
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request, "index.html")

@app.get("/actions", response_class=HTMLResponse)
async def actions(request: Request):
    return templates.TemplateResponse(request, "actions.html")

@app.get("/qual", response_class=HTMLResponse)
async def qual(request: Request):
    return templates.TemplateResponse(request, "qual.html")

@app.get("/restaurants", response_class=HTMLResponse)
async def restaurants(request: Request):
    return templates.TemplateResponse(request, "restorans.html")

@app.get("/menu/combo", response_class=HTMLResponse)
async def menu_combo(request: Request):
    return templates.TemplateResponse(request, "combo.html")

@app.get("/product/{product_id}", response_class=HTMLResponse)
async def product_detail(request: Request, product_id: str):
    return templates.TemplateResponse(request, "product-detail.html")

@app.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    if request.session.get("user_id"):
        return RedirectResponse(url="/profile")
    return templates.TemplateResponse(request, "login.html")

@app.get("/profile", response_class=HTMLResponse)
async def profile(request: Request):
    if not request.session.get("user_id"):
        return RedirectResponse(url="/login")
    return templates.TemplateResponse(request, "profile.html")

@app.get("/basket", response_class=HTMLResponse)
async def basket(request: Request):
    return templates.TemplateResponse(request, "basket.html")

@app.get("/health")
async def health():
    return {"status": "ok"}