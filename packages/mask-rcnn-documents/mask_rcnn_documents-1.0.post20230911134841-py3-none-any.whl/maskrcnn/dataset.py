from pathlib import Path
from typing import Any, Dict, Tuple

import cv2
import numpy
import torch
from PIL import Image
from torch import Tensor
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms as T


class CensusTableDataset(Dataset):
    def __init__(self, root, transform: T.Compose = None, target_transform: T.Compose = None):
        self.root = root
        if transform:
            self.transform = transform
        else:
            # Image should be tensors of inputs in range [0, 1]
            self.transform = T.Compose([T.PILToTensor(), T.ConvertImageDtype(torch.float32)])
        self.target_transform = target_transform
        self.root_path = Path(self.root)
        self.images = sorted((self.root_path / "images").iterdir())
        self.masks = sorted((self.root_path / "labels").iterdir())

    def __len__(self):
        return len(self.images)

    def __getitem__(self, index) -> Tuple[Tensor, Dict[str, Any]]:
        image_path = self.images[index]
        mask_path = self.masks[index]

        # Load the image
        image = Image.open(image_path).convert("RGB")

        # Load the mask
        (
            number_of_instances,
            mask,
        ) = self.__transform_mask_image_into_a_connected_components_image(Image.open(mask_path).convert("RGB"))

        # Get the identifiers of all the element of the mask
        # They are all encoded using a different color.
        object_ids = numpy.unique(mask)
        object_ids = object_ids[1:]  # remove the background

        # split the color-encoded mask into a set
        # of binary masks
        masks = mask == object_ids[:, None, None]

        # Get the bounding boxes for all the objects
        number_of_objects = len(object_ids)

        # For Mask-RCNN, bounding boxes are expected to be in
        # [x0, y0, x1, y1] format
        bounding_boxes, selected_masks, nb_of_selected_masks = [], numpy.zeros(shape=masks.shape), 0
        for i in range(number_of_objects):
            # Where the pixels have the value of the object id
            position = numpy.where(masks[i])
            # In numpy, the shape is (height, width)
            x_min = numpy.min(position[1])
            x_max = numpy.max(position[1])
            y_min = numpy.min(position[0])
            y_max = numpy.max(position[0])

            # If the bounding box has more than one pixel.
            if x_max > x_min and y_max > y_min:
                bounding_boxes.append([x_min, y_min, x_max, y_max])
                selected_masks[i] = masks[i]
                nb_of_selected_masks += 1

        # Convert elements to Tensors
        bounding_boxes = torch.as_tensor(bounding_boxes, dtype=torch.float32)
        labels = torch.ones((nb_of_selected_masks,), dtype=torch.int64)
        masks = torch.as_tensor(selected_masks, dtype=torch.uint8)

        target = {
            "boxes": bounding_boxes,
            "labels": labels,
            "masks": masks,
            "shape": [image.height, image.width],
            "name": Path(image_path).stem,
        }

        if self.transform:
            image = self.transform(image)

        if self.target_transform:
            target = self.target_transform(target)

        return image, target

    @staticmethod
    def __transform_mask_image_into_a_connected_components_image(
        mask_image: Image,
    ) -> Tuple[int, numpy.array]:
        # In Pillow, images are encoded in RGB, not in OpenCV
        image_cv2 = cv2.cvtColor(numpy.array(mask_image), cv2.COLOR_RGB2BGR)
        # In order to binarize the image, to have the thresholding function work, we need to convert it
        # to grayscale.
        image_cv2_grey = cv2.cvtColor(image_cv2, cv2.COLOR_BGR2GRAY)
        image_cv2_binarised = cv2.threshold(image_cv2_grey, 128, 192, cv2.THRESH_OTSU)[1]
        # Then, we extract the connected components of the image.
        number_labels, labels = cv2.connectedComponents(image_cv2_binarised)
        return number_labels, labels.reshape(mask_image.size)


class CensusTableDataLoader(DataLoader):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.collate_fn = collate_fn


def collate_fn(batch):
    return tuple(zip(*batch))
