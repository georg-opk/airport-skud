"""Конфигурация CV-сервиса. Файл: cv_service/config.py"""
import os
from pathlib import Path

# Автопоиск модели w600k_r50 внутри пакета buffalo_l
_INSIGHTFACE_DIR = Path.home() / ".insightface" / "models" / "buffalo_l"
_ARCFACE_AUTO = str(_INSIGHTFACE_DIR / "w600k_r50.onnx") \
    if (_INSIGHTFACE_DIR / "w600k_r50.onnx").exists() \
    else "w600k_r50"


class Config:
    """Пороги, пути к моделям и настройки Milvus."""
    DETECTION_CONFIDENCE = 0.5     # порог уверенности детектора
    SIMILARITY_THRESHOLD = 0.6     # порог косинусной близости
    LIVENESS_THRESHOLD = 0.5       # порог вероятности живости
    ARCFACE_MODEL = os.getenv("ARCFACE_MODEL", _ARCFACE_AUTO)
    LIVENESS_MODEL = os.getenv("LIVENESS_MODEL", "cv_service/models/liveness.onnx")
    CTX_ID = int(os.getenv("CTX_ID", "-1"))   # -1 = CPU
    MILVUS_HOST = os.getenv("MILVUS_HOST", "localhost")
    MILVUS_PORT = os.getenv("MILVUS_PORT", "19530")
    MILVUS_COLLECTION = "face_embeddings"
    EMBEDDING_DIM = 512
    TOP_K = 1