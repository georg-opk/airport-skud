"""Эндпоинты управления сотрудниками (§2.8, таблица 2.18).
Файл: backend/app/api/employees.py"""
import logging
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Employee
from app.db.milvus_client import MilvusClient
from app.models.schemas import EmployeeResponse
from app.services.cv_client import build_embedding_from_upload

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/employees", tags=["employees"])

_milvus = None


def get_milvus():
    """Ленивая инициализация Milvus (не при импорте модуля)."""
    global _milvus
    if _milvus is None:
        _milvus = MilvusClient()
    return _milvus


@router.get("", response_model=list[EmployeeResponse])
def list_employees(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    """GET /employees — список сотрудников с пагинацией."""
    return db.query(Employee).offset(skip).limit(limit).all()


@router.get("/{emp_id}", response_model=EmployeeResponse)
def get_employee(emp_id: int, db: Session = Depends(get_db)):
    """GET /employees/{id} — детали сотрудника."""
    emp = db.query(Employee).get(emp_id)
    if emp is None:
        raise HTTPException(status_code=404, detail="Сотрудник не найден")
    return emp


@router.post("", response_model=EmployeeResponse, status_code=201)
async def create_employee(full_name: str, position: str = "",
                          photo: UploadFile = File(...),
                          db: Session = Depends(get_db)):
    """POST /employees — регистрация сотрудника с фото."""
    emp = Employee(full_name=full_name, position=position)
    db.add(emp); db.commit(); db.refresh(emp)
    try:
        embedding = await build_embedding_from_upload(photo)
        get_milvus().insert_embedding(emp.id, embedding)
    except Exception as exc:
        logger.error("Ошибка построения эмбеддинга: %s", exc)
        raise HTTPException(status_code=400, detail="Ошибка обработки фото")
    return emp


@router.delete("/{emp_id}")
def delete_employee(emp_id: int, db: Session = Depends(get_db)):
    """DELETE /employees/{id} — логическое увольнение."""
    emp = db.query(Employee).get(emp_id)
    if emp is None:
        raise HTTPException(status_code=404, detail="Сотрудник не найден")
    emp.status = "уволен"
    db.commit()
    get_milvus().delete_embedding(emp_id)
    return {"status": "ok"}

