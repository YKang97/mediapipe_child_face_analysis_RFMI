# MediaPipe Child Face RFMI Demo

This repository provides a compact Jupyter-based demonstration for converting an open-eye frontal child facial image into MediaPipe Face Landmarker coordinates, coordinate-based overlay figures, relative facial morphology indices (RFMI), and simple descriptive output tables.

The repository is designed as the public code companion for a pilot feasibility study on distance-uncalibrated child frontal facial photographs. It uses a synthetic open-eye child facial image for demonstration only. No real child participant photographs, participant metadata, or study-level scoring records are included.

## What This Repository Shows

The notebook is intentionally simple. It is meant to show reviewers and readers what each computational step does and what files are produced after running it.

| Notebook section | Purpose | Main outputs |
|---|---|---|
| 1. Install and import libraries | Load the Python environment and required packages. | Python session with `mediapipe`, `pandas`, `numpy`, `Pillow`, and display tools. |
| 2. Prepare synthetic example image | Copy the synthetic image into a working folder and create a manifest. | `outputs_manifest/manifest.csv` |
| 3. Run MediaPipe and export coordinates | Run MediaPipe Face Landmarker and save raw landmark coordinates. | `outputs_landmarks/landmarks_raw.csv`, `outputs_landmarks/detection_log.csv` |
| 4. Inspect overlay images | Display coordinate-based full-face, eye-region, and RFMI-line overlays. | `outputs_overlay/full_face/`, `outputs_overlay/eye_zoom/`, `outputs_overlay/rfmi_lines/` |
| 5. Compute RFMI indices | Convert selected official MediaPipe landmark coordinates into relative facial morphology indices. | `outputs_features/rfmi_image_level.csv`, `outputs_features/rfmi_subject_level.csv` |
| 6. Create summary tables | Generate subject-level and descriptive RFMI tables. | `outputs_stats/tables/rfmi_subject_indices.csv`, `outputs_stats/tables/rfmi_summary.csv` |

## Demo Output Preview

The points and lines shown below are generated from MediaPipe landmark coordinates. They are not manually drawn landmarks.

### Full-face landmark overlay

![Full-face landmark overlay](docs/figures/demo_full_face_overlay.jpg)

### Eye-region landmark overlay

![Eye-region landmark overlay](docs/figures/demo_eye_zoom_overlay.jpg)

### RFMI distance-line overlay

![RFMI distance-line overlay](docs/figures/demo_rfmi_lines_overlay.jpg)

## Repository Structure

```text
.
├── README.md
├── LICENSE
├── CITATION.cff
├── AI_IMAGE_DISCLOSURE.md
├── requirements.txt
├── example_data/
│   └── images/
│       └── SYN_open.jpg
├── notebooks/
│   └── BIBE_RFMI_Image_to_Indices_Demo.ipynb
├── scripts/
│   ├── 01_prepare_project.py
│   ├── 02_detect_and_overlay.py
│   ├── 04_compute_rfmi.py
│   └── 05_summarize_rfmi.py
└── docs/
    ├── figures/
    │   ├── demo_full_face_overlay.jpg
    │   ├── demo_eye_zoom_overlay.jpg
    │   └── demo_rfmi_lines_overlay.jpg
    └── tables/
        ├── demo_rfmi_subject_indices.csv
        └── demo_rfmi_summary.csv
```

Generated folders such as `outputs_landmarks/`, `outputs_overlay/`, `outputs_features/`, `outputs_stats/`, `models/`, and `logs/` are created when the notebook is run. They are not committed to the repository.

## How to Run

### Option 1: Jupyter notebook

Open:

```text
notebooks/BIBE_RFMI_Image_to_Indices_Demo.ipynb
```

Then run the notebook from top to bottom.

The notebook automatically detects the repository root in common launch situations. If automatic detection fails, set `ROOT_OVERRIDE` in the first code cell to the local repository folder.

### Option 2: command line

From the repository root:

```bash
python scripts/01_prepare_project.py --root . --open-image example_data/images/SYN_open.jpg --child-id SYN
python scripts/02_detect_and_overlay.py --root .
python scripts/04_compute_rfmi.py --root .
python scripts/05_summarize_rfmi.py --root .
```

## Installation

Create a Python environment and install the required packages:

```bash
pip install -r requirements.txt
```

The notebook also includes an optional installation cell. Set `INSTALL = True` only when packages are not already installed in the active Jupyter environment.

## MediaPipe Model

The preparation script downloads or verifies a fixed MediaPipe Face Landmarker model:

```text
https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task
```

Expected SHA256:

```text
64184e229b263107bc2b804c6625db1341ff2bb731874b0bcc2fe6544e0bc9ff
```

Using a fixed model URL and hash improves reproducibility compared with using a moving latest-version model URL.

## RFMI Interpretation

RFMI values are relative image indices, not centimeter measurements. They are designed for distance-uncalibrated frontal photographs when the goal is to describe within-face proportional morphology.

The current demo calculates:

- right and left eye aperture indices;
- mean eye aperture index;
- eye aperture asymmetry index;
- nose-width/face-width index;
- mouth-width/face-width index;
- jaw-width/face-width index;
- selected MediaPipe eye-related blendshape scores.

All geometric RFMI values are computed from MediaPipe landmark coordinates. The RFMI formulas are study-defined features; they are not official MediaPipe medical measurements.

## Data and Ethics

The included demonstration image is synthetic and AI-generated. It does not depict a real participant. Real child facial images and participant metadata should only be processed under appropriate ethics approval, consent, and privacy protection procedures.

## Citation

If you use this repository, please cite the repository using `CITATION.cff` and cite MediaPipe Face Landmarker according to the official MediaPipe documentation.

## License

The code in this repository is released under the MIT License. See `LICENSE` for details.
