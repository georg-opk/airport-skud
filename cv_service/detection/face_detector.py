"""Детектирование лиц (RetinaFace, InsightFace).
Файл: cv_service/detection/face_detector.py"""
import logging
from dataclasses import dataclass
from typing import List
import numpy as np
from insightface.app import FaceAnalysis
from insightface.utils import face_align

logger = logging.getLogger(__name__)


@dataclass
class FaceInfo:
    """Информация об обнаруженном лице."""
    bbox: np.ndarray
    landmarks: np.ndarray
    confidence: float
    face_id: int = 0


class FaceDetector:
    """Детектор лиц на основе RetinaFace."""

    def __init__(self, det_size: int = 640, conf_threshold: float = 0.5,
                 ctx_id: int = 0):
        self.conf_threshold = conf_threshold
        self._app = FaceAnalysis(allowed_modules=["detection"])
        self._app.prepare(ctx_id=ctx_id, det_size=(det_size, det_size))

    def detect(self, frame: np.ndarray) -> List[FaceInfo]:
        """Детекция всех лиц, сортировка по размеру."""
        if frame is None or frame.size == 0:
            return []
        try:
            faces = self._app.get(frame)
        except Exception as exc:
            logger.error("Ошибка детектирования: %s", exc)
            return []
        result = [FaceInfo(f.bbox, f.kps, float(f.det_score), i)
                  for i, f in enumerate(faces)
                  if f.det_score >= self.conf_threshold]
        result.sort(key=lambda fi: (fi.bbox[2] - fi.bbox[0]) *
                    (fi.bbox[3] - fi.bbox[1]), reverse=True)
        return result

    def align_face(self, frame: np.ndarray, face: FaceInfo) -> np.ndarray:
        """Выравнивание по 5 ключевым точкам к 112x112."""
        return face_align.norm_crop(frame, landmark=face.landmarks,
                                    image_size=112)
