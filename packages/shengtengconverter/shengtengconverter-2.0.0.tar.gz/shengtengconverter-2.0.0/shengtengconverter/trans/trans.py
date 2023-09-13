import onnx
from shengtengconverter.onnx2pytorch import ConvertModel
import torch
from shengtengconverter.utils import list_onnx_models


def convert_onnx_to_pytorch(onnx_model_path, experimental=False, pytorch_path=None):
    """
    This function is used to convert onnx model to pytorch model.

    Parameters:
        onnx_model_path(str): The path of onnx model.
        experimental(bool): Whether to use experimental mode. When experimental is True, batch_size > 1 is allowed.
        pytorch_path(str): The path of pytorch model.

    Returns:
        str: The path of pytorch model.
    """
    onnx_model = onnx.load(onnx_model_path)
    pytorch_model = ConvertModel(onnx_model, experimental=experimental)
    if pytorch_path is None:
        pytorch_path = onnx_model_path.replace(".onnx", ".pth")
    torch.save(pytorch_model, pytorch_path)
    print("Convert {} to {} done.".format(onnx_model_path, pytorch_path))
    return pytorch_path


def convert_onnx_to_pytorch_batch(onnx_model_path, pytorch_path=None):
    """
    This function is used to convert onnx model to pytorch model in batch.

    Parameters:
        onnx_model_path(str): The path of onnx model.
        pytorch_path(str): The path of pytorch model.

    Returns:
        str: The path of pytorch model.
    """
    return convert_onnx_to_pytorch(onnx_model_path, experimental=True, pytorch_path=pytorch_path)


def main(path):
    """
    This function is used to convert onnx model to pytorch model in the path.

    Parameters:
        path(str): The directory path may contain onnx model.

    Returns:
        None
    """
    onnx_model = list_onnx_models(path)
    for i in onnx_model:
        convert_onnx_to_pytorch_batch(i)
