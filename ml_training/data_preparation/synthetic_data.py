"""Генерация синтетических атак.
Файл: ml_training/data_preparation/synthetic_data.py"""
import logging
import cv2
import numpy as np

logger = logging.getLogger(__name__)


def _add_print_artifacts(image: np.ndarray) -> np.ndarray:
    """Имитация фотопечати: размытие и снижение насыщенности."""
    blurred = cv2.GaussianBlur(image, (3, 3), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_RGB2HSV).astype(np.float32)
    hsv[..., 1] *= 0.85
    return cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB)


def _add_moire(image: np.ndarray) -> np.ndarray:
    """Имитация муаровых паттернов от экрана."""
    w = image.shape[1]
    pattern = (np.sin(np.arange(w) * 0.6) * 10).astype(np.int16)
    return np.clip(image.astype(np.int16) + pattern[None, :, None],
                   0, 255).astype(np.uint8)


def generate_synthetic_attacks(image: np.ndarray) -> list:
    """Генерация синтетических атак из изображения живого лица."""
    result = []
    try:
        result.append(_add_print_artifacts(image))
        result.append(_add_moire(image))
    except Exception as exc:
        logger.error("Ошибка генерации: %s", exc)
    return result
