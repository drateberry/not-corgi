"""Shared constants for the Not Corgi model.

This module is the single source of truth for the class ordering. Per
specifications.md section 5.2, the mapping is fixed and alphabetical because
Keras's image_dataset_from_directory assigns labels by sorted folder name:

    Cardigan = 0, Not_Corgi = 1, Pembroke = 2

A mismatch between training, API, and app scrambles labels silently with no
error, so both the training code and the API import this ordering rather than
re-declaring it.
"""

from pathlib import Path

# Index position in this list IS the class index. Do not reorder.
CLASS_NAMES = ["Cardigan", "Not_Corgi", "Pembroke"]

# set the input resolution the chosen MobileNetV3 variant expects.
IMAGE_SIZE = (224, 224)

# pick a batch size that fits available memory.
BATCH_SIZE = 32

TRAIN_SPLIT = 0.7
VAL_SPLIT = 0.15
TEST_SPLIT = 0.15

# Random seed, so splits are reproducible across runs.
SEED = 32

# Max Hamming distance between two 64-bit phashes for images to count as
# near-duplicates.
PHASH_THRESHOLD = 10

# Anchoring to the file not the shell's directory
SRC_DIR  = Path(__file__).resolve().parent
RAW_DIR  = SRC_DIR.parent / "data" / "raw"
PROC_DIR = SRC_DIR.parent / "data" / "processed"
ARTIFACTS_DIR = SRC_DIR.parent / "artifacts"
REPORTS_DIR = SRC_DIR.parent / "reports"
MODEL_PATH = ARTIFACTS_DIR / "not_corgi.keras"

# Grad-CAM target
LAST_CONV_LAYER = "activation_19"

DROPOUT = 0.3
HEAD_EPOCS = 40
HEAD_LR = 1e-3
FINE_TUNE_EPOCS = 30
FINE_TUNE_LR = 1e-5
FINE_TUNE_FROM = 150
