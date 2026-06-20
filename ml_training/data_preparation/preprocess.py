"""Предобработка: детекция, выравнивание 112x112, нормализация.
Файл: ml_training/data_preparation/preprocess.py"""
import os
import logging
import cv2
import numpy as np
from insightface.app import FaceAnalysis
from insightface.utils import face_align

logger = logging.getLogger(__name__)
IMAGENET_MEAN = np.array([0.485, 0.456, 0.406], dtype=np.float32)
IMAGENET_STD = np.array([0.229, 0.224, 0.225], dtype=np.float32)
FACE_SIZE = 112

_face_app = FaceAnalysis(allowed_modules=["detection"])
_face_app.prepare(ctx_id=0, det_size=(640, 640))


def preprocess_image(image_path: str):
    """Детекция, выравнивание и нормализация одного изображения."""
    img = cv2.imread(image_path)
    if img is None:
        logger.warning("Не удалось прочитать: %s", image_path)
        return None
    faces = _face_app.get(img)
    if not faces:
        return None
    face = max(faces, key=lambda f: (f.bbox[2] - f.bbox[0]) *
               (f.bbox[3] - f.bbox[1]))
    aligned = face_align.norm_crop(img, landmark=face.kps, image_size=FACE_SIZE)
    aligned = cv2.cvtColor(aligned, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0
    return (aligned - IMAGENET_MEAN) / IMAGENET_STD


def preprocess_dataset(input_dir: str, output_dir: str) -> int:
    """Пакетная предобработка с сохранением в .npy."""
    os.makedirs(output_dir, exist_ok=True)
    count = 0
    for root, _, files in os.walk(input_dir):
        for name in files:
            if not name.lower().endswith((".jpg", ".jpeg", ".png")):
                continue
            arr = preprocess_image(os.path.join(root, name))
            if arr is None:
                continue
            np.save(os.path.join(output_dir,
                    os.path.splitext(name)[0] + ".npy"), arr)
            count += 1
    logger.info("Предобработано: %d", count)
    return count
