"""
Pydantic-схемы для REST API СКУД.
Файл: backend/app/models/schemas.py
Соответствует спецификации OpenAPI (Приложение Д).
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# ===== Сотрудники =====

class EmployeeCreate(BaseModel):
    """Схема создания сотрудника (POST /employees)."""
    full_name: str = Field(..., min_length=1, max_length=255, description="ФИО сотрудника")
    position: Optional[str] = Field("", max_length=100, description="Должность")
    department: Optional[str] = Field("", max_length=100, description="Подразделение")


class EmployeeResponse(BaseModel):
    """Схема ответа с данными сотрудника (GET /employees)."""
    id: int
    full_name: str
    position: Optional[str] = None
    department: Optional[str] = None
    status: str = "активен"
    photo_path: Optional[str] = None

    class Config:
        from_attributes = True  # поддержка ORM-моделей SQLAlchemy


# ===== Пропуска =====

class PassCreate(BaseModel):
    """Схема выдачи пропуска (POST /passes)."""
    employee_id: int
    pass_number: str = Field(..., max_length=50)
    access_level: int = Field(1, ge=1, le=5)
    expiry_date: Optional[datetime] = None


class PassResponse(BaseModel):
    """Схема ответа с данными пропуска."""
    id: int
    employee_id: int
    pass_number: str
    status: str = "активен"
    access_level: int

    class Config:
        from_attributes = True


# ===== События доступа =====

class AccessEventResponse(BaseModel):
    """Схема ответа с событием доступа (GET /events)."""
    id: int
    event_time: datetime
    checkpoint_id: Optional[int] = None
    employee_id: Optional[int] = None
    result: str  # "допуск" / "отказ" / "атака"
    similarity_score: Optional[float] = None
    liveness_score: Optional[float] = None
    reason: Optional[str] = None

    class Config:
        from_attributes = True


# ===== Аутентификация =====

class LoginRequest(BaseModel):
    """Схема запроса на вход (POST /auth/login)."""
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)


class TokenResponse(BaseModel):
    """Схема ответа с JWT-токеном."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # время жизни в секундах


# ===== CV / Идентификация =====

class IdentifyResponse(BaseModel):
    """Схема ответа от CV-сервиса (POST /cv/identify)."""
    employee_id: Optional[int] = None
    similarity: float
    liveness_score: float
    decision: str  # "grant" / "reject"
    reason: str    # "ok" / "no_match" / "attack" / "no_face"
    processing_time: Optional[float] = None


class CVStatusResponse(BaseModel):
    """Схема статуса CV-сервиса (GET /cv/status)."""
    status: str


# ===== Зоны =====

class ZoneCreate(BaseModel):
    """Схема создания зоны (POST /zones)."""
    zone_name: str = Field(..., max_length=100)
    zone_type: Optional[str] = Field("", max_length=50)
    security_level: int = Field(1, ge=1, le=5)


class ZoneResponse(BaseModel):
    """Схема ответа с данными зоны."""
    id: int
    zone_name: str
    zone_type: Optional[str] = None
    security_level: int

    class Config:
        from_attributes = True


# ===== Чёрный список =====

class BlacklistCreate(BaseModel):
    """Схема добавления в чёрный список (POST /blacklist)."""
    person_id: str = Field(..., max_length=50)
    full_name: str = Field(..., max_length=255)
    reason: Optional[str] = None


class BlacklistResponse(BaseModel):
    """Схема ответа из чёрного списка."""
    id: int
    person_id: str
    full_name: str
    add_date: datetime
    reason: Optional[str] = None

    class Config:
        from_attributes = True