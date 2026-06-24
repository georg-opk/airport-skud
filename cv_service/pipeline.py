"""Конвейер биометрической идентификации (§2.4.3).
Файл: cv_service/pipeline.py"""
import time
import logging
from dataclasses import dataclass
from typing import Optional
import numpy as np

from detection.face_detector import FaceDetector
from recognition.face_recognizer import FaceRecognizer
from config import Config

logger = logging.getLogger(__name__)


@dataclass
class AccessResult:
    """Результат обработки кадра."""
    employee_id: Optional[int]
    similarity: float
    liveness_score: float
    decision: str
    reason: str
    processing_time: float


class BiometricPipeline:
    """Конвейер: детекция -> живость -> эмбеддинг -> сверка -> решение."""

    def __init__(self, detector, recognizer, liveness_detector, milvus_client):
        self.detector = detector
        self.recognizer = recognizer
        self.liveness = liveness_detector  # может быть None
        self.milvus = milvus_client

    def process(self, frame: np.ndarray,
                presented_id: Optional[int] = None) -> AccessResult:
        """Обработка кадра и принятие решения."""
        start = time.time()
        faces = self.detector.detect(frame)
        if not faces:
            return self._reject("no_face", start)
        aligned = self.detector.align_face(frame, faces[0])

        # проверка живости — только если детектор подключен
        if self.liveness is not None:
            liveness_score = self.liveness.check_liveness(aligned)
            if liveness_score < Config.LIVENESS_THRESHOLD:
                return self._reject("attack", start, liveness=liveness_score)
        else:
            liveness_score = 1.0  # без модели считаем живым

        embedding = self.recognizer.get_embedding(aligned)
        if presented_id is not None:
            employee_id, similarity = self._verify_1to1(embedding, presented_id)
        else:
            employee_id, similarity = self._identify_1toN(embedding)
        elapsed = time.time() - start
        if employee_id is not None and similarity >= Config.SIMILARITY_THRESHOLD:
            return AccessResult(employee_id, similarity, liveness_score,
                                "grant", "ok", elapsed)
        return AccessResult(None, similarity, liveness_score,
                            "reject", "no_match", elapsed)

    def _verify_1to1(self, embedding, presented_id):
        """Верификация 1:1 по предъявленному ID."""
        reference = self.milvus.get_embedding(presented_id)
        if reference is None:
            return None, 0.0
        is_match, similarity = self.recognizer.verify(
            embedding, reference, Config.SIMILARITY_THRESHOLD)
        return (presented_id if is_match else None), similarity

    def _identify_1toN(self, embedding):
        """Идентификация 1:N через Milvus."""
        hit = self.milvus.search(embedding, top_k=Config.TOP_K)
        if not hit:
            return None, 0.0
        return hit[0]["employee_id"], hit[0]["score"]

    @staticmethod
    def _reject(reason, start, liveness=0.0):
        """Формирование результата отказа."""
        return AccessResult(None, 0.0, liveness, "reject", reason,
                            time.time() - start)