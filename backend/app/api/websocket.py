"""WebSocket для доставки оповещений (§2.9).
Файл: backend/app/api/websocket.py"""
import logging
from typing import List
from fastapi import APIRouter, WebSocket

logger = logging.getLogger(__name__)
ws_router = APIRouter()
_clients: List[WebSocket] = []  # подключённые дашборды


@ws_router.websocket("/ws/alerts")
async def alerts_socket(ws: WebSocket):
    """WebSocket-канал доставки оповещений оператору."""
    await ws.accept()
    _clients.append(ws)
    try:
        while True:
            await ws.receive_text()  # поддержание соединения
    except Exception:
        _clients.remove(ws)  # отключение клиента


async def broadcast_alert(alert: dict):
    """Рассылка оповещения всем подключённым дашбордам."""
    for client in list(_clients):
        try:
            await client.send_json(alert)
        except Exception as exc:
            logger.error("Ошибка отправки алерта: %s", exc)
