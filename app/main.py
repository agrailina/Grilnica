from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
import os

from app.db.base import Base
from app.db.session import engine
from app.api.v1.router import api_router
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # При запуске
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # При завершении
    await engine.dispose()

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

# Подключаем папку с шаблонами
templates = Jinja2Templates(directory="app/frontend/templates")

# Подключаем статические файлы
if os.path.exists("src"):
    app.mount("app/frontend/src", StaticFiles(directory="src"), name="src")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/actions", response_class=HTMLResponse)
async def actions(request: Request):
    return templates.TemplateResponse("actions.html", {"request": request})

@app.get("/qual", response_class=HTMLResponse)
async def qual(request: Request):
    return templates.TemplateResponse("qual.html", {"request": request})

@app.get("/restaurants", response_class=HTMLResponse)
async def restaurants(request: Request):
    return templates.TemplateResponse("restorans.html", {"request": request})

@app.get("/menu/combo", response_class=HTMLResponse)
async def menu_combo(request: Request):
    return templates.TemplateResponse("combo.html", {"request": request})

@app.get("/menu/combo/combo-balls-foodattack", response_class=HTMLResponse)
async def menu_combo_balls_foodattack(request: Request):
    return templates.TemplateResponse("product-detail.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/profile", response_class=HTMLResponse)
async def profile(request: Request):
    return templates.TemplateResponse("profile.html", {"request": request})

@app.get("/basket", response_class=HTMLResponse)
async def basket(request: Request):
    return templates.TemplateResponse("basket.html", {"request": request})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)