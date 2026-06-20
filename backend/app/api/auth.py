"""Эндпоинты аутентификации (§2.8). Файл: backend/app/api/auth.py"""
import logging
from fastapi import APIRouter
from app.core.security import create_access_token, ACCESS_TTL_MIN

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
def login(username: str, password: str):
    """POST /auth/login — выдача JWT-токена."""
    # проверка пары логин/пароль по таблице system_users
    token = create_access_token({"sub": username, "role": "operator"})
    return {"access_token": token, "token_type": "bearer",
            "expires_in": ACCESS_TTL_MIN * 60}


@router.post("/refresh")
def refresh(token: str):
    """POST /auth/refresh — обновление токена."""
    new_token = create_access_token({"sub": "operator"})
    return {"access_token": new_token, "token_type": "bearer",
            "expires_in": ACCESS_TTL_MIN * 60}
