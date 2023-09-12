#!/bin/env python3

import argparse
import multiprocessing
import time
from pathlib import Path

import pytorch_lightning as pl
import torch
from lightning_fabric import seed_everything

from maskrcnn.dataset import CensusTableDataLoader, CensusTableDataset
from maskrcnn.logger import CensusTableCSVLogger
from maskrcnn.model import MaskRCNN


def main():
    parser = argparse.ArgumentParser("Test Mask-RCNN model.")
    parser.add_argument(
        "--data-path",
        help="Path to the directory where are stored the images and labels. In this directory,"
        " there should be a test directory containing another images and labels subdirectories.",
        type=str,
        required=True,
    )
    parser.add_argument(
        "--model-checkpoint",
        help="Path to the model checkpoint to test",
        type=str,
        required=True,
    )
    parser.add_argument(
        "--threshold",
        help="Confidence threshold in the model to export the masks.",
        type=float,
        required=False,
        default=0.5,
    )
    parser.add_argument(
        "--device",
        "-d",
        default="cpu",
        help="Device on which to run the neural network (’cpu’ or ‘cuda’)",
        type=str,
        required=False,
    )
    parser.add_argument("--experiment-name", type=str, required=True, help="Name of the experiment")

    args = parser.parse_args()

    seed_everything(0, workers=True)
    maskrcnn = MaskRCNN.load_from_checkpoint(args.model_checkpoint)
    test_dataloader = CensusTableDataLoader(
        CensusTableDataset(Path(args.data_path) / "test"),
        num_workers=multiprocessing.cpu_count() // 2,
    )
    loggers = [
        CensusTableCSVLogger(save_dir=Path("."), name=args.experiment_name),
    ]
    extra_params = {"accelerator": args.device}
    if args.device.startswith("cuda"):
        extra_params = {
            "accelerator": "gpu",
            "devices": torch.cuda.device_count(),
        }

    trainer = pl.Trainer(deterministic=True, **extra_params, logger=loggers)
    maskrcnn.mask_threshold = args.threshold

    start_time = time.time()
    trainer.test(model=maskrcnn, dataloaders=test_dataloader)
    end_time = time.time()

    fps = len(test_dataloader) / (end_time - start_time)
    for logger in loggers:
        output_path = Path(logger.log_dir)
        with open(output_path / "fps.txt", mode="w") as of:
            of.write(f"{fps:.2f}\n")


if __name__ == "__main__":
    main()
