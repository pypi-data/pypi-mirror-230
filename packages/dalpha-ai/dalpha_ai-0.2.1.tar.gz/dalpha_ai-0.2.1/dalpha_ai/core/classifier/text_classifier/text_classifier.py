import os

os.environ["TOKENIZERS_PARALLELISM"] = "false"
import torch

torch.backends.cudnn.benchmark = False
import logging
from typing import List, Optional, Union

import pandas as pd

from ..trainer_util import set_seed
from .text_config import TextClassifierConfig
from .text_datamodule import TextClassifierDataModule
from .text_trainer import TextClassifierModule
from ..base_classifier import BaseClassifier

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)


class TextClassifier(BaseClassifier):
    """
    Text Classifier for training and inference.

    Args:
        train_dataset (Union[pd.DataFrame, List[List]]): Training dataset.
        val_dataset (Union[pd.DataFrame, List[List]]): Validation dataset.
        test_dataset (Union[pd.DataFrame, List[List]]): Test dataset.
        label_name_list (List): List of label names.
        train_config (TextClassifierConfig): TextClassifierConfig.
    """

    def __init__(
        self,
        train_dataset: Union[pd.DataFrame, List[List]],
        val_dataset: Union[pd.DataFrame, List[List]],
        test_dataset: Union[pd.DataFrame, List[List]] = None,
        label_name_list: List = None,
        train_config: TextClassifierConfig = None,
    ):
        # Initial starting without loading from checkpoint
        if train_config is None:
            output_dir = "tmp_classifier"
            logger.info(
                f"No `TextClassifierConfig` passed, using `output_dir={output_dir}`."
            )
            train_config = TextClassifierConfig(output_dir=output_dir)
        else:
            assert (
                type(train_config) == TextClassifierConfig
            ), f"train_config type has to be TextClassifierConfig, but got {type(train_config)}"

        super().__init__(
            train_dataset, val_dataset, test_dataset, label_name_list, train_config
        )
        # Define Data module
        self.data_module = TextClassifierDataModule(
            train_dataset=self.train_dataset,
            val_dataset=self.val_dataset,
            test_dataset=self.test_dataset,
            train_config=self.train_config,
        )

        # Define Train Module
        self.train_module = TextClassifierModule(train_config=self.train_config)

        self.trainer = None

    def train(self, resume_from_checkpoint: Optional[str] = None):
        """
        Train the model, if resume_from_checkpoint is passed, resume from checkpoint.
        """
        # Resume from checkpoint, local path to a saved checkpoint.
        if resume_from_checkpoint:
            self.train_module = TextClassifierModule.load_from_checkpoint(
                resume_from_checkpoint
            )
        # Define Trainer and Callbacks for training, and start training
        self.base_train()
