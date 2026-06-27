import torch

# Dataset
SEQUENCE_LENGTH = 128
PREDICTION_HORIZON = 20
PROFIT_THRESHOLD = 0.005

# Triple barrier labeling (shared by core/labels.py and train.py)
TP_MULT = 2.0
SL_MULT = 1.0
LABEL_HORIZON = 20

# Feature columns, in the exact order the model consumes them.
# core/features.py must produce every one of these columns.
# Length of this list must equal NUM_FEATURES below.
FEATURE_COLUMNS = [
    "open", "high", "low", "close", "tick_volume",
    "ema10", "ema20", "ema50", "ema100",
    "rsi", "rsi_slope",
    "atr", "atr_pct",
    "returns", "log_returns",
    "volatility", "volatility_ratio",
    "macd", "macd_signal", "macd_hist",
    "bb_width", "bb_position",
    "stoch_k", "stoch_d",
    "adx",
    "momentum",
    "high_low_range",
    "body_size",
    "hour_sin",
]

# Features
NUM_FEATURES = len(FEATURE_COLUMNS)

# Training
BATCH_SIZE = 64
EPOCHS = 50
LEARNING_RATE = 0.0003
VALIDATION_SPLIT = 0.15
TEST_SPLIT = 0.15
EARLY_STOPPING_PATIENCE = 8
GRADIENT_CLIP_NORM = 1.0

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
MIN_CONFIDENCE = 0.68

# Model paths (single source of truth - every module that loads/saves
# the model imports these instead of hardcoding the string).
MODEL_DIR = "models/trained"
MODEL_SAVE_PATH = "models/trained/neurolla.pth"
SCALER_SAVE_PATH = "models/trained/scaler.joblib"
CHECKPOINT_DIR = "models/checkpoints"
CHECKPOINT_PATH = "models/checkpoints/latest.pth"

# Device
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
