import torch


def check_pytorch_model(pytorch_model_path):
    """
    This function is used to check whether the pytorch model has saved the topology and parameters or only the parameters.

    Parameters:
        - pytorch_model_path(str): The path of pytorch model.

    Returns:
        bool: if the topology is saved, return True, else return False.
    """
    try:
        model = torch.load(pytorch_model_path)
        if isinstance(model, torch.nn.Module):
            return True
        elif isinstance(model, dict):
            return False
        else:
            raise RuntimeError(
                "The pytorch model is invalid. Its type is {}".format(type(model)))
    except Exception as e:
        raise RuntimeError("The pytorch model {} cannot be loaded. Error: {}".format(
            pytorch_model_path, e))
