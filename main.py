from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI()

# Проверяем, что папка templates существует
if not os.path.exists("templates"):
    os.makedirs("templates")
    print("Создана папка templates")

# Подключаем папку с шаблонами
templates = Jinja2Templates(directory="templates")

# Подключаем статические файлы
if os.path.exists("src"):
    app.mount("/src", StaticFiles(directory="src"), name="src")
else:
    print("ВНИМАНИЕ: Папка src не найдена!")

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

# Для отладки - проверка содержимого файла
@app.get("/debug/{filename}")
async def debug_file(filename: str):
    """Показывает содержимое файла шаблона для отладки"""
    filepath = f"templates/{filename}"
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        return HTMLResponse(f"<pre>{content[:1000]}</pre>")
    return HTMLResponse(f"Файл {filepath} не найден")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)