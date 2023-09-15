import logging

from ..head_classifier import *
from .text_config import TextClassifierConfig
from ..base_trainer import BaseClassifierModule

logger = logging.getLogger(__name__)


class TextClassifierModule(BaseClassifierModule):
    """
    Text Classifier for training and inference.

    Args:
        train_config (TextClassifierConfig): TextClassifierConfig.
    """

    def __init__(self, train_config: TextClassifierConfig):
        super().__init__(train_config)

        (
            self.backbone,
            self.tokenizer,
            self.initial_config,
            self.delete_input_key_list,
        ) = self.get_model()
        self.embedding_size = self.initial_config.hidden_size

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
        Get backbone, tokenizer, initial_config, delete_input_key_list
        """
        return self.get_text_model(
            self.train_config.backbone_name,
            self.train_config.freeze,
            self.train_config.lora,
            self.train_config.lora_r,
            self.train_config.lora_alpha,
            self.train_config.lora_target_modules,
            self.train_config.lora_dropout,
        )

    # model forward
    def forward(self, input_texts, eval=False):
        return self.text_forward(
            input_texts,
            self.backbone,
            self.initial_config,
            self.train_config.freeze,
            eval=eval,
        )

    # Optimizer setup
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
