"""Configuration for the Flask API.

Class ordering is imported from the training code rather than duplicated.
specifications.md section 5.2 requires the Cardigan=0 / Not_Corgi=1 /
Pembroke=2 mapping be consistent across training, API, and app — a mismatch
scrambles labels silently with no error. One definition, imported everywhere,
is the cheapest way to guarantee that.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

API_DIR = Path(__file__).resolve().parent
load_dotenv(API_DIR / ".env")

MODEL_SRC = API_DIR.parent / "model" / "src"
sys.path.insert(0, str(MODEL_SRC))

from constants import CLASS_NAMES, IMAGE_SIZE, LAST_CONV_LAYER # noqa: E402

# Let's make sure that model_path can be resolved no matter where the shell is
MODEL_PATH = Path(os.environ.get("MODEL_PATH", "artifacts/not_corgi.keras"))
if not MODEL_PATH.is_absolute():
    MODEL_PATH = API_DIR / MODEL_PATH

HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", 5001))

MAX_CONTENT_LENGTH = 10 * 1024 * 1024
