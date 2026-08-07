# Not Corgi — Design Document

TODO — write the technical tour. Per `specifications.md` §7 this document is the
required home for the following discussions, each of which was committed to in the
approved proposal:

- **The tail-occlusion accuracy ceiling.** Why Pembroke vs. Cardigan has a hard
  performance limit that cannot be trained past, and what that implies for the
  reported numbers.
- **TensorFlow over PyTorch.** Chosen for the short Keras → TFLite export path,
  which is what makes the on-device stretch goal reachable at all.
- **Server-side inference over on-device.** Whether the TFLite stretch goal was
  attempted, reached, or descoped — and the rationale either way. §3 of the spec
  requires that descoping be stated explicitly, never done silently.
- **Dataset assembly tradeoffs.** Stanford Dogs for the two corgi classes,
  sampled Google Open Images for the negative class; class balance, split
  methodology, and how near-duplicate leakage was checked for.
- **What Grad-CAM revealed about model attention.** Whether the model attends to
  tails, ears, and coat coloration, or to background artifacts.
- **Evaluation.** The confusion matrix and per-class precision/recall, not just
  aggregate accuracy (§6).

## How I utilized AI
For the completion of "Not Corgi" I used Anthropic's Claude Code within VSCode in the following ways:
- Creating the scaffolding and boilerplate of files
- Design of the UI for the React Native app
- Validation of final project against original proposal

All uses of Claude are disclosed in the commits on Github where Claude is noted as a co-author of specific commits.