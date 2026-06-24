"""Эндпоинты интеграции с CV-сервисом (§2.8, §3.4).
Файл: backend/app/api/cv.py"""
import logging
from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import AccessEvent
from app.services.cv_client import identify_frame

logger = logging.getLogger(__name__)
router = APIRouter(tags=["cv"])


@router.post("/cv/identify")
async def cv_identify(checkpoint_id: int, presented_id: int = None,
                      frame: UploadFile = File(...),
                      db: Session = Depends(get_db)):
    """POST /cv/identify — идентификация по кадру и запись события."""
    result = await identify_frame(frame, presented_id)   # вызов конвейера §3.4
    try:
        event = AccessEvent(
            checkpoint_id=checkpoint_id,
            employee_id=result.get("employee_id"),
            result=result.get("decision", "reject"),
            similarity_score=result.get("similarity", 0.0),
            liveness_score=result.get("liveness_score", 0.0),
            reason=result.get("reason", ""),
        )
        db.add(event)
        db.commit()
    except Exception as exc:  # noqa: BLE001
        db.rollback()
        logger.error("Не удалось записать событие доступа: %s", exc)
    return result


@router.get("/cv/status")
def cv_status():
    """GET /cv/status — статус CV-сервиса."""
    return {"status": "ok"}

