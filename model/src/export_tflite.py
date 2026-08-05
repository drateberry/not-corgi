"""Convert the trained Keras model to TensorFlow Lite / LiteRT.

This is the BEST-tier stretch goal from specifications.md section 3 — on-device
inference so the app works with weak or absent connectivity. Scope discipline
from that same section applies:

    The server-based inference path is the primary implementation. On-device
    inference is attempted only after the full pipeline works end to end. If the
    two conflict, the working pipeline wins. Descoping the stretch goal is an
    acceptable outcome; descoping it silently is not — the decision and its
    rationale belong in DESIGN.md.

Note also (spec section 4.3) that consuming a TFLite model in React Native needs
a native ML runtime, which means an Expo development build rather than Expo Go.
That is a second reason this is scoped last.

Leave this file unimplemented until train.py, evaluate.py, the API, and the app
all work end to end.
"""

# TODO: imports


def convert():
    """Convert the saved Keras model in model/artifacts/ to a .tflite file.

    TODO: implement, if the stretch goal is attempted.
    """
    raise NotImplementedError


def verify_parity():
    """Check that the converted model agrees with the Keras model on test images.

    A conversion that silently changes predictions is worse than no conversion.

    TODO: implement.
    """
    raise NotImplementedError


if __name__ == "__main__":
    convert()
