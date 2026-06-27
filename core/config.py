import torch

# Dataset
SEQUENCE_LENGTH = 128
PREDICTION_HORIZON = 20
PROFIT_THRESHOLD = 0.005

# Features
NUM_FEATURES = 29

# Training
BATCH_SIZE = 64
EPOCHS = 50
LEARNING_RATE = 0.0003

# Network
CONV_OUT = 64
LSTM_HIDDEN = 128
LSTM_LAYERS = 2
ATTENTION_HEADS = 8
DROPOUT = 0.2

# Risk
MAX_RISK_PER_TRADE = 0.02
MAX_DAILY_DRAWDOWN = 0.05
MAX_OPEN_POSITIONS = 3

# Model Paths
MODEL_SAVE_PATH = "models/trained/tradenet.pth"
CHECKPOINT_PATH = "models/checkpoints/checkpoint.pth"

# Device
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"