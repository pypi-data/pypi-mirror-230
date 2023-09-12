#!/usr/bin/env python3
import argparse
import multiprocessing
from pathlib import Path

import pytorch_lightning as pl
import torch
from lightning_fabric import seed_everything
from pytorch_lightning.callbacks import EarlyStopping, ModelCheckpoint

from maskrcnn.dataset import CensusTableDataLoader, CensusTableDataset
from maskrcnn.logger import CensusMLFlowLogger, CensusTableCSVLogger
from maskrcnn.model import MaskRCNN

torch.set_float32_matmul_precision("medium")


def main():
    parser = argparse.ArgumentParser(description="Train a Mask-RCNN model based on ResNet-50")
    parser.add_argument(
        "--data-path",
        help="Path to the directory where are stored the images and labels. In this directory,"
        " there should be a train and a val subdirectory, each containing another images "
        "and labels subdirectories.",
        type=str,
        required=True,
    )
    parser.add_argument("--experiment-name", type=str, required=True, help="Name of the experiment")
    parser.add_argument("--epochs", "-e", type=int, help="Number of epochs", required=True)
    parser.add_argument(
        "--batch-size",
        "-bs",
        default=8,
        help="Batch size for the model",
        type=int,
        required=False,
    )
    parser.add_argument(
        "--device",
        "-d",
        default="cpu",
        help="Device on which to run the neural network",
        type=str,
        required=False,
    )
    parser.add_argument("--log-path", required=False, help="Where to log the model steps", type=str, default="logs")
    parser.add_argument(
        "--mlflow-endpoint",
        required=False,
        help="URL to a MLFlow tracking system",
        type=str,
    )
    parser.add_argument(
        "--model-checkpoint", required=False, help="Model checkpoint to start training from.", type=str
    )

    args = parser.parse_args()
    dataset_path = Path(args.data_path)
    batch_size = args.batch_size
    number_of_epochs = args.epochs
    experiment_name = args.experiment_name
    mlflow_endpoint = args.mlflow_endpoint
    model_checkpoint = args.model_checkpoint

    seed_everything(0, workers=True)

    # Spawning processes is not unlimited because I/O limits of the kernel.
    max_cpus = min(12, multiprocessing.cpu_count())
    train_dataloader = CensusTableDataLoader(
        CensusTableDataset(dataset_path / "train"),
        batch_size=batch_size,
        num_workers=max_cpus,
        persistent_workers=True,
    )
    validation_dataloader = CensusTableDataLoader(
        CensusTableDataset(dataset_path / "val"),
        batch_size=batch_size,
        num_workers=max_cpus,
        persistent_workers=True,
    )
    test_dataloader = CensusTableDataLoader(
        CensusTableDataset(dataset_path / "test"),
        batch_size=batch_size,
        num_workers=max_cpus,
        persistent_workers=True,
    )

    loggers = [
        CensusTableCSVLogger(save_dir=args.log_path, name=experiment_name),
    ]
    if mlflow_endpoint:
        loggers.append(
            CensusMLFlowLogger(
                experiment_name=experiment_name,
                tracking_uri=mlflow_endpoint,
            )
        )

    if model_checkpoint:
        print(f"Starting from existing checkpoint: {Path(model_checkpoint).name}")
        model = MaskRCNN.load_from_checkpoint(model_checkpoint)
    else:
        model = MaskRCNN()

    extra_params = dict()
    if args.device.startswith("cuda"):
        extra_params = {
            "accelerator": "gpu",
            "devices": torch.cuda.device_count(),
        }
    trainer = pl.Trainer(
        max_epochs=number_of_epochs,
        log_every_n_steps=2,
        auto_scale_batch_size=True,
        auto_lr_find=True,
        callbacks=[
            EarlyStopping(monitor="val_loss", mode="min", patience=10),
            # Save checkpoints, and especially the best one if ‘early stopping‘ stops after
            # many validation steps
            ModelCheckpoint(save_top_k=3, monitor="val_loss", mode="min"),
        ],
        logger=loggers,
        deterministic=True,
        **extra_params,
    )
    trainer.fit(
        model=model,
        train_dataloaders=train_dataloader,
        val_dataloaders=validation_dataloader,
    )
    trainer.test(model=model, dataloaders=test_dataloader)


if __name__ == "__main__":
    main()
