import torch
from ..head_classifier import *

from .image_text_config import ImageTextClassifierConfig
from ..base_trainer import BaseClassifierModule


class ImageTextClassifierModule(BaseClassifierModule):
    """
    Image Text Classifier Module.

    Args:
        train_config (ImageTextClassifierConfig): ImageTextClassifierConfig.
    """

    def __init__(self, train_config: ImageTextClassifierConfig):
        super().__init__(train_config)

        (
            self.image_backbone,
            self.train_transforms,
            self.val_transforms,
            self.image_initial_config,
            self.train_config.image_timm,
            self.text_backbone,
            self.tokenizer,
            self.text_initial_config,
            self.delete_input_key_list,
        ) = self.get_model()
        # Concat embedding
        self.image_embedding_size = self.image_backbone.forward(
            torch.randn(self.image_initial_config["input_size"]).unsqueeze(0)
        ).shape[-1]
        self.text_embedding_size = self.text_initial_config.hidden_size
        self.embedding_size = self.image_embedding_size + self.text_embedding_size

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
        Get model from config.
        Return image_backbone, train_transforms, val_transforms, image_initial_config, image_timm, text_backbone, tokenizer, text_initial_config, delete_input_key_list
        """
        # Get Text Models
        get_text_model_result = self.get_text_model(
            self.train_config.text_backbone_name,
            self.train_config.text_freeze,
            self.train_config.text_lora,
            self.train_config.text_lora_r,
            self.train_config.text_lora_alpha,
            self.train_config.text_lora_target_modules,
            self.train_config.text_lora_dropout,
        )
        get_image_model_result = self.get_image_model(
            self.train_config.image_backbone_name,
            self.train_config.image_freeze,
            self.train_config.image_lora,
            self.train_config.image_lora_r,
            self.train_config.image_lora_alpha,
            self.train_config.image_lora_target_modules,
            self.train_config.image_lora_dropout,
        )

        return get_image_model_result + get_text_model_result

    # model forward
    def forward(self, input_img_paths, input_texts, eval=False):
        image_backbone_outputs = self.image_forward(
            input_img_paths,
            self.image_backbone,
            self.train_config.image_freeze,
            eval=eval,
            classifier=False,
        )
        text_backbone_outputs = self.text_forward(
            input_texts,
            self.text_backbone,
            self.text_initial_config,
            self.train_config.text_freeze,
            eval=eval,
            classifier=False,
        )

        backbone_outputs = torch.cat(
            [image_backbone_outputs, text_backbone_outputs], dim=1
        )
        logits = self.classifier_head(backbone_outputs)

        return logits

    def configure_optimizers(self):
        optimizer = self.classifier_head_optimizers()
        optimizer = self.add_optimizers(
            optimizer,
            self.text_backbone,
            self.train_config.text_backbone_learning_rate,
            self.train_config.text_freeze,
            self.train_config.text_lora,
        )
        optimizer = self.add_optimizers(
            optimizer,
            self.image_backbone,
            self.train_config.image_backbone_learning_rate,
            self.train_config.image_freeze,
            self.train_config.image_lora,
        )

        lr_scheduler = self.get_lr_scheduler(optimizer)

        return [optimizer], [{"scheduler": lr_scheduler}]
