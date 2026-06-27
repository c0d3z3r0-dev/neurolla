import torch
import torch.nn as nn


class NeuroLLaCore(nn.Module):
    def __init__(
        self,
        input_dim=29,
        embed_dim=128,
        num_heads=4,
        num_classes=3
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
            batch_first=True
        )

        self.layer_norm1 = nn.LayerNorm(embed_dim)
        self.layer_norm2 = nn.LayerNorm(embed_dim)

        self.ffn = nn.Sequential(
            nn.Linear(embed_dim, embed_dim * 2),
            nn.GELU(),
            nn.Dropout(0.35),
            nn.Linear(embed_dim * 2, embed_dim)
        )

        self.classifier = nn.Linear(
            embed_dim,
            num_classes
        )

    def forward(self, x):
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