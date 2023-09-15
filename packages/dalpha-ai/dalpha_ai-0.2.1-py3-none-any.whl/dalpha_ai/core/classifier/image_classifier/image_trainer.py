import logging
import torch

from ..head_classifier import *
from .image_config import ImageClassifierConfig
from ..base_trainer import BaseClassifierModule

logger = logging.getLogger(__name__)


class ImageClassifierModule(BaseClassifierModule):
    """
    Image Classifier for training and inference.

    Args:
        train_config (ImageClassifierConfig): ImageClassifierConfig.
    """

    def __init__(self, train_config: ImageClassifierConfig):
        super().__init__(train_config)

        (
            self.backbone,
            self.train_transforms,
            self.val_transforms,
            self.initial_config,
            self.train_config.timm,
        ) = self.get_model()
        self.embedding_size = self.backbone.forward(
            torch.randn(self.initial_config["input_size"]).unsqueeze(0)
        ).shape[-1]

        # Define classifier
        if type(self.train_config.fc_classifier) == str:
            classifier_class = globals()[self.train_config.fc_classifier]
            self.classifier_head = classifier_class(
                self.embedding_size, self.train_config.num_class
            )
        else:
            self.classifier_head = self.train_config.fc_classifier(
                self.embedding_size, self.train_config.num_class
            )

        self.save_hyperparameters()

    def get_model(self):
        """
        Get model, train transforms, val transforms, initial config, and timm flag.
        """
        return self.get_image_model(
            self.train_config.backbone_name,
            self.train_config.freeze,
            self.train_config.lora,
            self.train_config.lora_r,
            self.train_config.lora_alpha,
            self.train_config.lora_target_modules,
            self.train_config.lora_dropout,
        )

    # model forward
    def forward(self, input_img_paths, eval=False):
        return self.image_forward(
            input_img_paths, self.backbone, self.train_config.freeze, eval=eval
        )

    def configure_optimizers(self):
        optimizer = self.classifier_head_optimizers()
        optimizer = self.add_optimizers(
            optimizer,
            self.backbone,
            self.train_config.backbone_learning_rate,
            self.train_config.freeze,
            self.train_config.lora,
        )

        lr_scheduler = self.get_lr_scheduler(optimizer)

        return [optimizer], [{"scheduler": lr_scheduler}]
