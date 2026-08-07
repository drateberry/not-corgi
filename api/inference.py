"""Model loading and prediction, kept separate from the HTTP layer in app.py.

Splitting this out means the prediction path can be tested without spinning up
Flask, and keeps the route handlers thin.

Critical: preprocessing here must match training exactly. Per specifications.md
section 5.3, do NOT apply preprocess_input on top of a MobileNetV3 that already
bakes in rescaling — it destroys accuracy with no visible error, and the failure
looks like a bad model rather than a bad API.

Channel order is the other half of that trap. Keras loaders return RGB; OpenCV's
imread returns BGR. Training goes through Keras, so decoding uploads here with
cv2 would feed the model blue dogs — no error, just quietly degraded predictions
that read as a bad model. requirements.txt specifies Pillow rather than
opencv-python to keep both sides on RGB; keep it that way.
"""

# TODO: imports — including gradcam from the model package, so the heatmap the
# app displays comes from the same code path validated during evaluation.


def load_model(path):
    """Load the trained model from disk. Called once at app startup.

    TODO: implement.
    """
    raise NotImplementedError


def preprocess(image_bytes):
    """Decode an uploaded image and prepare it for the model.

    Must mirror the training-time preprocessing exactly — see module docstring.

    TODO: implement.
    """
    raise NotImplementedError


def predict(model, image_bytes):
    """Return class probabilities and the Grad-CAM overlay for one image.

    TODO: implement. Map probabilities back to names via config.CLASS_NAMES —
    never by positional assumption at the call site.
    """
    raise NotImplementedError
