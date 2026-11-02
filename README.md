# Classifier-Correction Reuse after INT8 Recalibration

**Accuracy Retention and the Value of Shared Fitting**  
Vishwaram Reddy · Manuscript revision 2 · October 15, 2026

[Read the paper](main.pdf) · [LaTeX source](main.tex) · [Results](evidence/all-accuracies.csv) · [Experiment process](docs/EXPERIMENT_PROCESS.md) · [Reproduction guide](docs/REPRODUCIBILITY.md)

This repository contains the completed empirical study of reusing a small classifier correction after INT8 recalibration. It includes the manuscript, original experiment code, fitted corrections, complete compact prediction evidence, and the code that reconstructs the reported statistics.

**Status:** completed research manuscript; not submitted or published. No arXiv identifier, peer-reviewed acceptance, or new correction algorithm is claimed. The later objective-comparison experiments are outside this manuscript and repository.

## Question and finding

Can a correction fitted on one or several source calibrations retain accuracy when the same pretrained model is quantized using different calibration samples?

We test MobileNetV2 and ResNet18 with seven methods, five target calibrations per model in host simulation, and two targets per model on a Snapdragon NPU. All configurations are evaluated on the same 7,000 ImageNetV2 images.

Both single-source reuse and shared fitting meet the preset **observed** 0.5-percentage-point accuracy-loss budget relative to target refitting in this panel. Shared fitting does **not** show a consistent additional accuracy advantage:

| Native comparison: Shared minus Single | Mean difference (percentage points) | 95% conditional interval |
|---|---:|---:|
| MobileNetV2 | +0.043 | [−0.086, +0.171] |
| ResNet18 | −0.107 | [−0.221, 0.000] |

These are pointwise paired class-bootstrap intervals conditional on the tested calibrations. They do not prove equivalence, population noninferiority, inference speedup or energy savings. All methods, targets and unfavorable outcomes are retained.

![Primary accuracy comparisons with paired uncertainty](figures/primary-effects.png)

## Reproduce the reported statistics

Use Python 3.10 and an environment with the dependencies below:

```bash
python -m pip install -r requirements.txt
python verify_evidence.py
```

Expected result:

```text
PASS: 98 accuracy cells, 126 paired bootstrap intervals, both FP32 references, and inventory hashes.
```

This works with the included evidence and NumPy; no GPU, dataset download, QAIRT installation, or phone is needed. It verifies the reported statistics from saved predictions. It does not rerun inference or independently authenticate private phone acquisition.

To regenerate the tables and figure into a separate output directory:

```bash
python -m pip install -r requirements-render.txt
python scripts/reproduce.py --render
```

The command preserves the released paper/evidence and writes to `build/reproduced/`. To compile the regenerated manuscript, with TeX Live/latexmk or Tectonic installed:

```bash
bash build/reproduced/manuscript/build.sh
```

The included `main.pdf` is the unchanged final manuscript, so compilation is optional.

## Repository contents

| Location | Contents |
|---|---|
| `main.pdf`, `main.tex`, `author.tex`, `references.bib`, `main.bbl` | Final paper and editable source |
| `tables/`, `figures/` | All manuscript tables and the primary-results figure |
| `verify_evidence.py`, `render_results.py`, `scripts/reproduce.py` | Statistical verification and figure/table regeneration |
| `evidence/predictions.npz` | All 70 host and 28 native configurations, both FP32 references, labels and top-score tie multiplicities |
| `evidence/fits/` | All saved scale/shift and bias correction parameters |
| `evidence/protocol.json`, `*.csv` | Frozen study design, dataset split identities and full result tables |
| `evidence/audit-public.json`, `provenance.json`, `inventory.json` | Anonymized audit summary, source hashes and immutable evidence inventory |
| `code/scripts/`, `code/runner/` | Original Python/PowerShell/shell experiment pipeline and C++ native runner source |
| `evidence/source/` | Unchanged source snapshot covered by the original evidence inventory |
| `environment/` | Recorded host/SDK Python environments and external asset URLs/hashes |
| `docs/` | Method details, reproduction scope, source-copy provenance and release checks |
| `MANIFEST.sha256` | Checksums of the repository's released files |

The original experiment code is archived with its workspace-relative assumptions. [Full inference requirements](docs/REPRODUCIBILITY.md#rerunning-model-inference) describe the additional data, pretrained models, caches, SDK and device work. This repository provides complete statistical reproduction and archived experiment source; it is not a one-command hardware replay installer.

## Citation and terms

See [CITATION.cff](CITATION.cff). Cite this as an unpublished manuscript unless a later public publication record is added.

No repository-wide reuse license has been selected. [NOTICE.md](NOTICE.md) records the scope and external dependency terms. Dataset images, pretrained weights, proprietary SDK/runtime binaries, private raw phone returns and credentials are not included; their relevant provenance or acquisition instructions are provided.
