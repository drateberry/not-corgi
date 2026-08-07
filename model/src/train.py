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

import json

import tensorflow as tf
import keras
import constants

def build_datasets():
    """Load the processed splits as tf.data datasets.

    Uses image_dataset_from_directory, which assigns labels by sorted folder
    name — this is what produces the Cardigan=0 / Not_Corgi=1 / Pembroke=2
    ordering in constants.CLASS_NAMES. Verify class_names matches after loading.
    """
    def load(split, shuffle):
        return keras.utils.image_dataset_from_directory(
            constants.PROC_DIR / split,
            labels="inferred",
            label_mode="int",
            class_names=constants.CLASS_NAMES,
            image_size=constants.IMAGE_SIZE,
            batch_size=constants.BATCH_SIZE,
            shuffle=shuffle,
            seed=constants.SEED,
        )

    train_ds, val_ds = load("train", True), load("val", False)
    assert train_ds.class_names == constants.CLASS_NAMES  # pyright: ignore[reportAttributeAccessIssue]
    auto = tf.data.AUTOTUNE
    return (train_ds.cache().prefetch(auto),  # pyright: ignore[reportAttributeAccessIssue]
            val_ds.cache().prefetch(auto))  # pyright: ignore[reportAttributeAccessIssue]



def build_augmentation():
    """Return the augmentation pipeline applied to the training split only.

    Horizontal flip, rotation, zoom, color jitter. No vertical flips.

    KEEP THE COLOR JITTER MILD. Coat color is not incidental here: brindle and
    blue merle are Cardigan-only markers (spec section 2), and they are among
    the few signals still available when the tail is cropped out. Aggressive
    hue/saturation shifts erase exactly the evidence the model needs for the
    hard half of the problem. Geometric augmentation is safe to push harder
    than color augmentation.

    Note also that CS80/week5/traffic omitted flips entirely because arrow
    direction was semantic. Same question, opposite answer: a mirrored corgi is
    still a corgi, so horizontal flip is free. An upside-down one is not.
    """
    return keras.Sequential([
        keras.layers.RandomFlip("horizontal"),
        keras.layers.RandomRotation(0.05),
        keras.layers.RandomZoom(0.1),
        keras.layers.RandomContrast(0.05) # keep this mild to account for color variations, but not confuse breed specific colors
    ], name="augmentation")


def build_model():
    """Assemble backbone + classification head with the backbone frozen.

    Do NOT carry a `Rescaling(1./255)` layer over from CS80/week5/traffic. That
    was correct there because the CNN was trained from scratch; here the
    MobileNetV3 backbone already handles its own input scaling and expects
    [0, 255]. Adding it is the silent-failure case in spec section 5.3.
    """
    base = keras.applications.MobileNetV3Large(
        input_shape=(*constants.IMAGE_SIZE, 3),
        include_top=False,
        weights="imagenet",
    )
    base.trainable = False

    inputs = keras.Input(shape=(*constants.IMAGE_SIZE, 3))
    x = build_augmentation()(inputs)
    x = base(x, training=False)
    x = keras.layers.GlobalAveragePooling2D()(x)
    x = keras.layers.Dropout(constants.DROPOUT)(x)
    outputs = keras.layers.Dense(len(constants.CLASS_NAMES), activation="softmax")(x)
    return keras.Model(inputs, outputs, name="not_corgi")


def class_weights():
    """Our Not_Corgi class outnumbers our corgi classes, so we need to modify the weights"""
    counts = [len(list((constants.PROC_DIR / "train" / c).glob("*.jpg")))
              for c in constants.CLASS_NAMES]
    return {i: sum(counts) / (len(counts) * c) for i, c in enumerate(counts)}


def callbacks():
    return [
        keras.callbacks.ModelCheckpoint(str(constants.MODEL_PATH),
                                        monitor="val_loss", mode="min", save_best_only=True),
        keras.callbacks.EarlyStopping(monitor="val_loss", mode="min",
                                      patience=10, restore_best_weights=True),
    ]


def train_head(model, train_ds, val_ds):
    """Phase one: frozen backbone, train the head at a higher learning rate.
    """
    model.compile(optimizer=keras.optimizers.Adam(constants.HEAD_LR),
                  loss="sparse_categorical_crossentropy", metrics=["accuracy"])
    return model.fit(train_ds, validation_data=val_ds, epochs=constants.HEAD_EPOCS,
                     class_weight=class_weights(), callbacks=callbacks())


def fine_tune(model, train_ds, val_ds):
    """Phase two: unfreeze the top of the backbone and fine-tune at ~1e-5.

    Recompile after setting `trainable` — see module docstring.

    If phase one uses a decaying learning-rate schedule, build a FRESH optimizer
    and schedule here rather than reusing the phase-one objects. A schedule
    carried across phases is already partway down its own decay curve and will
    not restart, so the effective phase-two rate is not the ~1e-5 intended.
    """
    base = model.get_layer("MobileNetV3Large")
    base.trainable = True
    for layer in base.layers[:constants.FINE_TUNE_FROM]:
        layer.trainable = False
    # Keep BatchNorm frozen to keep noise to a minimum
    for layer in base.layers:
        if isinstance(layer, keras.layers.BatchNormalization):
            layer.trainable = False
    unfrozen = sum(1 for l in base.layers if l.trainable)
    print(f"fine-tuning {unfrozen} of {len(base.layers)} backbone layers")
    assert unfrozen > 0, "phase two unfroze nothing — check the backbone lookup"

    model.compile(optimizer=keras.optimizers.Adam(constants.FINE_TUNE_LR),
                  loss="sparse_categorical_crossentropy", metrics=["accuracy"])
    return model.fit(train_ds, validation_data=val_ds, epochs=constants.FINE_TUNE_EPOCS,
                     class_weight=class_weights(), callbacks=callbacks())


def main():
    """run both phases and save the model into model/artifacts/."""
    keras.utils.set_random_seed(constants.SEED)

    constants.ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    constants.REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    train_ds, val_ds = build_datasets()
    model = build_model()
    model.summary()

    print("\n==== phase1: frozen backbone ====")
    head = train_head(model, train_ds, val_ds)
    print("\n==== phase 2: fine-tune ====")
    tune = fine_tune(model, train_ds, val_ds)
    model.save(constants.MODEL_PATH)
    print(f"saved {constants.MODEL_PATH}")

    def clean(history):
        return {k: [float(v) for v in vs] for k, vs in history.history.items()}

    (constants.REPORTS_DIR / "history.json").write_text(
        json.dumps({"head": clean(head), "fine_tune": clean(tune)}, indent=2)
    )


if __name__ == "__main__":
    main()
