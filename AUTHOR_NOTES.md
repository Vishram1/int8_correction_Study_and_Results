# Correction-reuse study — revision 2 for author review

**Author: Vishwaram Reddy.** This is the second editorial revision of the final-study manuscript, dated 15 October 2026. [Revision notes](REVISION_NOTES.md) describe the stronger practical framing and unchanged evidence. Nothing has been submitted, accepted, or published. No affiliation has been invented; add one only if appropriate and authorized.

The measured question is whether fitting one classifier correction across three source INT8 calibrations improves reuse on excluded recalibrations. Native shared-minus-single accuracy averages +0.043 pp for MobileNetV2 and −0.107 pp for ResNet18, with conditional intervals that include zero. Both Single and Shared met the preset observed loss budget relative to target refitting on every tested target and folded without additional graph operators. The study demonstrates no consistent shared-fitting advantage in this setting; the practical benefits of reuse apply to both methods. It does not prove equivalence or claim a new compensation algorithm, inference speedup, or energy saving.

## Files

- `main.pdf`: manuscript, including all host/native accuracy cells and primary/secondary comparisons.
- `main.tex`, `author.tex`, `references.bib`, `main.bbl`, `tables/`, `figures/`: editable LaTeX source and generated tables/figure.
- `evidence/predictions.npz`: ordered predicted class indices and top-maximum multiplicities for 70 host configurations, 28 native configurations, and two FP32 references; exact labels included. There are 7,000 unique test images, reused across configurations.
- `evidence/expected-statistics.json`: numerical results from the frozen analysis.
- `evidence/verified-statistics.json`: independently checked statistics, including correct/tied counts and improved/harmed image counts.
- `evidence/all-accuracies.csv`, `all-target-contrasts.csv`: complete machine-readable tables.
- `evidence/protocol.json`, split CSVs, `source/`, `fits/`: frozen design, image identities (not image pixels), archived project scripts, and fitted correction vectors.
- `evidence/cost-records.json`, `native-structure.json`, `feature-diagnostics.json`: preparation-stage records, native IR summaries, and descriptive source-feature diagnostics.
- `evidence/audit-public.json`: sanitized derivative of canonical private audit records. Literal serials are omitted; validation/final identity linkage, setup limitations, and thermal ranges remain disclosed.
- `evidence/provenance.json`, `inventory.json`: original full-output and audit hashes, plus compact evidence hashes.

## Reproduce the statistics

Python 3.10 and NumPy 1.26.4 were used. In the extracted evidence package:

```bash
python verify_evidence.py --output evidence/verified-statistics.json
```

Expected result: **98 accuracy cells and 126 paired-bootstrap intervals pass**, plus both FP32 references and all inventory checks. The verifier independently implements the frozen 10,000-resample class bootstrap, seed 2026101499. It pairs the same seven images per class across arms and targets. Intervals are pointwise and conditional on the observed calibrations, not calibration-population or simultaneous confidence statements.

The arrays have shape `[model, target, arm, image]`; FP32 arrays have `[model, image]`. Model/arm/target order and hashes are in `provenance.json`. `*_ties` stores the number of equal top scores for each observation. Predictions use NumPy's first-index argmax. A tie observation means multiplicity greater than one. No alternative tie rule was selected after evaluation.

With Matplotlib installed:

```bash
python render_results.py
bash build.sh
```

`render_results.py` consumes verified statistics. `build.sh` accepts TeX Live with latexmk, Tectonic on PATH, or the local cached Tectonic installation. The source-only archive already includes the generated tables, figure PDF, and bibliography; it does not need the evidence package to compile. Statistical reproduction needs the separate evidence archive.

## What these files verify

The compact supplement independently reproduces reported statistics. It does not rerun model inference or independently authenticate phone acquisition. The full float output arrays and original phone files remain in the private research workspace and are linked by hashes. Native validation passed all 84 jobs with bitwise runner/reference agreement and 336 HTP events. Final acquisition passed all 1,960 jobs, with 196,000 model–image outputs. All 70 host configurations completed.

Full inference reproduction additionally requires the ImageNetV2 images, exact pretrained model artifacts, AIMET/ONNX dependencies, QAIRT 2.45.41.260507, and a compatible Android device. Those image/model/SDK/runtime files are not redistributed here. The frozen experiment scripts document the original workspace implementation and refer to prior experiment paths; they are not a standalone inference installer.

No literal phone serials are included. The current validation/final share one recorded identity/build; continuity with earlier handsets is unconfirmed. Operator-assumed equivalent conditions are not represented as measured controls. The original raw records are preserved without changing their hashes.

## Author actions remaining

1. Read the manuscript and verify that you can explain the fitting objective, classifier folding, re-encoding control, data roles, paired uncertainty, and negative/mixed conclusion. Correct any factual setup description you can substantiate.
2. Review the cited prior work and confirm the modest empirical framing. This is a completed study, not a demonstrated new accuracy-improvement algorithm.
3. Add an appropriate affiliation/contact if desired and decide the destination and publication license. Check model/data/SDK redistribution permissions before releasing additional artifacts.
4. Submit the reviewed manuscript and selected artifacts through your own account. For arXiv, complete account/category/license/endorsement requirements if requested by its submission workflow. Moderation and acceptance are not guaranteed.
5. Use “completed research project / manuscript” now, “submitted” only after submission, and “arXiv preprint” only once a public identifier exists. A preprint is not peer-reviewed acceptance.

No additional phone runs are needed to finish this fixed study. A new claim or a changed method would need separately planned evaluation; these final images have now been used.
