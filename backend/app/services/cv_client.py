"""Клиент CV-сервиса. Файл: backend/app/services/cv_client.py

- Согласованный корень импортов: каталог cv_service добавляется в sys.path.
- MilvusClient импортируется как app.db.milvus_client.
- Ленивая и отказоустойчивая инициализация конвейера.
- LivenessDetector подключается только если файл модели существует.
"""
import logging
from pathlib import Path
import sys
import cv2
import numpy as np
from fastapi import UploadFile

logger = logging.getLogger(__name__)

_CV_SERVICE_DIR = Path(__file__).resolve().parents[3]
if str(_CV_SERVICE_DIR) not in sys.path:
    sys.path.insert(0, str(_CV_SERVICE_DIR))

_pipeline = None
_init_error = None


def _get_pipeline():
    """Ленивое создание конвейера CV. Ошибки инициализации не пробрасываются."""
    global _pipeline, _init_error
    if _pipeline is not None:
        return _pipeline
    if _init_error is not None:
        return None
    try:
        from pipeline import BiometricPipeline
        from detection.face_detector import FaceDetector
        from recognition.face_recognizer import FaceRecognizer
        from config import Config
        from app.db.milvus_client import MilvusClient

        detector = FaceDetector(conf_threshold=Config.DETECTION_CONFIDENCE,
                                ctx_id=Config.CTX_ID)
        recognizer = FaceRecognizer(Config.ARCFACE_MODEL, ctx_id=Config.CTX_ID)

        # Живость — только если файл модели существует
        liveness_model_path = _CV_SERVICE_DIR / Config.LIVENESS_MODEL
        if liveness_model_path.exists():
            from liveness.liveness_detector import LivenessDetector
            liveness = LivenessDetector(str(liveness_model_path),
                                        ctx_id=Config.CTX_ID)
        else:
            logger.warning("Модель живости не найдена (%s), проверка пропущена",
                           liveness_model_path)
            liveness = None

        milvus = MilvusClient(host=Config.MILVUS_HOST, port=Config.MILVUS_PORT,
                              collection=Config.MILVUS_COLLECTION)
        _pipeline = BiometricPipeline(detector, recognizer, liveness, milvus)
        logger.info("Конвейер CV инициализирован (модель %s)", Config.ARCFACE_MODEL)
    except Exception as exc:
        _init_error = exc
        logger.error("Не удалось инициализировать конвейер CV: %s", exc)
        return None
    return _pipeline


def _decode(contents: bytes):
    nparr = np.frombuffer(contents, np.uint8)
    return cv2.imdecode(nparr, cv2.IMREAD_COLOR)


async def build_embedding_from_upload(photo: UploadFile) -> np.ndarray:
    """Построение эмбеддинга из загруженного фото (для регистрации)."""
    frame = _decode(await photo.read())
    pipeline = _get_pipeline()
    if pipeline is None:
        raise RuntimeError("CV-сервис недоступен")
    faces = pipeline.detector.detect(frame)
    if not faces:
        raise ValueError("Лицо не обнаружено")
    aligned = pipeline.detector.align_face(frame, faces[0])
    return pipeline.recognizer.get_embedding(aligned)


async def identify_frame(frame: UploadFile, presented_id=None) -> dict:
    """Идентификация по кадру. Всегда возвращает словарь без исключений."""
    try:
        frame_np = _decode(await frame.read())
    except Exception as exc:
        logger.error("Ошибка декодирования кадра: %s", exc)
        return _error("bad_frame")

    if frame_np is None:
        return _error("bad_frame")

    pipeline = _get_pipeline()
    if pipeline is None:
        return _error("cv_unavailable")

    try:
        result = pipeline.process(frame_np, presented_id)
    except Exception as exc:
        logger.error("Ошибка обработки кадра: %s", exc)
        return _error("cv_error")

    return {
        "employee_id": result.employee_id,
        "similarity": result.similarity,
        "liveness_score": result.liveness_score,
        "decision": result.decision,
        "reason": result.reason,
        "processing_time": result.processing_time,
    }


def _error(reason: str) -> dict:
    """Структурированный отказ при невозможности обработки."""
    return {"employee_id": None, "similarity": 0.0, "liveness_score": 0.0,
            "decision": "reject", "reason": reason, "processing_time": 0.0}