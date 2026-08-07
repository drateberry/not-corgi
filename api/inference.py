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

import io
import base64
import numpy as np
import keras
from PIL import Image, ImageOps

import config
import gradcam

def load_model(path):
    """Load the trained model from disk. Called once at app startup.
    """
    model = keras.models.load_model(path, compile=False)
    if not isinstance(model, keras.Model):
        raise RuntimeError(f"failed to load model from {path}")
    # Warm up Tensorflow
    dummy = np.zeros((1, *config.IMAGE_SIZE, 3), dtype="float32")
    model.predict(dummy, verbose=0) # pyright: ignore[reportArgumentType]

    return model


def preprocess(image_bytes):
    """Decode an uploaded image and prepare it for the model.

    Must mirror the training-time preprocessing exactly — see module docstring.
    """
    img = Image.open(io.BytesIO(image_bytes))
    # iOS stores rotation as metadata, we need to know that for the model
    img = ImageOps.exif_transpose(img)

    img = img.convert("RGB").resize(config.IMAGE_SIZE)
    return np.asarray(img, dtype="float32")


def predict(model, image_bytes):
    """Return class probabilities and the Grad-CAM overlay for one image.
    """
    x = preprocess(image_bytes)
    probs = model.predict(x[None], verbose=0)[0]
    idx = int(np.argmax(probs))
    hm = gradcam.compute_heatmap(model, x, idx, config.LAST_CONV_LAYER)
    composite = gradcam.overlay(x.astype(np.uint8), hm)
    buffer = io.BytesIO()
    Image.fromarray(composite).save(buffer, format="PNG")

    return {
        "predicted_class": config.CLASS_NAMES[idx],
        "confidence": float(probs[idx]),
        "probabilities": {
            name: float(p) for name, p in zip(config.CLASS_NAMES, probs)
        },
        "is_corgi": config.CLASS_NAMES[idx] != "Not_Corgi",
        "gradcam": base64.b64encode(buffer.getvalue()).decode(),
    }

