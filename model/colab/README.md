# Training on Google Colab from VS Code

Training the classifier on a MacBook Air means CPU-only TensorFlow and epoch times
measured in tens of minutes. This directory offloads training to a Google Colab GPU
runtime while you keep editing in VS Code.

- [`train_colab.ipynb`](./train_colab.ipynb) — the driver notebook. Clones the repo onto
  the Colab VM and runs `model/src/*.py` unchanged.
- [`../requirements-colab.txt`](../requirements-colab.txt) — Colab-side dependencies
  (only what a stock Colab image lacks).

Nothing in `model/src/` needed to change for this, and nothing in it is Colab-aware.
That is deliberate: one implementation of the training code, under version control,
that runs the same way in both places.

---

## The one thing to understand first

The Colab VS Code extension puts a **remote kernel** behind a **local editor**. Your
notebook file lives on your Mac; the Python process executing its cells lives on a VM
in Google's datacenter.

That means **the Colab runtime cannot see your local filesystem.** Not your dataset,
not your `model/src/` edits, not anything. `pd.read_csv("localfile.csv")` fails, and
`google.colab.files.upload()` does not work in the extension either. This is a known,
currently-open limitation, not something you have misconfigured
([issue #223](https://github.com/googlecolab/colab-vscode/issues/223)).

So there are exactly two channels between your Mac and the runtime, and the whole
setup is built around them:

| What | Channel | Mechanism |
|---|---|---|
| **Code** | GitHub | you push; the notebook's clone/pull cell fetches |
| **Data & results** | Google Drive | mounted into the runtime at `/content/drive` |

Corollary worth internalising: **an unpushed edit is not running.** If you change
`train.py` and re-run the training cell without committing and pushing first, Colab
trains the old code and gives you no indication that it did.

---

## One-time setup

### 1. Install the extension

In VS Code, open Extensions (`Cmd+Shift+X`), search **Google Colab**, and install the
official one — publisher **Google**, extension ID `google.colab`. It is built on top of
Microsoft's Jupyter extension, so accept the prompt to install that dependency if you
do not already have it.

### 2. Connect a runtime

Open [`train_colab.ipynb`](./train_colab.ipynb) in VS Code. Click **Select Kernel** at
the top right, choose **Colab**, and sign in with the Google account whose Drive holds
the dataset. Pick a GPU runtime rather than CPU.

The free tier gives you an NVIDIA T4, which is entirely adequate for fine-tuning a
MobileNetV3 on a dataset this size. Colab Pro adds faster GPUs and longer sessions; you
should not need it for this project.

You will know it worked when the kernel indicator shows a Colab runtime and cell 2
prints `nvidia-smi` output.

### 3. Put the dataset in Drive

The notebook expects a single archive at `MyDrive/not-corgi/data/raw.zip`, unzipping to
class folders at the archive root:

```
Cardigan/
Not_Corgi/
Pembroke/
```

One archive rather than a folder of loose images is a performance decision. The Drive
mount is FUSE-backed and slow per file; copying one large archive to the VM's local SSD
and unzipping it there takes seconds, while reading thousands of individual JPEGs
through the mount every epoch will leave the GPU idle waiting on I/O.

If you already have the raw images locally:

```sh
cd model/data/raw
zip -r ../raw.zip .        # note the "." — class folders must be at the archive root
```

then upload `model/data/raw.zip` to `MyDrive/not-corgi/data/` and delete the local copy.

If you have not assembled the dataset yet, the alternative is to download the sources
(Stanford Dogs for the two corgi breeds, Open Images for the negative class) *inside*
Colab and write the archive to Drive from there — a several-hundred-megabyte download
over Google's network is far faster than over yours. Either way, assembling and
splitting the data is `prepare_data.py`'s job, not the notebook's.

The notebook creates the rest of the Drive layout itself on first run:

```
MyDrive/not-corgi/
├── data/raw.zip        <- you provide this
├── artifacts/          <- trained model lands here
└── reports/            <- confusion matrix, figures, run logs
```

---

## The working loop

Once set up, a normal iteration is:

1. Edit `model/src/*.py` in VS Code, locally, with full IntelliSense and git.
2. Commit and push.
3. In the notebook, re-run **cell 4 (Get the code)** — it fast-forwards the clone.
4. Re-run the training cell.

Cells 1–6 are setup and are idempotent; after a disconnect, run them top to bottom
again and they will skip the work that is already done (the dataset stays unzipped on
the VM if the VM survived, and re-unpacks if it did not).

### Where things end up

Cell 6 replaces four directories inside the Colab clone with symlinks:

| Repo path | Points at | Why |
|---|---|---|
| `model/data/raw/` | local SSD | unzipped from the Drive archive |
| `model/data/processed/` | local SSD | read every epoch — must be fast |
| `model/artifacts/` | Drive | must survive the VM being recycled |
| `model/reports/` | Drive | figures `DESIGN.md` cites |

This is why the training code needs no Colab branch: `train.py` writes to
`model/artifacts/` exactly as it does on your Mac, and the file lands in Drive.

### Getting results back

Trained weights: download from `MyDrive/not-corgi/artifacts/` into `api/artifacts/` on
your Mac. They travel by Drive, not git — `artifacts/` and `model/data/` are gitignored
to keep the submission ZIP under ~15MB (specifications.md §7).

Reports: `model/reports/` is **not** gitignored, and its contents are what `DESIGN.md`
references. Download and commit those.

---

## Things that will bite you

**Runtimes are disposable.** Idle runtimes disconnect after roughly 90 minutes, and
Colab can reclaim a session mid-epoch. Have `train.py` write a `ModelCheckpoint` into
`model/artifacts/` — which is Drive — so a disconnect costs you minutes rather than the
whole run. Training output is teed into `model/reports/*.log` for the same reason: if
the runtime vanishes, the log of how far it got is still in Drive.

**Verify you got a GPU.** A runtime with no accelerator trains happily, just slowly,
and it is easy not to notice until you are an hour in. Cell 2 exists for this.

**Versions are part of the result.** specifications.md §5.3 — whether MobileNetV3 bakes
rescaling into the graph, and therefore whether calling `preprocess_input` silently
destroys your accuracy — depends on the TensorFlow version the runtime happens to hand
you. Colab upgrades its base image without asking. The verification cell prints the
versions and probes for baked-in preprocessing on every run; once a run produces a
model you intend to keep, record those versions in `requirements-colab.txt`.

**Don't edit code in the Colab clone.** `/content/not-corgi` is wiped with the VM, and
the pull cell uses `--ff-only` so local commits there will make it fail rather than
merge. Edit on your Mac, push, pull.

**Secrets.** Colab's `userdata.get()` is not wired up in the VS Code extension. Nothing
in the training path needs a secret, so this only matters if you later add one.

---

## Troubleshooting

| Symptom | Cause |
|---|---|
| `FileNotFoundError` on a path you can see in Finder | The runtime cannot see your Mac. Data goes via Drive, code via git. |
| Training uses old code | You didn't push, or didn't re-run the pull cell. Check the commit hash cell 4 prints. |
| `git pull` fails in cell 4 | Something was committed inside the Colab clone. Delete `/content/not-corgi` and re-run to re-clone. |
| Epochs slow, GPU near idle | Data pipeline bound, not compute bound. Confirm cell 6 linked `processed/` to local SSD and not to Drive; add `cache()`/`prefetch()`. |
| `unzip` cell raises `FileNotFoundError` | `raw.zip` isn't at `MyDrive/not-corgi/data/`. See "Put the dataset in Drive". |
| Accuracy far worse than the CPU run | Check the double-normalization probe in the verification cell against what `train.py` assumes. |

---

## Sources

- [Google Colab is Coming to VS Code — Google Developers Blog](https://developers.googleblog.com/google-colab-is-coming-to-vs-code/)
- [googlecolab/colab-vscode](https://github.com/googlecolab/colab-vscode) — extension repo
- [Issue #223 — uploading local files to Colab servers](https://github.com/googlecolab/colab-vscode/issues/223)
- [Issue #210 — accessing local files from the Colab kernel](https://github.com/googlecolab/colab-vscode/issues/210)
