from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from starlette.middleware.sessions import SessionMiddleware

from app.core.config import settings
from app.api.v1.router import api_router
from app.db.base import Base
from app.db.session import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Создаем таблицы при запуске (если их нет)
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

# Session middleware для хранения авторизации
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY,
    session_cookie="grilnica_session",
    max_age=60 * 60 * 24 * 30,  # 30 дней
)

# CORS
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Подключаем API роутер
app.include_router(api_router, prefix="/api/v1")

# Пути
BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = BASE_DIR / "app" / "frontend" / "templates"
STATIC_DIR = BASE_DIR / "app" / "frontend" / "src"

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Статические файлы
if STATIC_DIR.exists():
    app.mount("/src", StaticFiles(directory=str(STATIC_DIR)), name="src")


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


@app.get("/menu/combo/combo-balls-foodattack", response_class=HTMLResponse)
async def menu_combo_balls_foodattack(request: Request):
    return templates.TemplateResponse(request, "product-detail.html")


@app.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    # Если пользователь уже авторизован, перенаправляем в профиль
    if request.session.get("user_id"):
        return RedirectResponse(url="/profile")
    return templates.TemplateResponse(request, "login.html")


@app.get("/profile", response_class=HTMLResponse)
async def profile(request: Request):
    # Проверяем авторизацию
    if not request.session.get("user_id"):
        return RedirectResponse(url="/login")
    return templates.TemplateResponse(request, "profile.html")


@app.get("/basket", response_class=HTMLResponse)
async def basket(request: Request):
    return templates.TemplateResponse(request, "basket.html")


@app.get("/health")
async def health():
    return {"status": "ok"}