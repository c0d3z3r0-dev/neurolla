import torch.nn as nn
from core.config import LSTM_HIDDEN, ATTENTION_HEADS


class AttentionBlock(nn.Module):
    def __init__(self):
        super().__init__()

        self.attention = nn.MultiheadAttention(
            embed_dim=LSTM_HIDDEN * 2,
            num_heads=ATTENTION_HEADS,
            batch_first=True
        )

    def forward(self, x):
        output, _ = self.attention(x, x, x)
        return output