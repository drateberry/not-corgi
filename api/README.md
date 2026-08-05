# api/

Flask API serving the Not Corgi classifier.

| Path | Purpose |
|---|---|
| `app.py` | Flask app and routes |
| `inference.py` | Model loading, preprocessing, prediction |
| `config.py` | Configuration; imports class ordering from `model/src/constants.py` |
| `artifacts/` | Trained model copied here for deployment — gitignored |
| `tests/` | Endpoint tests |

## Endpoints

- `POST /predict` — multipart image upload → three class probabilities + Grad-CAM overlay
- `GET /health` — liveness check

## Running locally

```
pip install -r requirements.txt
cp .env.example .env      # then fill in MODEL_PATH
python app.py
```

TODO: document the deployment target and its URL once chosen.
