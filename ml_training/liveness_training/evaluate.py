"""Оценка качества модели liveness (§1.4.3).
Файл: ml_training/liveness_training/evaluate.py"""
import logging
import torch

logger = logging.getLogger(__name__)


def evaluate_model(model, test_loader, device: str = "cuda",
                   threshold: float = 0.5) -> dict:
    """Вычисление APCER, BPCER, ACER на тестовой выборке."""
    model = model.to(device).eval()
    attack_total = attack_err = bona_total = bona_err = 0
    with torch.no_grad():
        for images, labels in test_loader:
            scores = model(images.to(device)).cpu().flatten()
            preds = (scores >= threshold).int()
            for pred, label in zip(preds, labels.int()):
                if label == 0:  # атака
                    attack_total += 1
                    attack_err += int(pred == 1)
                else:  # живой
                    bona_total += 1
                    bona_err += int(pred == 0)
    apcer = attack_err / attack_total if attack_total else 0.0
    bpcer = bona_err / bona_total if bona_total else 0.0
    acer = (apcer + bpcer) / 2
    metrics = {"APCER": round(apcer, 4), "BPCER": round(bpcer, 4),
               "ACER": round(acer, 4)}
    logger.info("Метрики: %s", metrics)
    return metrics
