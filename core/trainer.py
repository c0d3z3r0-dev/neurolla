import torch
import os


class Trainer:
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
        loss
    ):
        os.makedirs(
            "models/checkpoints",
            exist_ok=True
        )

        torch.save(
            {
                "epoch": epoch,
                "model_state": self.model.state_dict(),
                "optimizer_state": self.optimizer.state_dict(),
                "loss": loss
            },
            "models/checkpoints/latest.pth"
        )

    def load_checkpoint(self):
        path = "models/checkpoints/latest.pth"

        if os.path.exists(path):
            checkpoint = torch.load(path)

            self.model.load_state_dict(
                checkpoint["model_state"]
            )

            self.optimizer.load_state_dict(
                checkpoint["optimizer_state"]
            )

            return checkpoint["epoch"]

        return 0