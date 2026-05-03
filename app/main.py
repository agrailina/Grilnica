from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI()


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