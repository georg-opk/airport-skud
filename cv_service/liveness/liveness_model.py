"""Модель выявления живости (§2.5.1).
Файл: cv_service/liveness/liveness_model.py"""
import logging
import torch
import torch.nn as nn
from torchvision import models

logger = logging.getLogger(__name__)


class LivenessModel(nn.Module):
    """Бинарный классификатор живости на основе MobileNetV2."""

    def __init__(self, pretrained: bool = True):
        super().__init__()
        weights = "IMAGENET1K_V1" if pretrained else None
        backbone = models.mobilenet_v2(weights=weights)
        self.features = backbone.features
        self.pool = nn.AdaptiveAvgPool2d(1)
        self.classifier = nn.Sequential(
            nn.Dropout(0.5),                       # регуляризация
            nn.Linear(backbone.last_channel, 1),
        )
        self._init_weights()

    def _init_weights(self):
        """Инициализация весов классификатора (Ксавье)."""
        for m in self.classifier:
            if isinstance(m, nn.Linear):
                nn.init.xavier_uniform_(m.weight)
                nn.init.zeros_(m.bias)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Прямой проход: возвращает вероятность живости."""
        x = self.features(x)
        x = self.pool(x).flatten(1)
        return torch.sigmoid(self.classifier(x))
