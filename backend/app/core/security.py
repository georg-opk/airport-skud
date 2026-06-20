"""JWT-аутентификация и хэширование паролей (§2.10).
Файл: backend/app/core/security.py"""
import logging
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext

logger = logging.getLogger(__name__)

SECRET_KEY = "CHANGE_ME"            # ключ из защищённого хранилища
ALGORITHM = "HS256"
ACCESS_TTL_MIN = 15                 # время жизни access-токена (§2.10)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def hash_password(password: str) -> str:
    """Хэширование пароля алгоритмом bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    """Проверка пароля по хэшу."""
    return pwd_context.verify(plain, hashed)


def create_access_token(data: dict, ttl_min: int = ACCESS_TTL_MIN) -> str:
    """Создание JWT-токена с заданным временем жизни."""
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + timedelta(minutes=ttl_min)
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """Проверка токена и извлечение пользователя."""
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=401, detail="Недействительный токен")
