import onnx
from shengtengconverter.onnx2pytorch import ConvertModel
import torch
from shengtengconverter.utils import *
import tf2onnx
import tensorflow as tf
from onnx_tf.backend import prepare


def convert_onnx_to_pytorch(onnx_model_path, experimental=False, pytorch_model_path=None):
    """
    This function is used to convert onnx model to pytorch model.

    Parameters:
        - onnx_model_path (str): The path of onnx model.
        - experimental (bool): Whether to use experimental mode. When experimental is True, batch_size > 1 is allowed.
        - pytorch_model_path (str): The path of pytorch model.

    Returns:
        str: The path of pytorch model.
    """
    onnx_model = onnx.load(onnx_model_path)
    pytorch_model = ConvertModel(onnx_model, experimental=experimental)
    if pytorch_model_path is None:
        pytorch_model_path = onnx_model_path.replace(".onnx", ".pth")
    torch.save(pytorch_model, pytorch_model_path)
    print("Convert {} to {} done.".format(onnx_model_path, pytorch_model_path))
    return pytorch_model_path


def convert_onnx_to_pytorch_batch(onnx_model_path, pytorch_model_path=None):
    """
    This function is used to convert onnx model to pytorch model in batch.

    Parameters:
        - onnx_model_path(str): The path of onnx model.
        - pytorch_model_path(str): The path of pytorch model.

    Returns:
        str: The path of pytorch model.
    """
    return convert_onnx_to_pytorch(onnx_model_path, experimental=True, pytorch_model_path=pytorch_model_path)


def convert_onnx_to_pytorch_all(path):
    """
    This function is used to convert onnx model to pytorch model in the path.

    Parameters:
        - path(str): The directory path may contain onnx model.

    Returns:
        None
    """
    onnx_model = list_onnx_models(path)
    for i in onnx_model:
        convert_onnx_to_pytorch_batch(i)


def convert_pytorch_to_onnx(pytorch_model_path, input_shape, onnx_model_path=None):
    """
    This function is used to convert pytorch model to onnx model.

    Parameters:
        - pytorch_model_path(str): The path of pytorch model.
        - input_shape(tuple): The input shape of pytorch model.
        - onnx_model_path(str): The path of onnx model.

    Returns:
        str: The path of onnx model.
    """
    pytorch_model = torch.load(pytorch_model_path)
    if onnx_model_path is None:
        onnx_model_path = pytorch_model_path.replace(".pth", ".onnx")
    is_valid = check_pytorch_model(pytorch_model_path)
    if is_valid:
        torch.onnx.export(pytorch_model, torch.randn(
            *input_shape), onnx_model_path)
        print("Convert {} to {} done.".format(
            pytorch_model_path, onnx_model_path))
        return onnx_model_path
    else:
        raise RuntimeError(
            "The pytorch model only contains parameters. Please provide the topology of the model.")


def convert_tensorflow_to_onnx(tensorflow_model_path, onnx_model_path=None, input_names=None, output_names=None):
    """
    This function is used to convert tensorflow model to onnx model.

    Parameters:
        - tensorflow_model_path(str): The path of tensorflow model.
        - onnx_model_path(str): The path of onnx model.

    Returns:
        str: The path of onnx model.
    """
    if output_names is None:
        output_names = ['output:0']
    if input_names is None:
        input_names = ['input:0']
    if onnx_model_path is None:
        onnx_model_path = tensorflow_model_path.replace(".pb", ".onnx")
    graph_def = tf.compat.v1.GraphDef()
    with tf.io.gfile.GFile(tensorflow_model_path, 'rb') as f:
        graph_def.ParseFromString(f.read())
    with tf.compat.v1.Session() as sess:
        tf.import_graph_def(graph_def, name='')
        g = sess.graph
        onnx_model = tf2onnx.convert.from_session(
            sess, input_names=input_names, output_names=output_names)
        with open(onnx_model_path, 'wb') as f:
            f.write(onnx_model.SerializeToString())
        print("Convert {} to {} done.".format(
            tensorflow_model_path, onnx_model_path))
        return onnx_model_path


def convert_onnx_to_tensorflow_savedmodel(onnx_model_path, tensorflow_model_path=None):
    """
    This function is used to convert onnx model to tensorflow model.

    Parameters:
        - onnx_model_path(str): The path of onnx model.
        - tensorflow_model_path(str): The path of tensorflow model.

    Returns:
        str: The path of tensorflow model.
    """
    if tensorflow_model_path is None:
        tensorflow_model_path = onnx_model_path.replace(".onnx", ".pb")
    onnx_model = onnx.load(onnx_model_path)
    tf_model = prepare(onnx_model)
    tf_model.export_graph(tensorflow_model_path)
    print("Convert {} to {} done.".format(
        onnx_model_path, tensorflow_model_path))
    return tensorflow_model_path
