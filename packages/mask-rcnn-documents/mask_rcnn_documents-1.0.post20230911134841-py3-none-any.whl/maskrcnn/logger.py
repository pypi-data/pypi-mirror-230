import abc
import json
from abc import ABC
from collections import defaultdict
from pathlib import Path

import cv2
import numpy
from pytorch_lightning.loggers import CSVLogger, MLFlowLogger
from shapely.geometry import Polygon
from torch import Tensor

from maskrcnn.model import (
    ModelStep,
    convert_normalized_array_to_pil_image,
    merge_list_of_tensor_masks,
    normalize_image_mask_values_between_zero_and_one,
)


class CensusTableLogger(ABC):
    @abc.abstractmethod
    def log_output(
        self,
        step: ModelStep,
        output,
        target,
        mask_threshold: float,
        current_epoch: int = None,
    ):
        raise NotImplementedError()


def segmentation_contours_from_masks_and_labels(
    scores: Tensor, labels: Tensor, masks: Tensor, mask_threshold: float = 0.5
):
    """
    Get the polygon made from the segmentation model and sort the segmentations
    based on labels.
    :param scores: the confidence prediction scores of the model
    :param labels: the labels predicted by the model
    :param masks: the output segmentation masks for each instance found
    :return: a dictionary with labels as keys and confidence scores and
    polygons as values.

    .. see: the format is made for https://gitlab.com/teklia/dla/arkindex_document_layout_training_label_normalization
    """
    scores = scores.detach().cpu().numpy()
    labels = labels.detach().cpu().numpy()
    masks = masks.detach().cpu().numpy()

    predicted_polygons = defaultdict(list)
    for score, label, mask in zip(scores, labels, masks):
        contours, _ = cv2.findContours(
            numpy.uint8(mask > mask_threshold).squeeze(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        for contour in contours:
            coordinates = contour.squeeze().tolist()
            if len(coordinates) >= 4:  # a polygon has at least 4 points
                polygon = {"confidence": round(float(score), 5), "polygon": coordinates}
                predicted_polygons[str(label)].append(polygon)
    return predicted_polygons


class CensusTableCSVLogger(CSVLogger, CensusTableLogger):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def simplify_predicitions(
        self,
        o_scores: Tensor,
        o_labels: Tensor,
        o_masks: Tensor,
        mask_threshold: float = 0.5,
        min_area_for_connected_components: float = 50.0,
    ):
        original_scores = o_scores.detach().cpu().numpy().squeeze()
        original_labels = o_labels.detach().cpu().numpy().squeeze()
        original_masks = o_masks.detach().cpu().numpy().squeeze()

        scores, labels, simplified_masks, polygons = [], [], [], defaultdict(list)
        for score, label, mask in zip(original_scores, original_labels, original_masks):
            contours, _ = cv2.findContours(
                numpy.uint8(mask > mask_threshold).squeeze(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )
            for contour in contours:
                coordinates = contour.squeeze().tolist()
                # A polygon has at least four coordinates
                if len(coordinates) >= 4:
                    polygon = Polygon(numpy.squeeze(contour))
                    simplified_polygon = polygon.simplify(tolerance=0.5, preserve_topology=True)

                    # let’s remove small connected components
                    if simplified_polygon.area > min_area_for_connected_components:
                        points = numpy.array(simplified_polygon.exterior.coords[:-1], numpy.int32)
                        simplified_mask = numpy.zeros_like(mask)
                        cv2.fillPoly(simplified_mask, [points], 1)

                        polygons[str(label)].append({"confidence": round(float(score), 5), "polygon": points.tolist()})
                        simplified_masks.append(simplified_mask)
                        labels.append(label)
                        scores.append(scores)

        return scores, labels, simplified_masks, polygons

    def log_output(
        self,
        step: ModelStep,
        output,
        target,
        mask_threshold: float = 0.5,
        current_epoch: int = None,
        min_area_for_connected_components: float = 50,
    ):
        write_path = Path(self.log_dir) / step.name.lower()
        if step == ModelStep.VALIDATION and current_epoch is not None:
            base_path = write_path / f"epoch_{current_epoch}"
            image_path = base_path / f"{target.get('name')}.png"
            json_path = base_path / f"{target.get('name')}.json"
        else:
            image_path = write_path / f"{target.get('name')}.png"
            json_path = write_path / f"{target.get('name')}.json"
        image_path.parent.mkdir(parents=True, exist_ok=True)

        scores, labels, masks, score_contours = self.simplify_predicitions(
            output.get("scores"),
            output.get("labels"),
            output.get("masks"),
            mask_threshold,
            min_area_for_connected_components,
        )

        # Export the predicted image
        if len(masks) > 0:
            image_mask = merge_list_of_tensor_masks(masks)
        else:
            image_mask = numpy.zeros_like(target.get("shape"), dtype=numpy.uint8)

        image_mask_norm = normalize_image_mask_values_between_zero_and_one(image_mask)
        image_mask = convert_normalized_array_to_pil_image(image_mask_norm)
        image_mask.save(image_path)

        score_contours["img_size"] = [image_mask.height, image_mask.width]
        with open(json_path, mode="w") as j_of:
            json.dump(score_contours, j_of, indent=2)


class CensusMLFlowLogger(MLFlowLogger, CensusTableLogger):
    def log_output(
        self,
        step: ModelStep,
        output,
        target,
        mask_threshold: float,
        current_epoch: int = None,
    ):
        pass
