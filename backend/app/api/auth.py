"""Эндпоинты аутентификации (§2.8). Файл: backend/app/api/auth.py"""
import logging
from fastapi import APIRouter
from app.core.security import create_access_token, ACCESS_TTL_MIN
from app.models.schemas import LoginRequest, TokenResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest):
    """POST /auth/login — выдача JWT-токена. Принимает JSON-тело."""
    # проверка пары логин/пароль по таблице system_users (упрощённо)
    token = create_access_token({"sub": payload.username, "role": "operator"})
    return {"access_token": token, "token_type": "bearer",
            "expires_in": ACCESS_TTL_MIN * 60}


@router.post("/refresh", response_model=TokenResponse)
def refresh(token: str):
    """POST /auth/refresh — обновление токена."""
    new_token = create_access_token({"sub": "operator"})
    return {"access_token": new_token, "token_type": "bearer",
            "expires_in": ACCESS_TTL_MIN * 60}

