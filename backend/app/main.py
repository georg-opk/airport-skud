"""Точка входа серверной части (FastAPI). Файл: backend/app/main.py"""
import logging
import time
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.api import employees, events, cv, auth, websocket
from app.db.database import init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Путь к папке фронтенда (на уровень выше backend/)
FRONTEND_DIR = Path(__file__).resolve().parent.parent.parent / "frontend"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Современный способ инициализации ресурсов (вместо on_event)."""
    init_db()
    logger.info("Приложение запущено")
    yield
    logger.info("Приложение остановлено")


app = FastAPI(
    title="СКУД аэропорта",
    version="1.0",
    description="REST API системы контроля доступа (§2.8)",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=False,
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    logger.info("%s %s -> %d (%.1f мс)", request.method, request.url.path,
                response.status_code, (time.time() - start) * 1000)
    return response


# API-маршруты ( ДО статических файлов!)
for router in (auth.router, employees.router, events.router,
               cv.router, websocket.ws_router):
    app.include_router(router, prefix="/api/v1")


# Корень — редирект на страницу входа
@app.get("/")
def root():
    return FileResponse(FRONTEND_DIR / "login.html")


# Раздача статики — ПОСЛЕ всех API-роутов
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")


# ===== Запуск сервера =====
if __name__ == "__main__":
    import uvicorn

    print("\n" + "=" * 50)
    print("Запуск СКУД API...")
    print("=" * 50)
    print("Вход:       http://localhost:8000/login.html")
    print("Swagger UI: http://localhost:8000/docs")
    print("=" * 50 + "\n")

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )