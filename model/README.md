# model/

Training pipeline for the Not Corgi classifier.

## Layout

| Path | Purpose |
|---|---|
| `src/constants.py` | Single source of truth for class ordering — imported by the API too |
| `src/prepare_data.py` | Assemble the dataset, check for near-duplicates, split |
| `src/train.py` | Two-phase transfer learning |
| `src/evaluate.py` | Confusion matrix and per-class precision/recall |
| `src/gradcam.py` | Grad-CAM heatmaps, shared with the API |
| `src/export_tflite.py` | Stretch goal: TFLite conversion |
| `data/raw/` | Downloaded source images — gitignored |
| `data/processed/` | Split dataset in the directory layout Keras expects — gitignored |
| `artifacts/` | Trained model files — gitignored |
| `reports/` | Confusion matrix, metrics, Grad-CAM figures for DESIGN.md |

`data/` and `artifacts/` are gitignored to keep the submission ZIP under ~15MB
(specifications.md §7).

## Order of operations

```
python src/prepare_data.py     # raw -> processed splits
python src/train.py            # phase 1 head, then phase 2 fine-tune
python src/evaluate.py         # held-out test set only
python src/export_tflite.py    # stretch goal, last
```

TODO: expand with setup instructions and where to download the raw datasets.
