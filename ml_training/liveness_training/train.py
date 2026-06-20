"""Обучение модели liveness. Файл: ml_training/liveness_training/train.py"""
import logging
import copy
import torch
import torch.nn as nn
from torch.optim import Adam
from torch.optim.lr_scheduler import CosineAnnealingLR

logger = logging.getLogger(__name__)


def train_model(model, train_loader, val_loader, epochs: int = 30,
                lr: float = 1e-4, device: str = "cuda"):
    """Обучение с сохранением лучшей модели по валидации."""
    model = model.to(device)
    criterion = nn.BCELoss()  # бинарная кросс-энтропия
    optimizer = Adam(model.parameters(), lr=lr, weight_decay=1e-5)
    scheduler = CosineAnnealingLR(optimizer, T_max=epochs)
    best_acc, best_state = 0.0, copy.deepcopy(model.state_dict())
    for epoch in range(epochs):
        model.train()
        running_loss = 0.0
        for images, labels in train_loader:
            images = images.to(device)
            labels = labels.to(device).unsqueeze(1)
            optimizer.zero_grad()
            loss = criterion(model(images), labels)
            loss.backward()
            optimizer.step()
            running_loss += loss.item()
        scheduler.step()
        val_acc = _validate(model, val_loader, device)
        logger.info("Эпоха %d/%d: loss=%.4f val_acc=%.4f", epoch + 1, epochs,
                    running_loss / len(train_loader), val_acc)
        if val_acc > best_acc:
            best_acc, best_state = val_acc, copy.deepcopy(model.state_dict())
    model.load_state_dict(best_state)
    return model


def _validate(model, val_loader, device: str) -> float:
    """Точность на валидационной выборке."""
    model.eval()
    correct = total = 0
    with torch.no_grad():
        for images, labels in val_loader:
            images = images.to(device)
            labels = labels.to(device).unsqueeze(1)
            preds = (model(images) >= 0.5).float()
            correct += (preds == labels).sum().item()
            total += labels.size(0)
    return correct / total if total else 0.0
