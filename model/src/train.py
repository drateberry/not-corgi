"""Train the Not Corgi classifier via transfer learning.

Per specifications.md section 4.1:
  - Backbone: MobileNetV3-class model pretrained on ImageNet. Not trained from
    scratch.
  - Head: GlobalAveragePooling2D -> Dropout -> Dense(3, softmax).
  - Two training phases:
      1. Backbone frozen, train the new head at a higher learning rate.
      2. Unfreeze the top portion of the backbone, fine-tune at ~1e-5.
  - Augmentation: random horizontal flip, rotation, zoom, color jitter.
    NO vertical flips — dogs are not upside down.

Two binding constraints apply here and both fail silently if violated:

  * Spec section 5.3 — do NOT double-normalize. Recent Keras versions bake
    preprocessing into MobileNetV3; calling preprocess_input on top of a model
    that already rescales destroys accuracy with no visible error.
  * Spec section 5.4 — RECOMPILE after changing `trainable`. Unfreezing backbone
    layers for phase two without recompiling fails silently and is the single
    most common Keras fine-tuning bug.

Writes the trained model to model/artifacts/.
"""

# TODO: imports (tensorflow, keras, and constants from .constants)


def build_datasets():
    """Load the processed splits as tf.data datasets.

    Uses image_dataset_from_directory, which assigns labels by sorted folder
    name — this is what produces the Cardigan=0 / Not_Corgi=1 / Pembroke=2
    ordering in constants.CLASS_NAMES. Verify class_names matches after loading.

    TODO: implement.
    """
    raise NotImplementedError


def build_augmentation():
    """Return the augmentation pipeline applied to the training split only.

    Horizontal flip, rotation, zoom, color jitter. No vertical flips.

    TODO: implement.
    """
    raise NotImplementedError


def build_model():
    """Assemble backbone + classification head with the backbone frozen.

    TODO: implement. Remember the no-double-normalization constraint above.
    """
    raise NotImplementedError


def train_head(model, train_ds, val_ds):
    """Phase one: frozen backbone, train the head at a higher learning rate.

    TODO: implement.
    """
    raise NotImplementedError


def fine_tune(model, train_ds, val_ds):
    """Phase two: unfreeze the top of the backbone and fine-tune at ~1e-5.

    TODO: implement. Recompile after setting `trainable` — see module docstring.
    """
    raise NotImplementedError


def main():
    """TODO: run both phases and save the model into model/artifacts/."""
    raise NotImplementedError


if __name__ == "__main__":
    main()
