"""Конфигурация CV-сервиса. Файл: cv_service/config.py"""
import os


class Config:
    """Пороги, пути к моделям и настройки Milvus."""
    DETECTION_CONFIDENCE = 0.5  # порог уверенности детектора
    SIMILARITY_THRESHOLD = 0.6  # порог косинусной близости
    LIVENESS_THRESHOLD = 0.5  # порог вероятности живости
    ARCFACE_MODEL = os.getenv("ARCFACE_MODEL", "models/arcface_r100.onnx")
    LIVENESS_MODEL = os.getenv("LIVENESS_MODEL", "models/liveness.onnx")
    CTX_ID = int(os.getenv("CTX_ID", "0"))  # 0 — GPU, -1 — CPU
    MILVUS_HOST = os.getenv("MILVUS_HOST", "localhost")
    MILVUS_PORT = os.getenv("MILVUS_PORT", "19530")
    MILVUS_COLLECTION = "face_embeddings"
    EMBEDDING_DIM = 512
    TOP_K = 1
