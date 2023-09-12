from enum import Enum, auto
from typing import List

import numpy
import pytorch_lightning as pl
import torch
import torchvision
from matplotlib import cm
from PIL import Image
from torchvision.models.detection import MaskRCNN_ResNet50_FPN_V2_Weights
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor


def merge_list_of_tensor_masks(masks: List[numpy.array]) -> numpy.array:
    merged_masks = numpy.zeros_like(masks[0])
    # we set a threshold to separate the background (value = 0) from the other components (value >= 100)
    background_threshold = 1_000
    for mask_idx, mask in enumerate(masks[0:]):
        merged_masks += mask.astype(numpy.uint8) * (mask_idx + background_threshold)
    return merged_masks


def normalize_image_mask_values_between_zero_and_one(image_mask: numpy.array) -> numpy.array:
    smooth = 10e-10
    return (image_mask - numpy.min(image_mask)) / ((numpy.max(image_mask) - numpy.min(image_mask)) + smooth)


def convert_normalized_array_to_pil_image(image_mask_norm: numpy.array) -> Image:
    return Image.fromarray(numpy.uint8(cm.inferno(image_mask_norm) * 255))


class ModelStep(Enum):
    TRAIN = auto()
    VALIDATION = auto()
    TEST = auto()


class MaskRCNN(pl.LightningModule):
    def __init__(self, mask_threshold: float = 0.5):
        super().__init__()
        self.model = torchvision.models.detection.maskrcnn_resnet50_fpn_v2(
            weights=MaskRCNN_ResNet50_FPN_V2_Weights.DEFAULT
        )

        # Replace the final predictor
        in_features = self.model.roi_heads.box_predictor.cls_score.in_features
        self.model.roi_heads.box_predictor = FastRCNNPredictor(in_features, num_classes=2)
        self.mask_threshold = mask_threshold

    def forward(self, batch):
        return self.model(batch)

    def training_step(self, batch, batch_idx):
        self.model.train()
        images, targets = batch
        loss_dict = self.model(images, targets)
        sum_losses = sum(loss for loss in loss_dict.values())
        self.log("train_loss", sum_losses, batch_size=len(batch), sync_dist=True)
        return sum_losses

    def validation_step(self, batch, batch_idx):
        images, targets = batch
        with torch.no_grad():
            # Get the losses
            self.model.train()
            loss_dict = self.model(images, targets)
            sum_losses = sum(loss for loss in loss_dict.values())
            self.log("val_loss", sum_losses, batch_size=len(batch), sync_dist=True)

            # Output the predictions
            self.model.eval()
            outputs = self.model(images)
            for idx, output_in_batch in enumerate(outputs):
                self.logger.log_output(
                    ModelStep.VALIDATION,
                    output_in_batch,
                    targets[idx],
                    self.mask_threshold,
                    self.current_epoch,
                )
        return sum_losses

    def test_step(self, batch, batch_idx):
        images, targets = batch
        self.model.eval()
        with torch.no_grad():
            outputs = self.model(images)
            for idx, output_in_batch in enumerate(outputs):
                self.logger.log_output(ModelStep.TEST, output_in_batch, targets[idx], self.mask_threshold)

    def configure_optimizers(self):
        optimizer = torch.optim.AdamW(params=self.model.parameters(), lr=1e-5)
        return optimizer
