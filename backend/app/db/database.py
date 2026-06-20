"""Подключение к PostgreSQL. Файл: backend/app/db/database.py"""
import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL",
                         "postgresql://scud:scud@localhost:5432/scud")
# движок с пулом соединений (§2.6.2)
engine = create_engine(DATABASE_URL, pool_size=10, max_overflow=20)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()


def get_db():
    """Dependency FastAPI: выдаёт сессию БД и закрывает её."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Создание таблиц при первом запуске."""
    Base.metadata.create_all(bind=engine)
    logger.info("Схема базы данных инициализирована")
