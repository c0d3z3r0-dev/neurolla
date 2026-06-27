import torch
import os
from core.config import CHECKPOINT_DIR, CHECKPOINT_PATH


class Trainer:
    """
    Wraps checkpoint save/resume so train.py can stop and restart
    without losing progress, and so the best-validation-loss epoch is
    never overwritten by a later, worse epoch.
    """

    def __init__(
        self,
        model,
        optimizer,
        criterion
    ):
        self.model = model
        self.optimizer = optimizer
        self.criterion = criterion

    def save_checkpoint(
        self,
        epoch,
        loss,
        path=CHECKPOINT_PATH
    ):
        os.makedirs(
            CHECKPOINT_DIR,
            exist_ok=True
        )

        torch.save(
            {
                "epoch": epoch,
                "model_state": self.model.state_dict(),
                "optimizer_state": self.optimizer.state_dict(),
                "loss": loss
            },
            path
        )

    def load_checkpoint(self, path=CHECKPOINT_PATH):
        if os.path.exists(path):
            checkpoint = torch.load(path, map_location="cpu")

            self.model.load_state_dict(
                checkpoint["model_state"]
            )

            self.optimizer.load_state_dict(
                checkpoint["optimizer_state"]
            )

            return checkpoint["epoch"]

        return 0
