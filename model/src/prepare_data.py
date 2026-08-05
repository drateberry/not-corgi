"""Assemble the three-class dataset and split it into train / val / test.

Per specifications.md section 4.1, the dataset is built from the Stanford Dogs
Dataset for the two corgi breeds, extended with sampled images from Google Open
Images for the Not_Corgi negative class.

Reads from   model/data/raw/
Writes into  model/data/processed/{train,val,test}/{Cardigan,Not_Corgi,Pembroke}/

Binding constraint (spec section 5.5): the test set is held out and untouched.
Splits must be disjoint at the image level, and augmentation must happen after
splitting, never before. Augmentation belongs in train.py, not here.
"""

# TODO: imports


def load_raw_index():
    """Walk model/data/raw/ and return every source image with its class label.

    TODO: implement.
    """
    raise NotImplementedError


def find_near_duplicates(paths):
    """Identify duplicate / near-duplicate images before splitting.

    Spec section 6 flags an accuracy at or near 99% on the breed distinction as
    evidence of data leakage rather than success, with duplicates spanning the
    train/test boundary as the most likely cause. Catching them here is cheaper
    than diagnosing them after training.

    TODO: implement (e.g. perceptual hashing, then group by hash distance).
    """
    raise NotImplementedError


def split(index):
    """Partition into train / val / test, disjoint at the image level.

    Near-duplicate groups must land entirely within a single split, or the
    leakage this is meant to prevent survives the split.

    TODO: implement.
    """
    raise NotImplementedError


def write_splits(splits):
    """Copy images into model/data/processed/<split>/<class>/.

    TODO: implement.
    """
    raise NotImplementedError


def main():
    """TODO: wire the steps above together and report per-class counts per split."""
    raise NotImplementedError


if __name__ == "__main__":
    main()
