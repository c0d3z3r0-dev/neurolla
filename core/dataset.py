import torch
from torch.utils.data import Dataset


class MarketDataset(Dataset):
    def __init__(self, features, labels):
        self.features = torch.tensor(features, dtype=torch.float32)
        # Long/int64 labels are required by nn.CrossEntropyLoss, which is
        # what trains this 3-class (SELL/HOLD/BUY) model.
        self.labels = torch.tensor(labels, dtype=torch.long)

    def __len__(self):
        return len(self.features)

    def __getitem__(self, idx):
        return self.features[idx], self.labels[idx]