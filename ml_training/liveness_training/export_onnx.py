"""Экспорт модели liveness в ONNX.
Файл: ml_training/liveness_training/export_onnx.py"""
import logging
import torch
import onnx

logger = logging.getLogger(__name__)


def export_to_onnx(model, input_shape=(1, 3, 112, 112),
                   output_path: str = "models/liveness.onnx") -> str:
    """Экспорт PyTorch -> ONNX с проверкой корректности."""
    model.eval()
    dummy = torch.randn(*input_shape)
    torch.onnx.export(model, dummy, output_path,
                      input_names=["input"], output_names=["liveness"],
                      dynamic_axes={"input": {0: "batch"},
                                    "liveness": {0: "batch"}},
                      opset_version=13)
    onnx.checker.check_model(onnx.load(output_path))
    logger.info("Экспорт в ONNX: %s", output_path)
    return output_path
