"""Пакетная обработка кадров (§2.4.2).
Файл: cv_service/utils/batch_processor.py"""
import logging
from typing import List
import numpy as np

from pipeline import BiometricPipeline, AccessResult

logger = logging.getLogger(__name__)


class BatchProcessor:
    """Пакетная обработка кадров с нескольких КПП."""

    def __init__(self, pipeline: BiometricPipeline, batch_size: int = 8):
        self.pipeline = pipeline
        self.batch_size = batch_size

    def process_batch(self, frames: List[np.ndarray]) -> List[AccessResult]:
        """Обработка пакета кадров."""
        results = []
        for i in range(0, len(frames), self.batch_size):
            for frame in frames[i:i + self.batch_size]:
                try:
                    results.append(self.pipeline.process(frame))
                except Exception as exc:
                    logger.error("Ошибка обработки кадра: %s", exc)
                    results.append(AccessResult(None, 0.0, 0.0,
                                                "reject", "error", 0.0))
        return results
