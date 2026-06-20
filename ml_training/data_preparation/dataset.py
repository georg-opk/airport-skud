"""Балансировка, разделение и DataLoader.
Файл: ml_training/data_preparation/dataset.py"""
import logging
import pandas as pd
from sklearn.model_selection import train_test_split
import torch
from torch.utils.data import Dataset, DataLoader

from .preprocess import preprocess_image
from .augmentation import DataAugmentor

logger = logging.getLogger(__name__)


def balance_classes(df: pd.DataFrame) -> pd.DataFrame:
    """Балансировка методом oversampling меньшего класса."""
    max_count = df["label"].value_counts().max()
    frames = [g.sample(max_count, replace=True, random_state=42)
              for _, g in df.groupby("label")]
    return pd.concat(frames).sample(frac=1, random_state=42).reset_index(drop=True)


def split_dataset(df: pd.DataFrame):
    """Стратифицированное разделение 80/10/10 (§2.5.2)."""
    train_df, temp = train_test_split(df, test_size=0.2,
                                      stratify=df["attack_type"], random_state=42)
    val_df, test_df = train_test_split(temp, test_size=0.5,
                                       stratify=temp["attack_type"], random_state=42)
    return train_df, val_df, test_df


class LivenessDataset(Dataset):
    """Датасет PyTorch для задачи выявления живости."""

    def __init__(self, df: pd.DataFrame, augment: bool = False):
        self.df = df.reset_index(drop=True)
        self.aug = DataAugmentor(enabled=augment)

    def __len__(self) -> int:
        return len(self.df)

    def __getitem__(self, idx: int):
        row = self.df.iloc[idx]
        image = preprocess_image(row["image_path"])
        if image is None:
            image = __import__("numpy").zeros((112, 112, 3), dtype="float32")
        image = self.aug.apply_augmentation(image)
        tensor = torch.from_numpy(image).permute(2, 0, 1).float()
        return tensor, torch.tensor(row["label"], dtype=torch.float32)


def create_dataloaders(train_df, val_df, test_df, batch_size: int = 64):
    """Создание DataLoader для всех выборок."""
    return (
        DataLoader(LivenessDataset(train_df, True), batch_size=batch_size,
                   shuffle=True, num_workers=4),
        DataLoader(LivenessDataset(val_df, False), batch_size=batch_size,
                   shuffle=False, num_workers=4),
        DataLoader(LivenessDataset(test_df, False), batch_size=batch_size,
                   shuffle=False, num_workers=4),
    )
