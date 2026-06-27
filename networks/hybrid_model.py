import torch
import torch.nn as nn
from core.config import (
    NUM_FEATURES,
    CONV_OUT,
    ATTENTION_HEADS,
    DROPOUT
)


class NeuroLLaCore(nn.Module):
    """
    Single, canonical NeuroLLa model: a temporal Conv1d layer extracts
    short local patterns from the raw feature sequence, multi-head
    self-attention lets every timestep weigh every other timestep, and
    a feedforward block with residual connections refines the result
    before mean-pooling into a 3-class (SELL/HOLD/BUY) classification.

    All hyperparameter defaults come from core.config, so changing the
    network's width/feature count/dropout in one place (config.py)
    changes it everywhere this class is constructed.
    """

    def __init__(
        self,
        input_dim=NUM_FEATURES,
        embed_dim=CONV_OUT * 2,
        num_heads=ATTENTION_HEADS,
        num_classes=3,
        dropout=DROPOUT
    ):
        super().__init__()

        self.temporal_cnn = nn.Conv1d(
            in_channels=input_dim,
            out_channels=embed_dim,
            kernel_size=3,
            padding=1
        )

        self.attention = nn.MultiheadAttention(
            embed_dim=embed_dim,
            num_heads=num_heads,
            batch_first=True,
            dropout=dropout
        )

        self.layer_norm1 = nn.LayerNorm(embed_dim)
        self.layer_norm2 = nn.LayerNorm(embed_dim)

        self.ffn = nn.Sequential(
            nn.Linear(embed_dim, embed_dim * 2),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(embed_dim * 2, embed_dim)
        )

        self.classifier = nn.Linear(
            embed_dim,
            num_classes
        )

    def forward(self, x):
        # x arrives as (batch, sequence_length, num_features); Conv1d
        # expects channels first, so permute to (batch, num_features, seq).
        x = x.permute(0, 2, 1)

        cnn_features = self.temporal_cnn(x)

        cnn_features = cnn_features.permute(0, 2, 1)

        attn_output, _ = self.attention(
            cnn_features,
            cnn_features,
            cnn_features
        )

        x = self.layer_norm1(
            cnn_features + attn_output
        )

        ffn_output = self.ffn(x)

        x = self.layer_norm2(
            x + ffn_output
        )

        pooled = torch.mean(x, dim=1)

        logits = self.classifier(pooled)

        return logits
