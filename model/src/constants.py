"""Shared constants for the Not Corgi model.

This module is the single source of truth for the class ordering. Per
specifications.md section 5.2, the mapping is fixed and alphabetical because
Keras's image_dataset_from_directory assigns labels by sorted folder name:

    Cardigan = 0, Not_Corgi = 1, Pembroke = 2

A mismatch between training, API, and app scrambles labels silently with no
error, so both the training code and the API import this ordering rather than
re-declaring it.
"""

# Index position in this list IS the class index. Do not reorder.
CLASS_NAMES = ["Cardigan", "Not_Corgi", "Pembroke"]

# TODO: set the input resolution the chosen MobileNetV3 variant expects.
IMAGE_SIZE = None  # e.g. (224, 224)

# TODO: pick a batch size that fits available memory.
BATCH_SIZE = None

# TODO: fill in once the split strategy is decided (spec section 5.5 requires the
# splits be disjoint at the image level, with augmentation applied after splitting).
TRAIN_SPLIT = None
VAL_SPLIT = None
TEST_SPLIT = None

# Random seed, so splits are reproducible across runs.
SEED = None
