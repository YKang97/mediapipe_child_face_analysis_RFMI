# Reproducibility Checklist

This checklist summarizes what can be reproduced from the repository and what is intentionally excluded for privacy and ethics reasons.

## Repository scope

Included:

- source code for preparing the demo image, running MediaPipe Face Landmarker, drawing coordinate-based overlays, creating a blank blinded quality-control template, computing RFMI variables, and creating summary tables;
- one synthetic, AI-generated open-eye child face image for demonstration;
- static preview figures and CSV tables generated from the synthetic image;
- method documentation, citation metadata, license, and AI-image disclosure files.

Excluded:

- real child participant photographs;
- participant metadata;
- consent records;
- diagnostic labels, clinical scores, or study-level statistical datasets;
- downloaded MediaPipe model binaries, because the preparation script downloads or verifies the fixed model file;
- real blinded QC ratings, because they belong to the protected study dataset.

## Recommended Python environment

The public demonstration workflow was tested with the following locked environment:

| Component | Version |
|---|---:|
| Python | 3.13.9 |
| MediaPipe | 0.10.35 |
| Pillow | 12.0.0 |
| pandas | 2.3.3 |
| NumPy | 2.3.3 |
| Matplotlib | 3.10.7 |
| openpyxl | 3.1.5 |
| Jupyter | 1.1.1 |

Use Python 3.13.9 to create a clean environment before installing the pinned dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

On Windows, create the virtual environment in a short path to avoid the legacy path-length limit that can affect Jupyter dependencies, then activate it with:

```powershell
python -m venv C:\venvs\rfmi
C:\venvs\rfmi\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

The `.python-version` and `requirements.txt` files are the authoritative environment specification for this repository. A run with substituted package versions should be documented as a different environment rather than treated as identical.

## Linux system dependencies

MediaPipe depends on OpenCV-related binary libraries. On minimal Linux containers, importing MediaPipe may fail if system graphical libraries are missing. On Ubuntu-like systems, install the relevant runtime libraries before running the detection step:

```bash
sudo apt-get update
sudo apt-get install -y libegl1 libgl1 libgles2 libglib2.0-0
```

The exact package names may differ by distribution.

## MediaPipe model reproducibility

The preparation script uses a fixed Face Landmarker model URL and verifies the file against a fixed SHA256 hash. If network access to Google Cloud Storage is blocked, download the model separately in an approved environment and pass it to the preparation script:

```bash
python scripts/01_prepare_project.py \
  --root . \
  --open-image example_data/images/SYN_open.jpg \
  --child-id SYN \
  --model-source /path/to/face_landmarker.task
```

The script will copy the local model and verify its SHA256 hash before downstream steps run.

## Command-line reproduction

From the repository root, run:

```bash
python scripts/01_prepare_project.py --root . --open-image example_data/images/SYN_open.jpg --child-id SYN
python scripts/02_detect_and_overlay.py --root .
python scripts/03_generate_qc_template.py --root .
python scripts/04_compute_rfmi.py --root .
python scripts/05_summarize_rfmi.py --root .
python scripts/06_validate_public_demo.py --root .
```

The notebook provides the same workflow in a step-by-step format.

## Expected generated outputs

The main generated outputs are intentionally ignored by Git and should appear after running the workflow:

| Path | Expected content |
|---|---|
| `outputs_manifest/manifest.csv` | One public demo row for `SYN_open`. |
| `outputs_landmarks/landmarks_raw.csv` | MediaPipe landmark coordinate rows for successfully detected faces. |
| `outputs_landmarks/blendshapes_raw.csv` | Selected MediaPipe blendshape outputs when returned by the model. |
| `outputs_landmarks/detection_log.csv` | Image dimensions, detection status, and overlay paths. |
| `outputs_overlay/full_face/` | Full-face coordinate overlay images. |
| `outputs_overlay/eye_zoom/` | Eye-region coordinate overlay images. |
| `outputs_overlay/rfmi_lines/` | RFMI distance-line overlay images. |
| `outputs_qc/qc_template.csv` | Blank blinded manual QC template generated from overlay paths. |
| `outputs_qc/qc_score_codebook.csv` | Score definitions for the public QC template. |
| `outputs_features/rfmi_image_level.csv` | Image-level RFMI outputs. |
| `outputs_features/rfmi_subject_level.csv` | Subject-level RFMI outputs. |
| `outputs_stats/tables/rfmi_subject_indices.csv` | Public-format subject-level RFMI table. |
| `outputs_stats/tables/rfmi_summary.csv` | Descriptive demo summary table. |

Because the public repository uses one synthetic image, summary statistics demonstrate table structure only and are not study estimates.

## Lightweight repository validation

`python scripts/06_validate_public_demo.py --root .` performs checks that do not require MediaPipe or model downloads. It verifies that required public files are present, documentation contains key cautionary language, the notebook JSON is parseable, and the static preview CSV files contain the expected demo columns.

This validator is not a replacement for running the full MediaPipe workflow. It checks repository structure, documentation safeguards, environment pins, notebook structure, and static demo tables.

The GitHub Actions workflow installs the locked environment and runs the complete six-script synthetic demonstration before applying this lightweight validation. This end-to-end check does not use or expose participant data.

## Limitations to report

When applying or describing this workflow, report the following limitations clearly:

- RFMI features are study-defined relative image indices, not official MediaPipe medical measurements.
- The public demo has one synthetic image only and cannot support clinical, diagnostic, or population-level claims.
- Landmark quality can be affected by pose, lighting, occlusion, image resolution, camera perspective, facial expression, and model version.
- Real child facial data require ethics approval, consent, privacy protection, and data-governance review before processing or sharing.
