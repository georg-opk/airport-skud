"""Клиент CV-сервиса. Файл: backend/app/services/cv_client.py"""
import logging
from fastapi import UploadFile
import cv2
import numpy as np
from pathlib import Path
import sys

# Добавляем путь к cv_service
sys.path.append(str(Path(__file__).parent.parent.parent.parent / 'cv_service'))

from cv_service.pipeline import BiometricPipeline
from cv_service.detection.face_detector import FaceDetector
from cv_service.recognition.face_recognizer import FaceRecognizer
from cv_service.liveness.liveness_detector import LivenessDetector
from cv_service.config import Config
from backend.app.db.milvus_client import MilvusClient

logger = logging.getLogger(__name__)

# Глобальные объекты (инициализируются при первом вызове)
_pipeline = None


def _get_pipeline():
    """Получение или создание конвейера CV."""
    global _pipeline
    if _pipeline is None:
        detector = FaceDetector(ctx_id=Config.CTX_ID)
        recognizer = FaceRecognizer(Config.ARCFACE_MODEL, ctx_id=Config.CTX_ID)
        liveness_detector = LivenessDetector(Config.LIVENESS_MODEL, ctx_id=Config.CTX_ID)
        milvus_client = MilvusClient()
        _pipeline = BiometricPipeline(detector, recognizer, liveness_detector, milvus_client)
    return _pipeline


async def build_embedding_from_upload(photo: UploadFile) -> np.ndarray:
    """Построение эмбеддинга из загруженного фото."""
    contents = await photo.read()
    nparr = np.frombuffer(contents, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    pipeline = _get_pipeline()
    faces = pipeline.detector.detect(frame)
    if not faces:
        raise ValueError("Лицо не обнаружено")

    aligned = pipeline.detector.align_face(frame, faces[0])
    embedding = pipeline.recognizer.get_embedding(aligned)
    return embedding


async def identify_frame(frame: UploadFile, presented_id=None) -> dict:
    """Идентификация по кадру."""
    contents = await frame.read()
    nparr = np.frombuffer(contents, np.uint8)
    frame_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    pipeline = _get_pipeline()
    result = pipeline.process(frame_np, presented_id)

    return {
        "employee_id": result.employee_id,
        "similarity": result.similarity,
        "liveness_score": result.liveness_score,
        "decision": result.decision,
        "reason": result.reason,
        "processing_time": result.processing_time
    }