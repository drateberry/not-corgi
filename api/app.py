"""Flask API for Not Corgi.

Per specifications.md section 4.2:
  - Loads the trained model and exposes a prediction endpoint accepting an
    image upload.
  - Returns class probabilities for all three classes plus a Grad-CAM heatmap
    overlay image.
  - Deployed to a cloud host so the mobile client can reach it over cellular.
  - Inference runs on CPU — no GPU dependency for anyone testing the project.

The class ordering (Cardigan=0, Not_Corgi=1, Pembroke=2) is imported from the
training code rather than redeclared here; see config.py.
"""

# TODO: imports (flask, and the helpers from inference.py)


def create_app():
    """Build and configure the Flask application.

    TODO: implement. Load the model once at startup rather than per request —
    model loading is slow and the demo is on cellular data where every second of
    latency shows.
    """
    raise NotImplementedError


# TODO: POST /predict
#   Accepts multipart form data with an image file.
#   Returns JSON: probabilities for all three classes, the predicted class, and
#   the Grad-CAM overlay (base64-encoded, or a URL the app can fetch).
#   Handle the failure cases the app will actually hit: no file, unsupported
#   format, corrupt image, image too large.

# TODO: GET /health
#   Cheap liveness check. Useful for confirming the deployment is up from a dog
#   park before starting to film (spec section 9).


if __name__ == "__main__":
    # Local development only. Use a production WSGI server when deployed.
    create_app().run(debug=True)
