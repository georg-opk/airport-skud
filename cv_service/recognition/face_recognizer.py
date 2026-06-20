"""Распознавание лиц (ArcFace, InsightFace).
Файл: cv_service/recognition/face_recognizer.py"""
import logging
from typing import Tuple
import numpy as np
from insightface.model_zoo import get_model

logger = logging.getLogger(__name__)


class FaceRecognizer:
    """Построение эмбеддингов и верификация (ArcFace)."""

    def __init__(self, model_path: str, ctx_id: int = 0):
        self._model = get_model(model_path)
        self._model.prepare(ctx_id=ctx_id)

    def get_embedding(self, aligned_face: np.ndarray) -> np.ndarray:
        """512-мерный эмбеддинг с нормировкой L2."""
        embedding = self._model.get_feat(aligned_face).flatten()
        norm = np.linalg.norm(embedding)
        if norm == 0:
            return embedding.astype(np.float32)
        return (embedding / norm).astype(np.float32)

    def verify(self, e1: np.ndarray, e2: np.ndarray,
               threshold: float = 0.6) -> Tuple[bool, float]:
        """Верификация 1:1 по косинусной близости."""
        similarity = float(np.dot(e1, e2))
        return similarity >= threshold, similarity
