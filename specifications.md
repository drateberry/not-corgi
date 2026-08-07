# Not Corgi — Project Specification

> **Purpose of this document.** This is the authoritative specification for the Not Corgi project, reflecting the proposal approved by CS50 staff. It exists so that work in progress can be checked against what was actually proposed. When implementation and this document disagree, that is a signal — either the implementation has drifted, or the spec needs to be revised deliberately and the change acknowledged.

---

## 1. Project Summary

**Not Corgi** is a mobile application that uses a custom-trained image classification model to identify whether a captured photo shows a Pembroke Welsh Corgi, a Cardigan Welsh Corgi, or neither ("Not Corgi"). The concept is a deliberate homage to the "Not Hotdog" app from HBO's *Silicon Valley*.

This is a CS50 final project, built individually. It draws on machine learning theory from CS80 but is **not** a combined submission — it satisfies CS50's requirements alone.

---

## 2. Why This Problem Is Non-Trivial

The choice of Pembroke vs. Cardigan is deliberate and central to the project's value. These are two distinct breeds that are genuinely difficult to tell apart, which makes this a **fine-grained classification** problem rather than a routine multi-class one.

Distinguishing features:

| Feature | Pembroke | Cardigan |
|---|---|---|
| Tail | Commonly docked or naturally bobbed | Long, full tail |
| Ears | Smaller, more pointed | Larger, more rounded |
| Coat colors | Red, sable, fawn, tricolor | Includes brindle and blue merle |
| Build | Lighter boned | Slightly larger, heavier boned |

**The tail is the strongest visual signal and it is frequently not visible.** Many photographs crop or occlude the tail entirely. This imposes a real ceiling on achievable accuracy that cannot be trained past, and understanding that ceiling is a core intellectual contribution of the project — it belongs in `DESIGN.md`.

---

## 3. Scope: Good / Better / Best

These outcomes were committed to in the approved proposal and define the boundaries of scope.

### GOOD — will be accomplished regardless
- A trained image classifier distinguishing the three classes.
- A Flask API layer that accepts a photo and returns class probabilities plus a Grad-CAM heatmap.

### BETTER — expected to be accomplished
- A React Native mobile application wrapping the API, providing camera capture and result display.

### BEST — hoped for, explicitly a stretch goal
- Conversion of the trained model to TensorFlow Lite / LiteRT for on-device inference, allowing the app to function with weak or absent connectivity.

**Scope discipline:** the server-based inference path is the primary implementation. On-device inference is attempted only after the full pipeline works end to end. If the two conflict, the working pipeline wins. Descoping the stretch goal is an acceptable outcome; descoping it silently is not — the decision and its rationale belong in `DESIGN.md`.

---

## 4. Architecture

Three components, built in this dependency order.

### 4.1 Model (TensorFlow / Keras)

- **Approach:** transfer learning from a backbone pretrained on ImageNet (MobileNetV3 class of model), not training from scratch.
- **Head:** GlobalAveragePooling2D → Dropout → Dense(3, softmax).
- **Training:** two phases — (1) frozen backbone, train the new head at a higher learning rate; (2) unfreeze the top portion of the backbone and fine-tune at a low learning rate (~1e-5).
- **Data:** three-class dataset assembled from the Stanford Dogs Dataset for the two corgi breeds, extended with sampled images from Google Open Images for the negative class.
- **Augmentation:** random horizontal flip, rotation, zoom, color jitter. **No vertical flips** — dogs are not upside down.
- **Explainability:** Grad-CAM visualization, used to verify the model attends to tails, ears, and coat coloration rather than background artifacts.

### 4.2 API (Flask)

- Loads the trained model and exposes a prediction endpoint accepting image upload.
- Returns class probabilities for all three classes and a Grad-CAM heatmap overlay image.
- **Runs locally** — served from the developer's machine on the local network, reachable by the phone at the host's LAN address. *(Revised Aug 6; see below.)*
- Inference runs on CPU — no GPU dependency for anyone testing the project.

> **REVISION (Aug 6, 2026) — cloud deployment removed.**
> This bullet previously read *"Deployed to a cloud host so the mobile client can
> reach it over cellular data."* The API now runs locally only.
>
> **What this does not change:** section 3's GOOD tier commits to "a Flask API
> layer that accepts a photo and returns class probabilities plus a Grad-CAM
> heatmap" and says nothing about hosting. The committed scope is intact; this is
> an architecture decision, not a descope.
>
> **Rationale.** A hosted URL stops being reachable the moment the deployment
> lapses, which makes the project unreproducible for anyone evaluating it after
> the deadline. Running from source keeps it executable indefinitely. Secondarily,
> full TensorFlow plus a 27.5 MB model is a poor fit for free-tier hosting, and
> cold-start latency is a live risk in the section 9 demo setting.
>
> **What this obligates.** Local-only means the API must be *runnable by someone
> else*, so `README.md` carries the burden a deployment URL would have: exact run
> steps, and a working route to obtain the trained model (see section 7).
>
> Per section 7.2 this decision and its rationale belong in `DESIGN.md`.

Consequences that are now binding:

- The Flask server must bind `0.0.0.0`, not the `127.0.0.1` default. Bound to loopback it is unreachable from the phone, and the failure looks like a network problem rather than a configuration one.
- The API base URL is a LAN address that changes with the network. It must be configurable without a code edit — hardcoding it guarantees a mid-demo code change.
- `GET /health` is now the mechanism for confirming the phone can see the host before filming, not merely a liveness check.

