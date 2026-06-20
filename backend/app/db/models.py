"""ORM-модели (соответствуют таблицам §2.6). Файл: backend/app/db/models.py"""
from sqlalchemy import (Column, Integer, String, Float, DateTime,
                        ForeignKey, func)
from sqlalchemy.orm import relationship
from app.db.database import Base


class Employee(Base):
    """Сотрудник (таблица employees)."""
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(255), nullable=False)
    position = Column(String(100))
    department = Column(String(100))
    status = Column(String(20), default="активен")
    photo_path = Column(String)
    passes = relationship("Pass", back_populates="employee")


class Pass(Base):
    """Пропуск (таблица passes)."""
    __tablename__ = "passes"
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), index=True)
    pass_number = Column(String(50))
    status = Column(String(20), default="активен")
    employee = relationship("Employee", back_populates="passes")


class AccessEvent(Base):
    """Событие доступа (таблица access_events)."""
    __tablename__ = "access_events"
    id = Column(Integer, primary_key=True, index=True)
    event_time = Column(DateTime, server_default=func.now(), index=True)
    checkpoint_id = Column(Integer)
    employee_id = Column(Integer, index=True)
    result = Column(String(20))  # допуск / отказ / атака
    similarity_score = Column(Float)
    liveness_score = Column(Float)
    reason = Column(String)
