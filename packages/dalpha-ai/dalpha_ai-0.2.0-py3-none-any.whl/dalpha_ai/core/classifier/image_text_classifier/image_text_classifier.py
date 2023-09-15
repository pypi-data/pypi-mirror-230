import os

os.environ["TOKENIZERS_PARALLELISM"] = "false"
import copy
import json
import pickle
import torch
import shutil

torch.backends.cudnn.benchmark = False
import logging
import typing
from typing import List, Optional, Union

import numpy as np
import pandas as pd
import pytorch_lightning as pl
import timm
from pytorch_lightning.callbacks import ModelCheckpoint


from .image_text_config import ImageTextClassifierConfig
from .image_text_datamodule import ImageTextClassifierDataModule
from .image_text_trainer import ImageTextClassifierModule
from ..base_classifier import BaseClassifier

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)


class ImageTextClassifier(BaseClassifier):
    """
    Image Text Classifier.

    Args:
        train_dataset (Union[pd.DataFrame, List[List]]): Training dataset.
        val_dataset (Union[pd.DataFrame, List[List]]): Validation dataset.
        test_dataset (Union[pd.DataFrame, List[List]]): Test dataset, optional.
        label_name_list (List): List of label names, optional.
        train_config (ImageTextClassifierConfig): ImageTextClassifierConfig, optional.
    """

    def __init__(
        self,
        train_dataset: Union[pd.DataFrame, List[List]],
        val_dataset: Union[pd.DataFrame, List[List]],
        test_dataset: Union[pd.DataFrame, List[List]] = None,
        label_name_list: List = None,
        train_config: ImageTextClassifierConfig = None,
    ):
        # Initial starting without loading from checkpoint
        if train_config is None:
            output_dir = "tmp_classifier"
            logger.info(
                f"No `ImageTextClassifierConfig` passed, using `output_dir={output_dir}`."
            )
            train_config = ImageTextClassifierConfig(output_dir=output_dir)
        else:
            assert (
                type(train_config) == ImageTextClassifierConfig
            ), f"train_config should be ImageTextClassifierConfig, but got {type(train_config)}"

        super().__init__(
            train_dataset, val_dataset, test_dataset, label_name_list, train_config
        )

        # Define Data module
        self.data_module = ImageTextClassifierDataModule(
            train_dataset=self.train_dataset,
            val_dataset=self.val_dataset,
            test_dataset=self.test_dataset,
            train_config=self.train_config,
        )

        # Define Train Module
        self.train_module = ImageTextClassifierModule(train_config=self.train_config)

        self.trainer = None

    def train(self, resume_from_checkpoint: Optional[str] = None):
        """
        Train the model, resume from checkpoint if `resume_from_checkpoint` is provided.
        """
        # Resume from checkpoint, local path to a saved checkpoint.
        if resume_from_checkpoint:
            self.train_module = ImageTextClassifierModule.load_from_checkpoint(
                resume_from_checkpoint
            )
        # Define Trainer and Callbacks for training, and start training
        self.base_train()
