"""Evaluate the trained classifier against the held-out test set.

Per specifications.md section 6, accuracy alone is NOT an acceptable evaluation:
a model that identifies Not_Corgi perfectly while confusing Pembrokes with
Cardigans can still report a high aggregate number while failing at the actual
task. Required output:

  - a confusion matrix over the held-out test set
  - per-class precision and recall

Expected performance, for calibration:
  - corgi vs. not-corgi: high 90s, without difficulty
  - Pembroke vs. Cardigan: mid-80s is a respectable result
  - at or near 99% on the breed distinction is a data-leakage signal, not a
    success — investigate before reporting it (see prepare_data.find_near_duplicates)

Writes figures and metrics into model/reports/ for inclusion in DESIGN.md.
"""

import json

import numpy as np
import keras
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
from PIL import Image

import constants
import gradcam

def load_test_set():
    """Load model/data/processed/test/ without augmentation and without shuffling.
    """
    return keras.utils.image_dataset_from_directory(
        constants.PROC_DIR / "test",
        labels="inferred", label_mode="int",
        class_names=constants.CLASS_NAMES,
        image_size=constants.IMAGE_SIZE,
        batch_size=constants.BATCH_SIZE,
        shuffle=False,
    )


def confusion(model, test_ds):
    """Return the 3x3 confusion matrix over the test set.
    """
    y_true = np.concatenate([y.numpy() for _, y in test_ds])
    y_pred = model.predict(test_ds).argmax(axis=1)

    k = len(constants.CLASS_NAMES)
    matrix = np.zeros((k, k), dtype=int)
    for t, p in zip(y_true, y_pred):
        matrix[t, p] += 1
    return matrix


def per_class_metrics(matrix):
    """Return precision and recall per class from the confusion matrix.
    """
    out = {}
    for i, name in enumerate(constants.CLASS_NAMES):
        tp = matrix[i, i]
        precision = tp / matrix[:, i].sum() if matrix[:, i].sum() else 0.0
        recall = tp / matrix[i, :].sum() if matrix[i, :].sum() else 0.0
        out[name] = {"precision": float(precision), "recall": float(recall), "support": int(matrix[i, :].sum())}
    return out


def headline_metrics(matrix):
    corgi = [0, 2]
    overall = np.trace(matrix) / matrix.sum()

    # corgi vs not-corgi. Both corgi breeds collapsed into one
    binary_correct = matrix[1, 1] + matrix[np.ix_(corgi, corgi)].sum()
    binary = binary_correct / matrix.sum()

    # breed accuracy between two corgi classes
    breed_total = matrix[np.ix_(corgi, [0, 1, 2])].sum()
    breed = (matrix[0, 0] + matrix[2, 2]) / breed_total
    return {"overall": float(overall), "corgi_vs_not": float(binary),
            "breed_given_corgi": float(breed), "breed_n": int(breed_total)}

def inspect_errors(model, test_ds, matrix):
    """Pull the actual misclassified images rather than guessing at them.

    Two things to separate: images where the tail is not visible (the real
    ceiling described in spec section 2, and not a fixable error), and any
    systematic Pembroke/Cardigan confusion that survives even when the tail IS
    visible (which is a model problem and is fixable). Running gradcam over the
    errors is how that distinction gets made, and the answer belongs in DESIGN.md.
    """
    paths = test_ds.file_paths
    y_true = np.concatenate([y.numpy() for _, y in test_ds])
    probs = model.predict(test_ds, verbose=0)
    y_pred = probs.argmax(axis=1)
    wrong = np.where(y_true != y_pred)[0]
    print(f"\n{len(wrong)} misclassified images")

    records = []
    fig, axes = plt.subplots(len(wrong), 2, figsize=(6, 3 * len(wrong)))
    for row, i in enumerate(wrong):
        path = Path(paths[i])
        img = np.asarray(
            Image.open(path).convert("RGB").resize(constants.IMAGE_SIZE), dtype="float32"
        )
        hm = gradcam.compute_heatmap(model, img, int(y_pred[i]), constants.LAST_CONV_LAYER)
        composite = gradcam.overlay(img.astype(np.uint8), hm)
        true_name = constants.CLASS_NAMES[y_true[i]]
        pred_name = constants.CLASS_NAMES[y_pred[i]]
        conf = float(probs[i][y_pred[i]])
        axes[row, 0].imshow(img.astype(np.uint8))
        axes[row, 0].set_title(f"{path.name}\ntrue: {true_name}", fontsize=8)
        axes[row, 1].imshow(composite)
        axes[row, 1].set_title(f"predicted: {pred_name} @ {conf:.2f}", fontsize=8)
        for col in (0, 1):
            axes[row, col].axis("off")
        records.append({"file": path.name, "true": true_name,
                        "predicted": pred_name, "confidence": round(conf, 3),
                        "judgement": ""})
        print(f"  {path.name:<28} true {true_name:<10} pred {pred_name:<10} {conf:.2f}")
    fig.savefig(constants.REPORTS_DIR / "errors.png", dpi=128, bbox_inches="tight")
    (constants.REPORTS_DIR / "errors.json").write_text(json.dumps(records, indent=2))
    return records


def main():
    """Evaluate, print the report, and save artifacts into model/reports/.

    Two ways of reading the numbers worth carrying over from CS80/week5/traffic:

      - Test accuracy above final training accuracy is Dropout, not a miracle.
        Dropout is active during training and disabled at evaluation, so the
        reported training number is pessimistic.
      - Accuracy going flat while loss keeps improving means the model is
        getting more confident, not more correct. That matters more here than
        it did there: a Pembroke call that moves from 0.51 to 0.85 is real
        progress that an accuracy column will not show.
    """
    model = keras.models.load_model(constants.MODEL_PATH)
    matrix = confusion(model, load_test_set())

    print("\n confusion matrix - rows actual, columns predicted")
    print(f"{'':<12}" + "".join(f"{n:>11}" for n in constants.CLASS_NAMES))
    for i, name in enumerate(constants.CLASS_NAMES):
        print(f"{name:<12}" + "".join(f"{v:>11}" for v in matrix[i]))

    per_class = per_class_metrics(matrix)
    headline = headline_metrics(matrix)

    print()
    for name, m in per_class.items():
        print(f"{name:<12} precision {m['precision']:.3f} "f"recall {m['recall']:.3f} n={m['support']}")
    print()
    for k, v in headline.items():
        print(f"{k:<20} {v}")

    constants.REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    (constants.REPORTS_DIR / "metrics.json").write_text(json.dumps({
        "confusion_matrix": matrix.tolist(),
        "per_class": per_class,
        "headline": headline,
    }, indent=2))

    fig, ax = plt.subplots(figsize=(5, 4.5))
    ax.matshow(matrix, cmap="Blues")
    ax.set_xticks(range(3), constants.CLASS_NAMES, rotation=45, ha="left")
    ax.set_yticks(range(3), constants.CLASS_NAMES)
    ax.set_xlabel("predicted"); ax.set_ylabel("actual")
    for (i,j), v in np.ndenumerate(matrix):
        ax.text(j, i, str(v), ha="center", va="center")
    fig.savefig(constants.REPORTS_DIR / "confusion_matrix.png", dpi=150, bbox_inches="tight")
    inspect_errors(model, load_test_set(), matrix)

if __name__ == "__main__":
    main()
