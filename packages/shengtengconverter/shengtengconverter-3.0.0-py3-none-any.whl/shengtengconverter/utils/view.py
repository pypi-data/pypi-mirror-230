import os


def list_onnx_models(path):
    """
    This function is used to list all onnx model in the path.

    Parameters:
        - path(str): The directory path may contain onnx model.

    Returns:
        str: The list of onnx model path.
    """
    onnx_model = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(".onnx"):
                onnx_model.append(os.path.join(root, file))
    return onnx_model


def list_pytorch_models(path):
    """
    This function is used to list all pytorch model in the path.

    Parameters:
        - path(str): The directory path may contain pytorch model.

    Returns:
        str: The list of pytorch model path.
    """
    pytorch_model = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(".pth"):
                pytorch_model.append(os.path.join(root, file))
    return pytorch_model


def list_tensorflow_models(path):
    """
    This function is used to list all tensorflow model in the path.

    Parameters:
        - path(str): The directory path may contain tensorflow model.

    Returns:
        str: The list of tensorflow model path.
    """
    tensorflow_model = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(".pb"):
                tensorflow_model.append(os.path.join(root, file))
    return tensorflow_model
