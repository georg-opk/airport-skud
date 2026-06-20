"""Эндпоинты журнала событий доступа (§2.8).
Файл: backend/app/api/events.py"""
import logging
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.database import get_db
from app.db.models import AccessEvent

logger = logging.getLogger(__name__)
router = APIRouter(tags=["events"])


@router.get("/events")
def list_events(zone_id: int = None, result: str = None,
                db: Session = Depends(get_db)):
    """GET /events — журнал событий с фильтрацией."""
    query = db.query(AccessEvent)
    if result:
        query = query.filter(AccessEvent.result == result)
    return query.order_by(AccessEvent.event_time.desc()).limit(100).all()


@router.get("/events/stats")
def events_stats(db: Session = Depends(get_db)):
    """GET /events/stats — агрегаты по результатам."""
    rows = (db.query(AccessEvent.result, func.count().label("cnt"))
            .group_by(AccessEvent.result).all())
    return {r.result: r.cnt for r in rows}
