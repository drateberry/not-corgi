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

# TODO: imports


def load_test_set():
    """Load model/data/processed/test/ without augmentation and without shuffling.

    TODO: implement.
    """
    raise NotImplementedError


def confusion(model, test_ds):
    """Return the 3x3 confusion matrix over the test set.

    TODO: implement.
    """
    raise NotImplementedError


def per_class_metrics(matrix):
    """Return precision and recall per class from the confusion matrix.

    TODO: implement.
    """
    raise NotImplementedError


def main():
    """TODO: evaluate, print the report, and save artifacts into model/reports/."""
    raise NotImplementedError


if __name__ == "__main__":
    main()
