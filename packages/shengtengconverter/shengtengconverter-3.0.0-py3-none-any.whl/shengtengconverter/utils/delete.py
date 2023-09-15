import os
from shengtengconverter.utils.view import *


def delete_file(path):
    """
    This function is used to delete file.

    Parameters:
        - path(str): The file path.

    Returns:
        None.
    """
    if os.path.exists(path):
        os.remove(path)
        print("Delete {} done.".format(path))
    else:
        print("The file does not exist")


def delete_onnx_models(path):
    """
    This function is used to delete all onnx model in the path.

    Parameters:
        - path(str): The directory path may contain onnx model.

    Returns:
        None.
    """
    onnx_models = list_onnx_models(path)
    for onnx_model in onnx_models:
        delete_file(onnx_model)


def delete_pytorch_models(path):
    """
    This function is used to delete all pytorch model in the path.

    Parameters:
        - path(str): The directory path may contain pytorch model.

    Returns:
        None.
    """
    pytorch_models = list_pytorch_models(path)
    for pytorch_model in pytorch_models:
        delete_file(pytorch_model)


def delete_tensorflow_models(path):
    """
    This function is used to delete all tensorflow model in the path.

    Parameters:
        - path(str): The directory path may contain tensorflow model.

    Returns:
        None.
    """
    tensorflow_models = list_tensorflow_models(path)
    for tensorflow_model in tensorflow_models:
        delete_file(tensorflow_model)
