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
import random
from collections import defaultdict
import shutil
import json
import imagehash
from PIL import Image

import constants

VALID_FILES = {".jpg", ".jpeg"}

def load_raw_index():
    """Walk model/data/raw/ and return every source image with its class label. """
    records = []
    for label in constants.CLASS_NAMES:
        folder = constants.RAW_DIR / label
        if not folder.is_dir():
            raise FileNotFoundError(f"missing category folder: {folder}")
        for path in sorted(folder.iterdir()):
            if path.name.startswith("."):
                continue
            if path.suffix.lower() not in VALID_FILES:
                continue
            records.append({"path": path, "label": label, "group": None})
    return records


def find_near_duplicates(paths, threshold=constants.PHASH_THRESHOLD):
    """Identify duplicate / near-duplicate images before splitting.

    Spec section 6 flags an accuracy at or near 99% on the breed distinction as
    evidence of data leakage rather than success, with duplicates spanning the
    train/test boundary as the most likely cause. Catching them here is cheaper
    than diagnosing them after training.

    PRECEDENT: this is the same failure mode as the GTSRB "track" problem from
    CS80/week5/traffic — ~30 near-identical frames of each physical sign, split
    randomly, so frames of one sign landed in both train and test and the 99.88%
    test accuracy was optimistic relative to real generalization. That project's
    spec forbade changing the split, so the fix was left as future work. This
    project owns the whole pipeline, so it gets fixed here.

    The corgi equivalent of a "track" is a set of photos of the same individual
    dog, or the same photo reposted at different sizes/crops across sources.
    Stanford Dogs and Open Images both contain these.
    """
    hashes = []
    for path in paths:
        with Image.open(path) as im:
            hashes.append(imagehash.phash(im.convert("RGB")))
    def is_similar(i, j):
        return hashes[i] - hashes[j] <= threshold
    
    parent = list(range(len(paths)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i
    
    def union(i, j):
        ri, rj = find(i), find(j)
        if ri != rj:
            parent[ri] = rj

    for i in range(len(paths)):
        for j in range(i + 1, len(paths)):
            if is_similar(i, j):
                union(i, j)
    groups = {}
    for i in range(len(paths)):
        groups.setdefault(find(i), []).append(paths[i])

    return list(groups.values())


def split(index):
    """Partition into train / val / test, disjoint at the image level.

    Near-duplicate groups must land entirely within a single split, or the
    leakage this is meant to prevent survives the split.

    Splits must be deterministic under constants.SEED and written to disk once.
    Re-deriving the split at training time means a re-run can reshuffle images
    across the test boundary, which silently destroys the held-out guarantee in
    spec section 5.5 — a real risk now that training may run on Colab, where
    re-running a cell is cheap and casual.

   """
    rng = random.Random(constants.SEED)
    splits = {"train": [], "val": [], "test": []}

    by_class = defaultdict(lambda: defaultdict(list))
    for rec in index:
        by_class[rec["label"]][rec["group"]].append(rec)

    for label in sorted(by_class):
        groups = [by_class[label][g] for g in sorted(by_class[label])]
        rng.shuffle(groups)

        n = sum(len(g) for g in groups)
        want_test = round(n * constants.TEST_SPLIT)
        want_val = round(n * constants.VAL_SPLIT)

        n_test = n_val = 0
        for group in groups:
            if n_test < want_test:
                splits["test"].extend(group)
                n_test += len(group)
            elif n_val < want_val:
                splits["val"].extend(group)
                n_val += len(group)
            else:
                splits["train"].extend(group)

    return splits




def write_splits(splits):
    """Copy images into model/data/processed/<split>/<class>/.
    """
    proc = constants.PROC_DIR

    # clear any previous output
    for split_name in ("train", "val", "test"):
        for label in constants.CLASS_NAMES:
            dest_dir = proc/ split_name / label
            dest_dir.mkdir(parents=True, exist_ok=True)
            for stale in dest_dir.iterdir():
                if stale.suffix.lower() in VALID_FILES:
                    stale.unlink()
    for split_name, records in splits.items():
        for rec in records:
            shutil.copy2(rec["path"], proc / split_name / rec["label"] / rec["path"].name)

    manifest = {
        name: sorted(r["path"].relative_to(constants.RAW_DIR).as_posix() for r in records)
        for name, records in splits.items()
    }
    (proc / "splits.json").write_text(json.dumps(manifest, indent=2))


def main():
    index = load_raw_index()
    print(f"indexed {len(index)} images")
    by_path = {rec["path"]: rec for rec in index}
    groups = find_near_duplicates([r["path"] for r in index])
    for gid, group in enumerate(groups):
        for path in group:
            by_path[path]["group"] = gid
    # Account for near-duplicate pair straddling two classes
    for group in groups:
        labels = {by_path[p]["label"] for p in group}
        assert len(labels) == 1, f"group spans classes {labels}: {[p.name for p in group]}"

    dupes = [g for g in groups if len(g) > 1]
    print(f"{len(groups)} groups, {len(dupes)} with near-duplicates")
    for g in dupes:
        print("  " + ", ".join(p.name for p in g))
    splits = split(index)

    paths = {k: {r["path"] for r in v} for k, v in splits.items()}
    assert not (paths["train"] & paths["test"])
    assert not (paths["train"] & paths["val"])
    assert not (paths["val"] & paths["test"])
    assert sum(len(v) for v in splits.values()) == len(index)

    write_splits(splits)

    print(f"\n{'class':<12}{'train':>7}{'val':>7}{'test':>7}{'total':>7}")
    for label in constants.CLASS_NAMES:
        row = [sum(1 for r in splits[s] if r["label"] == label)
               for s in ("train", "val", "test")]
        print(f"{label:<12}{row[0]:>7}{row[1]:>7}{row[2]:>7}{sum(row):>7}")



if __name__ == "__main__":
    main()
