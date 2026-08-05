"""Configuration for the Flask API.

Class ordering is imported from the training code rather than duplicated.
specifications.md section 5.2 requires the Cardigan=0 / Not_Corgi=1 /
Pembroke=2 mapping be consistent across training, API, and app — a mismatch
scrambles labels silently with no error. One definition, imported everywhere,
is the cheapest way to guarantee that.

TODO: make model/src importable from here (path entry, or install the model
package). Until then this import will fail.
"""

# from model.src.constants import CLASS_NAMES  # noqa: F401

# TODO: path to the trained model file (see .env.example).
MODEL_PATH = None

# TODO: maximum accepted upload size. Phone cameras produce large files and the
# demo is on cellular — consider downscaling client-side too.
MAX_CONTENT_LENGTH = None

# TODO: allowed image MIME types / extensions.
ALLOWED_EXTENSIONS = None
