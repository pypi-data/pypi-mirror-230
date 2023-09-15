import onnxruntime
import torch
from shengtengconverter.utils.check import check_pytorch_model


def get_onnxruntime_provider():
    """
    obtain all providers supported by onnxruntime, which can be used for parameters of get_onnx_input() and get_onnx_output()

    Returns:
        list: onnxruntime all supported providers
    """
    return onnxruntime.get_available_providers()


def get_onnx_input(onnx_model_path, provider="CPUExecutionProvider"):
    """
    obtain input information for the onnx model

    Parameters:
        - onnx_model_path(str): path of onnx model
        - provider(str): provider supported by onnxruntime can be obtained through get_onnxruntime_provider(). Default to CPUExecutionProvider

    Returns:
        list: input information of the onnx model, where each element is a dictionary with key values of name, type, shape
    """
    onnx_session = onnxruntime.InferenceSession(
        onnx_model_path, providers=[provider])
    input_tensors = onnx_session.get_inputs()
    input_info = []
    for input_tensor in input_tensors:  # It's a list Because there may be multiple inputs
        input_info.append({
            "name": input_tensor.name,
            "type": input_tensor.type,
            "shape": input_tensor.shape,
        })
    return input_info


def get_onnx_output(onnx_model_path, provider="CPUExecutionProvider"):
    """
    obtain output information for the onnx model

    Parameters:
        - onnx_model_path(str): path of onnx model
        - provider(str): provider supported by onnxruntime can be obtained through get_onnxruntime_provider(). Default to CPUExecutionProvider

    Returns:
        list: output information of the onnx model, where each element is a dictionary with key values of name, type, shape
    """
    onnx_session = onnxruntime.InferenceSession(
        onnx_model_path, providers=[provider])
    output_tensors = onnx_session.get_outputs()
    output_info = []
    for output_tensor in output_tensors:  # It's a list Because there may be multiple outputs
        output_info.append({
            "name": output_tensor.name,
            "type": output_tensor.type,
            "shape": output_tensor.shape,
        })
    return output_info


def get_pytorch_state_dict(pytorch_model_path):
    """
    obtain state_dict for the pytorch model

    Parameters:
        - pytorch_model_path(str): path of pytorch model

    Returns:
        list: state_dict information of the pytorch model, where each element is a dictionary with key values of name, type, shape
    """
    state_dict_info = []
    is_valid = check_pytorch_model(pytorch_model_path)
    if is_valid:
        model = torch.load(pytorch_model_path)
        state_dict = model.state_dict()
    else:
        state_dict = torch.load(pytorch_model_path)
    for i in state_dict.keys():
        state_dict_info.append({
            "name": i,
            "type": state_dict[i].type(),
            "shape": state_dict[i].shape,
        })
    return state_dict_info