### 4.3 Mobile App (React Native / Expo)

- Camera interface for photo capture, plus the option to select an existing photo from the library.
- Sends the image to the API as multipart form data.
- Results screen: a prominent verdict (Corgi / Not Corgi), the specific breed determination, all three class probabilities, and a toggleable Grad-CAM heatmap overlay.
- Must handle network failure gracefully — the intended demo environment is a dog park, with the phone and the API host sharing a personal-hotspot network (see section 4.2 revision).
- Runs on Expo Go for the server-based path. Adding a native ML runtime for on-device inference would require a development build; this is a reason the stretch goal is scoped last.

---

## 5. Binding Technical Constraints

These are decisions already made. Deviating from them is a drift signal, not a free choice.

1. **Framework is TensorFlow/Keras, not PyTorch.** This was chosen specifically because the Keras → TFLite export path is short, which is what makes the on-device stretch goal reachable at all. The approved proposal states TensorFlow. Building in PyTorch would contradict the submitted proposal.

2. **Class indices are alphabetical:** `Cardigan=0`, `Not_Corgi=1`, `Pembroke=2`. Keras's `image_dataset_from_directory` assigns labels by sorted folder name. This mapping must be hardcoded consistently across training, API, and app. Mismatches here scramble labels silently with no error.

3. **Do not double-normalize.** Recent Keras versions bake preprocessing into MobileNetV3. Calling `preprocess_input` on top of a model that already rescales destroys accuracy with no visible error.

4. **Recompile after changing `trainable`.** When unfreezing backbone layers for phase-two fine-tuning, the model must be recompiled. Skipping this fails silently and is the single most common fine-tuning bug in Keras.

5. **The test set is held out and untouched.** Splits must be disjoint at the image level, and augmentation must occur after splitting, never before.

---

## 6. Evaluation Standard

**Accuracy alone is not an acceptable evaluation.** A model that identifies "Not Corgi" perfectly while confusing Pembrokes with Cardigans can still report a high aggregate number while failing at the actual task.

Required:
- A **confusion matrix** over the held-out test set.
- Per-class precision and recall.

**Expected performance:** corgi vs. not-corgi should reach the high 90s without difficulty. Pembroke vs. Cardigan in the **mid-80s is a respectable result**.

**A reported accuracy at or near 99% on the breed distinction should be treated as evidence of data leakage, not success.** The most likely causes are duplicate or near-duplicate images spanning the train/test boundary, or augmentation applied before splitting. This must be investigated rather than reported at face value.

---

## 7. Required Deliverables

Due **Friday, August 7, 2026 at 11:59 AM EDT**. Extensions are not granted.

1. **`README.md`** — a user's manual. Several paragraphs minimum. Must make it unambiguous how to configure, run, and test the project. Must include the demo video URL. Written so that staff never need to ask a follow-up question.
2. **`DESIGN.md`** — a technical design document. Several paragraphs minimum. Explains *how* the project was implemented and *why* each design decision was made. This is the right home for: the tail-occlusion accuracy ceiling, the TensorFlow-over-PyTorch decision, the server-side-over-on-device decision, dataset assembly tradeoffs, and what Grad-CAM revealed about model attention.
3. **All source code**, thoroughly commented, plus any configuration files needed to run the project.
4. **A demo video**, under 3 minutes, uploaded to YouTube as public or unlisted, with the URL in `README.md`. Must include the project title, name and year, dorm/house and concentration.

**Submission constraint:** the ZIP should stay under ~15MB. Omit the dataset and any large assets.

**Model distribution (added Aug 6).** The section 4.2 revision to local-only execution creates an obligation that a hosted API would have absorbed: staff must be able to obtain the trained model in order to run anything. `not_corgi.keras` is 27.5 MB — over the ZIP budget and gitignored, so at present no path exists by which an evaluator gets it. `instructions.md` permits linking files publicly from `README.md`. This must be resolved before submission; until it is, the project is not runnable by anyone but its author, which defeats the stated rationale for going local.

---

## 8. Academic Honesty Boundary

CS50 permits the use of AI tools for the final project — and only the final project — but states that **the essence of the work must remain the student's own**. These tools are to amplify productivity, not substitute for it.

Practically, for any assistant working on this project: explaining concepts, reviewing code, catching bugs, suggesting approaches, and pressure-testing decisions are all appropriate. Authoring the substance of the project is not. If a request would result in the assistant having written the project rather than the student, that is worth naming directly rather than quietly complying.

---

## 9. Demo Context

The demonstration video is intended to be filmed at a dog park with live dogs, using the app on a physical iPhone. Two consequences for implementation:

- **Network reliability is a functional requirement, not a nicety.** With the API running locally (section 4.2 revision), the hotspot is no longer a fallback — it is the primary and only transport. The laptop must be physically present at the park and joined to the iPhone's personal hotspot, putting both devices on one network so the phone can reach the host's LAN address. This is not an added burden: Expo Go already requires the laptop on the same network to serve the JS bundle. Three things to verify *before* leaving: the host firewall permits inbound connections to Python, `GET /health` answers from the phone over the hotspot, and the API base URL matches the hotspot-assigned address.
- **Class coverage matters for the demo.** Pembrokes dominate at dog parks. A demo that only ever encounters one breed does not actually demonstrate the fine-grained classification that the project is about.