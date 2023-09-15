import torch
import os
from ..classifier import *
from typing import Union, List
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)

from .util import postprocess


class PytorchClassificationPipeline:
    """
    Pytorch Classification Pipeline

    Args:
        model_type (str): Model type, support TextClassifier, ImageClassifier, ImageTextClassifier.
        save_dir (str): Model directory.
        device (str, optional): Device for inference, support cpu and gpu. Defaults to "gpu".
    """

    def __init__(
        self,
        model_type: str,
        save_dir: str,
        device: str = "gpu",
        quantization: bool = False,
        optimization: bool = False,
    ):
        # Device setting
        if device == "cpu":
            self.device = torch.device("cpu")
            self.autocast_device = "cpu"
        elif device == "gpu":
            self.device = torch.device("cuda")
            self.autocast_device = "cuda"
        else:
            raise ValueError(
                f"Not supported device type: {device}, choose in ['cpu', 'gpu']."
            )

        # Use pytorch lightning module for inferene pipeline.
        if model_type.endswith("Module"):
            train_module_name = model_type
        else:
            train_module_name = model_type + "Module"
        # Call model class with model type string
        if train_module_name not in globals().keys():
            raise ValueError(f"Not supported model type: {model_type}")

        # Load pretrained model
        model_class = globals()[train_module_name]
        ckpt_path = os.path.join(save_dir, "model.ckpt")
        self.pretrained_model = model_class.load_from_checkpoint(ckpt_path)
        self.pretrained_model.eval()
        self.pretrained_model.to(self.device)

    def __call__(
        self,
        inputs: Union[str, List[str]],
        topk: int = 1,
        return_logits: bool = False,
        sigmoid: bool = False,
    ):
        """
        Args:
            inputs (Union[str, List[str]]): Input text or list of input texts.
            topk (int, optional): Top k prediction. Defaults to 1.
            return_logits (bool, optional): Return logits or not. Defaults to False.
            sigmoid (bool, optional): Apply sigmoid to logits or not. Defaults to False.
        """
        if type(inputs) == str:
            inputs = [inputs]

        # In case when model is trained with multiple inputs, pipeline receives list of inputs. (e.g. ImageTextClassification)
        if type(inputs[0]) == list:
            with torch.autocast(self.autocast_device):
                logits = self.pretrained_model.forward(*inputs, eval=True)
        else:
            with torch.autocast(self.autocast_device):
                logits = self.pretrained_model.forward(inputs, eval=True)

        return postprocess(
            logits,
            topk,
            self.pretrained_model.train_config.label_name_list,
            return_logits,
            sigmoid,
        )
