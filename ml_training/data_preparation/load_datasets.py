"""Загрузка и парсинг датасетов. Файл: ml_training/data_preparation/load_datasets.py"""
import logging
from pathlib import Path
import pandas as pd

logger = logging.getLogger(__name__)
LABEL_BONAFIDE = 0  # метка живого лица
LABEL_ATTACK = 1  # метка атаки


def load_celeba_spoof(dataset_path: str) -> pd.DataFrame:
    """Загрузка CelebA-Spoof и парсинг разметки."""
    dataset_path = Path(dataset_path)
    if not dataset_path.exists():
        raise FileNotFoundError(f"Датасет не найден: {dataset_path}")
    records = []
    with open(dataset_path / "annotations.txt", "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) < 2:
                continue
            rel_path, attack_type = parts[0], int(parts[1])
            img_path = dataset_path / rel_path
            if not img_path.exists():
                logger.warning("Файл не найден: %s", img_path)
                continue
            label = LABEL_BONAFIDE if attack_type == 0 else LABEL_ATTACK
            records.append({"image_path": str(img_path), "label": label,
                            "attack_type": attack_type,
                            "attributes": " ".join(parts[2:])})
    df = pd.DataFrame(records)
    logger.info("Загружено %d изображений", len(df))
    return df
