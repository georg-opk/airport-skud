"""Аугментация данных (§2.5.2). Файл: ml_training/data_preparation/augmentation.py"""
import logging
import random
import numpy as np
import torchvision.transforms as T

logger = logging.getLogger(__name__)


class DataAugmentor:
    """Случайные преобразования изображения лица."""

    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        self.transform = T.Compose([
            T.RandomRotation(degrees=15),               # поворот ±15°
            T.ColorJitter(brightness=0.2, contrast=0.2),  # яркость/контраст
            T.RandomResizedCrop(112, scale=(0.85, 1.0)),  # случайный кроп
            T.RandomHorizontalFlip(p=0.5),              # отражение
        ])

    def apply_augmentation(self, image: np.ndarray) -> np.ndarray:
        """Применение аугментации (numpy HWC, RGB)."""
        if not self.enabled:
            return image
        try:
            tensor = T.functional.to_tensor(image)
            augmented = self.transform(tensor).permute(1, 2, 0).numpy()
        except Exception as exc:
            logger.error("Ошибка аугментации: %s", exc)
            return image
        if random.random() < 0.5:                       # гауссов шум
            noise = np.random.normal(0, 0.02, augmented.shape).astype(np.float32)
            augmented = np.clip(augmented + noise, 0.0, 1.0)
        return augmented
