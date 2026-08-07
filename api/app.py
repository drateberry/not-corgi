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

from flask import Flask, jsonify, request
from flask_cors import CORS
from PIL import UnidentifiedImageError

import config
import inference

def create_app(model=None):
    """Build and configure the Flask application.
    """
    app = Flask(__name__)
    app.config["MAX_CONTENT_LENGTH"] = config.MAX_CONTENT_LENGTH
    CORS(app)
    app.config["MODEL"] = model if model is not None else inference.load_model(
        config.MODEL_PATH
    )

    @app.get("/health")
    def health():
        # Returns model status as part of health check
        return jsonify({
            "status": "ok",
            "model_loaded": app.config["MODEL"] is not None,
            "classes": config.CLASS_NAMES
        })

    @app.post("/predict")
    def predict():
        if "image" not in request.files:
            return jsonify({"error": "no image file in request", "code": "no_file"}), 400
        data = request.files["image"].read()
        try:
            result = inference.predict(app.config["MODEL"], data)
        except (UnidentifiedImageError, OSError):
            return jsonify({"error": "could not decode image", "code": "bad_image"}), 400
        return jsonify(result)

    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({"error": "malformed request", "code": "bad_request"}), 400

    @app.errorhandler(413)
    def too_large(e):
        return jsonify({"error": "image too large", "code": "too_large"}), 413

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"error": "internal server error", "code": "server_error"}), 500
    
    return app

if __name__ == "__main__":
    # Local development only. Use a production WSGI server when deployed.
    create_app().run(host=config.HOST, port=config.PORT)
