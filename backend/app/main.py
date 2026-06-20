"""Точка входа серверной части (FastAPI). Файл: backend/app/main.py"""
import logging
import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api import employees, events, cv, auth, websocket
from app.db.database import init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="СКУД аэропорта", version="1.0",
              description="REST API системы контроля доступа (§2.8)")

# CORS: разрешаем запросы с дашборда оператора
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"],
                   allow_headers=["*"], allow_credentials=True)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Middleware логирования времени обработки запросов."""
    start = time.time()
    response = await call_next(request)
    logger.info("%s %s -> %d (%.1f мс)", request.method, request.url.path,
                response.status_code, (time.time() - start) * 1000)
    return response


@app.on_event("startup")
async def on_startup():
    """Инициализация ресурсов при запуске (БД, Milvus)."""
    init_db()
    logger.info("Приложение запущено")


@app.on_event("shutdown")
async def on_shutdown():
    """Освобождение ресурсов при остановке."""
    logger.info("Приложение остановлено")


# Регистрация маршрутов с префиксом /api/v1
for router in (auth.router, employees.router, events.router,
               cv.router, websocket.ws_router):
    app.include_router(router, prefix="/api/v1")
