"""Инференс модели liveness через ONNX Runtime.
Файл: cv_service/liveness/liveness_detector.py"""
import logging
import numpy as np
import onnxruntime as ort

logger = logging.getLogger(__name__)
_MEAN = np.array([0.485, 0.456, 0.406], dtype=np.float32)
_STD = np.array([0.229, 0.224, 0.225], dtype=np.float32)


class LivenessDetector:
    """Детектор живости. Метод check_liveness возвращает float (§3.4)."""

    def __init__(self, model_path: str, ctx_id: int = 0):
        providers = (["CUDAExecutionProvider"] if ctx_id >= 0
                     else ["CPUExecutionProvider"])
        self._session = ort.InferenceSession(model_path, providers=providers)
        self._input_name = self._session.get_inputs()[0].name

    def _preprocess(self, aligned_face: np.ndarray) -> np.ndarray:
        """Предобработка лица 112x112 (HWC, RGB) -> (1,3,112,112)."""
        img = aligned_face.astype(np.float32)
        if img.max() > 1.0:
            img = img / 255.0
        img = (img - _MEAN) / _STD
        return np.expand_dims(np.transpose(img, (2, 0, 1)), axis=0)

    def check_liveness(self, aligned_face: np.ndarray) -> float:
        """Вероятность живости [0.0, 1.0]; при ошибке — 0.0 (атака)."""
        try:
            tensor = self._preprocess(aligned_face)
            output = self._session.run(None, {self._input_name: tensor})
            score = float(np.asarray(output[0]).flatten()[0])
            return max(0.0, min(1.0, score))
        except Exception as exc:
            logger.error("Ошибка инференса liveness: %s", exc)
            return 0.0
