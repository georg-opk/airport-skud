"""Экспорт моделей в ONNX. Файл: cv_service/utils/onnx_exporter.py"""
import logging
import torch
import onnx

logger = logging.getLogger(__name__)


def export_model_to_onnx(model, input_shape=(1, 3, 112, 112),
                         output_path: str = "models/model.onnx") -> str:
    """Экспорт PyTorch-модели в ONNX с проверкой."""
    model.eval()
    dummy = torch.randn(*input_shape)
    torch.onnx.export(model, dummy, output_path,
                      input_names=["input"], output_names=["output"],
                      dynamic_axes={"input": {0: "batch"},
                                    "output": {0: "batch"}},
                      opset_version=13)
    onnx.checker.check_model(onnx.load(output_path))
    return output_path
