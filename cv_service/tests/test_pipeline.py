"""Модульные и интеграционные тесты.
Файлы: cv_service/tests/test_pipeline.py, backend/tests/test_api.py"""
import logging
import numpy as np
import cv2
from fastapi.testclient import TestClient

from detection.face_detector import FaceDetector
from recognition.face_recognizer import FaceRecognizer
from liveness.liveness_detector import LivenessDetector
from config import Config
from app.main import app

logging.basicConfig(level=logging.INFO)
client = TestClient(app)


def test_detector_finds_face():
    """Детектор обнаруживает лицо на тестовом изображении."""
    detector = FaceDetector(ctx_id=-1)
    frame = cv2.imread("tests/data/sample_face.jpg")
    assert len(detector.detect(frame)) >= 1


def test_embedding_dim_and_norm():
    """Эмбеддинг имеет размерность 512 и единичную L2-норму."""
    recognizer = FaceRecognizer(Config.ARCFACE_MODEL, ctx_id=-1)
    face = np.random.rand(112, 112, 3).astype(np.float32)
    emb = recognizer.get_embedding(face)
    assert emb.shape[0] == 512
    assert abs(np.linalg.norm(emb) - 1.0) < 1e-3


def test_liveness_returns_float_in_range():
    """check_liveness возвращает float в диапазоне [0, 1]."""
    detector = LivenessDetector(Config.LIVENESS_MODEL, ctx_id=-1)
    face = np.random.rand(112, 112, 3).astype(np.float32)
    score = detector.check_liveness(face)
    assert isinstance(score, float) and 0.0 <= score <= 1.0


def test_login_returns_token():
    """POST /auth/login возвращает JWT-токен."""
    resp = client.post("/api/v1/auth/login",
                       params={"username": "operator", "password": "pass"})
    assert resp.status_code == 200 and "access_token" in resp.json()


def test_cv_status_ok():
    """GET /cv/status возвращает статус сервиса."""
    resp = client.get("/api/v1/cv/status")
    assert resp.status_code == 200 and resp.json()["status"] == "ok"
