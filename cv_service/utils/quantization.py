"""Квантизация ONNX-моделей. Файл: cv_service/utils/quantization.py"""
import logging
import onnx
from onnxconverter_common import float16
from onnxruntime.quantization import quantize_dynamic, QuantType

logger = logging.getLogger(__name__)


def quantize_model(onnx_path: str, output_path: str,
                   quant_type: str = "FP16") -> str:
    """Квантизация модели в FP16 или INT8."""
    if quant_type == "FP16":
        model = onnx.load(onnx_path)
        onnx.save(float16.convert_float_to_float16(model), output_path)
    elif quant_type == "INT8":
        quantize_dynamic(onnx_path, output_path, weight_type=QuantType.QInt8)
    else:
        raise ValueError(f"Неизвестный тип: {quant_type}")
    logger.info("Квантизация %s: %s", quant_type, output_path)
    return output_path
