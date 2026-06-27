import torch.nn as nn
from core.config import CONV_OUT, LSTM_HIDDEN, LSTM_LAYERS


class LSTMBlock(nn.Module):
    def __init__(self):
        super().__init__()

        self.lstm = nn.LSTM(
            input_size=CONV_OUT,
            hidden_size=LSTM_HIDDEN,
            num_layers=LSTM_LAYERS,
            batch_first=True,
            bidirectional=True
        )

    def forward(self, x):
        output, _ = self.lstm(x)
        return output