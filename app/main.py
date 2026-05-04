from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Grilnica API with PostgreSQL",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url=None,
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
    return templates.TemplateResponse(request, "login.html")


@app.get("/profile", response_class=HTMLResponse)
async def profile(request: Request):
    return templates.TemplateResponse(request, "profile.html")


@app.get("/basket", response_class=HTMLResponse)
async def basket(request: Request):
    return templates.TemplateResponse(request, "basket.html")


@app.get("/health")
async def health():
    return {"status": "ok"}