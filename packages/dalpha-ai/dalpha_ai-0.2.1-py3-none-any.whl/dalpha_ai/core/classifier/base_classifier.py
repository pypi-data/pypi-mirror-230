import os

os.environ["TOKENIZERS_PARALLELISM"] = "false"
import copy
import torch

torch.backends.cudnn.benchmark = False
import logging
from typing import List, Union

import pandas as pd
import pytorch_lightning as pl
from pytorch_lightning.callbacks import ModelCheckpoint

from .trainer_util import set_seed

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)


def check_dataset(dataset: Union[pd.DataFrame, List[List]], column_list: List[str]):
    """
    Check if the dataset is in the correct format
    Args:
        dataset (pd.DataFrame or list): dataset
        column_list (list): list of column names (must be in order of text, label)
    Returns:
        output dataset
    """

    if type(dataset) == pd.DataFrame:
        if len(dataset.columns) != len(column_list):
            raise ValueError(
                f"For DataFrame input, dataset must have {len(column_list)} columns. Got {len(dataset.columns)} columns"
            )
        for idx, col in enumerate(column_list):
            if dataset.columns[idx] != col:
                logger.warning(
                    f"Column {idx} is {dataset.columns[idx]}, but expected {col}"
                )
            dataset.rename(columns={dataset.columns[idx]: col}, inplace=True)
    elif type(dataset) == list:
        if len(dataset[0]) != len(column_list):
            raise ValueError(
                f"For list input, dataset must have {len(column_list)} columns. Got {len(dataset[0])} columns"
            )
        else:
            logger.warning(
                f"For list input, column names will be set to default: {column_list}"
            )
    else:
        raise ValueError(
            f"Dataset must be either pd.DataFrame or list. Got {type(dataset)}"
        )

    if dataset["label"].dtype != "int64":
        raise ValueError(
            f"Label column must be int64 dtype. Got {dataset['label'].dtype}"
        )

    return dataset


class BaseClassifier:
    """
    Base class for all classifiers, including text, image, and image-text classifiers
    Args:
        train_dataset (pd.DataFrame or list): training dataset
        val_dataset (pd.DataFrame or list): validation dataset
        test_dataset (pd.DataFrame or list): test dataset (optional)
        label_name_list (list): list of label names (optional)
        train_config (ClassifierConfig): training config (optional)
    """

    def __init__(
        self,
        train_dataset: Union[pd.DataFrame, List[List]],
        val_dataset: Union[pd.DataFrame, List[List]],
        test_dataset: Union[pd.DataFrame, List[List]] = None,
        label_name_list: List = None,
        train_config=None,
    ):
        from .text_classifier import TextClassifierConfig
        from .image_classifier import ImageClassifierConfig
        from .image_text_classifier import ImageTextClassifierConfig

        self.train_config = train_config
        # Set random seed
        set_seed(self.train_config.seed)

        train_dataset = copy.deepcopy(train_dataset)
        val_dataset = copy.deepcopy(val_dataset)
        test_dataset = copy.deepcopy(test_dataset)
        if type(train_config) == TextClassifierConfig:
            train_dataset = check_dataset(train_dataset, ["text", "label"])
            val_dataset = check_dataset(val_dataset, ["text", "label"])
            if test_dataset is not None:
                test_dataset = check_dataset(test_dataset, ["text", "label"])
            else:
                logger.warning(
                    "test_dataset is None. Using val_dataset as test_dataset"
                )
                test_dataset = copy.deepcopy(val_dataset)

        elif type(train_config) == ImageClassifierConfig:
            train_dataset = check_dataset(train_dataset, ["img_path", "label"])
            val_dataset = check_dataset(val_dataset, ["img_path", "label"])
            if test_dataset is not None:
                test_dataset = check_dataset(test_dataset, ["img_path", "label"])
            else:
                logger.warning(
                    "test_dataset is None. Using val_dataset as test_dataset"
                )
                test_dataset = copy.deepcopy(val_dataset)

        elif type(train_config) == ImageTextClassifierConfig:
            train_dataset = check_dataset(train_dataset, ["img_path", "text", "label"])
            val_dataset = check_dataset(val_dataset, ["img_path", "text", "label"])
            if test_dataset is not None:
                test_dataset = check_dataset(
                    test_dataset, ["img_path", "text", "label"]
                )
            else:
                logger.warning(
                    "test_dataset is None. Using val_dataset as test_dataset"
                )
                test_dataset = copy.deepcopy(val_dataset)
        else:
            raise ValueError(f"Not supported train_config type: {type(train_config)}")

        self.train_dataset = train_dataset
        self.val_dataset = val_dataset
        self.test_dataset = test_dataset

        # Check number of class when training config num class value is default value.
        if self.train_config.num_class == 0:
            if label_name_list is not None:
                logger.info("Get number of class with the length of label name list.")
                self.train_config.num_class = len(label_name_list)
                self.train_config.label_name_list = label_name_list
            else:
                label_list = (
                    list(map(lambda x: int(x), train_dataset["label"]))
                    + list(map(lambda x: int(x), val_dataset["label"]))
                    + list(map(lambda x: int(x), test_dataset["label"]))
                )
                self.train_config.num_class = max(label_list) + 1
                logger.warning(
                    f"Since training config does not get the number of class, trainer estimate the number of class with input dataset, estimated number of class is {self.train_config.num_class} "
                )

        else:
            if label_name_list is not None:
                if self.train_config.num_class != len(label_name_list):
                    raise ValueError(
                        f"Number of class in training config {self.train_config.num_class} does not match with length of label_name_list {len(label_name_list)}."
                    )
                self.train_config.label_name_list = label_name_list

        self.trainer = None

    def base_train(self):
        """
        Base training function
        """
        if self.train_config.monitor_topk == "total":
            monitor_acc = "val/tot_acc"
            checkpoint_callback = ModelCheckpoint(
                monitor=monitor_acc,
                mode="max",
                save_top_k=self.train_config.save_ckpt_topk,
                filename="epoch{epoch:02d}-val_totacc={val/tot_acc:.2f}",
                auto_insert_metric_name=False,
            )
        else:
            monitor_acc = f"val/acc{self.train_config.monitor_topk}"
            self.monitor_topk = 1
            checkpoint_callback = ModelCheckpoint(
                monitor=monitor_acc,
                mode="max",
                save_top_k=self.train_config.save_ckpt_topk,
                filename="epoch{epoch:02d}-val_acc={val/monitor_acc:.2f}",
                auto_insert_metric_name=False,
            )

        # Define trainer
        self.trainer = pl.Trainer(
            accelerator=self.train_config.device,
            devices=self.train_config.use_device_list,
            precision=self.train_config.precision,
            max_epochs=self.train_config.max_epochs,
            callbacks=[checkpoint_callback],
            num_sanity_val_steps=self.train_config.num_sanity_val_steps,
            check_val_every_n_epoch=self.train_config.check_val_every_n_epoch,
            default_root_dir=self.train_config.output_dir,
        )

        self.trainer.fit(self.train_module, self.data_module)

        print(
            "Best ckpt saved path: ", self.trainer.checkpoint_callback.best_model_path
        )

    # Test the best trained model with test dataset
    def test(self):
        """
        Test the best trained model with test dataset, if test dataset is None, test with val dataset.
        """
        if self.trainer is None:
            raise ValueError(
                "You should train the trainer before inference. E.g. TextClassifier().train()"
            )
        self.trainer.test(ckpt_path="best", dataloaders=self.data_module)
