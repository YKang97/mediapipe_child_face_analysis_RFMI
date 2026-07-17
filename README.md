# RFMI Extraction Framework for MediaPipe Child Facial Images

This repository provides the public executable demonstration of an RFMI extraction framework and reproducible workflow for distance-uncalibrated open-eye frontal child facial photographs.

The workflow converts an input image into MediaPipe Face Landmarker coordinates, coordinate-based overlay figures, a blinded manual quality-control template, relative facial morphology indices (RFMI), and simple descriptive output tables.

The repository is designed as the code companion for a pilot feasibility study. It uses one synthetic open-eye child facial image for demonstration only. No real child participant photographs, participant metadata, or study-level scoring records are included.

## Workflow Concept

The public repository separates the method into three layers:

1. **Core RFMI calculation workflow**: image preparation, MediaPipe Face Landmarker detection, landmark export, RFMI calculation, and table output.
2. **Visual quality-control workflow**: coordinate-based overlay figures and a blank blinded manual QC template for checking whether landmarks align with visible facial regions.
3. **Technical sensitivity analysis module**: image scaling and horizontal-mirroring sensitivity analyses are reported in the manuscript as technical sensitivity analyses. They are not required for every public demo run and are not included as real-study outputs in this repository.

This distinction is important: the repository demonstrates the executable RFMI workflow, while the manuscript reports the study-level feasibility and technical sensitivity results.

Additional reviewer-oriented details are provided in [`docs/methods_rfmi.md`](docs/methods_rfmi.md) and [`docs/reproducibility.md`](docs/reproducibility.md).

## Reviewer-Facing Public-Release Notes

This repository is intended to be reviewed as a transparent computational demo rather than as a release of participant-level research data. To make the public version auditable:

- the MediaPipe model URL and SHA256 hash are fixed in the preparation script;
- all overlay points and RFMI distance lines are generated from exported MediaPipe Face Landmarker coordinates;
- RFMI variables are study-defined relative image indices, not centimeter measurements and not official MediaPipe medical measurements;
- static preview figures and CSV tables are included only to show expected output structure from the synthetic image;
- real child facial images require ethics approval, consent, privacy protection, and data-governance review before processing or sharing.

## Six-Part Workflow Preview

The notebook is organized so that reviewers can see, step by step, what the code does and what each step produces.

![Six-part RFMI workflow overview](docs/figures/rfmi_six_part_overview.png)

## What Each Part Does

| Part | Code section | What the code does | What readers see after running it |
|---|---|---|---|
| Part 1 | Environment setup and synthetic input image | Imports Python packages, locates the repository root, and displays the clean synthetic open-eye image. | Printed project path and the AI-generated example image. |
| Part 2 | Manifest creation | Writes the image manifest for the one-subject public demo. | `outputs_manifest/manifest.csv` with subject ID, image state, and copied analysis path. |
| Part 3 | MediaPipe landmark detection | Runs MediaPipe Face Landmarker and exports raw coordinates. | `landmarks_raw.csv` with 478 landmark rows and `detection_log.csv`. |
| Part 4 | Overlay figures and QC template | Displays full-face landmarks, eye-region zoom, RFMI distance lines, and creates a blank blinded manual QC template. | Three overlay images plus `outputs_qc/qc_template.csv` and `outputs_qc/qc_score_codebook.csv`. |
| Part 5 | RFMI index calculation | Converts selected MediaPipe landmark coordinate groups into RFMI variables. | Image-level and subject-level RFMI tables. |
| Part 6 | Summary tables and output checklist | Creates descriptive RFMI summaries and lists expected output files. | `rfmi_subject_indices.csv`, `rfmi_summary.csv`, and an output checklist. |

## Example Input and Outputs

### Part 1 input: synthetic open-eye image

![Synthetic open-eye image](docs/figures/demo_synthetic_input.jpg)

### Part 4 output: full-face landmark overlay

![Full-face landmark overlay](docs/figures/demo_full_face_overlay.jpg)

### Part 4 output: eye-region landmark overlay

![Eye-region landmark overlay](docs/figures/demo_eye_zoom_overlay.jpg)

### Part 4 output: RFMI distance-line overlay

![RFMI distance-line overlay](docs/figures/demo_rfmi_lines_overlay.jpg)

### Part 5 output: subject-level RFMI table preview

![Subject-level RFMI table preview](docs/figures/demo_rfmi_subject_table.png)

### Part 6 output: descriptive RFMI summary preview

![RFMI summary table preview](docs/figures/demo_rfmi_summary_table.png)

The points and lines shown in the overlay figures are generated from MediaPipe landmark coordinates. They are not manually drawn landmarks.

## Repository Structure

```text
.
├── README.md
├── LICENSE
├── CITATION.cff
├── AI_IMAGE_DISCLOSURE.md
├── .python-version
├── requirements.txt
├── example_data/
│   └── images/
│       └── SYN_open.jpg
├── notebooks/
│   └── BIBE_RFMI_Image_to_Indices_Demo.ipynb
├── scripts/
│   ├── 01_prepare_project.py
│   ├── 02_detect_and_overlay.py
│   ├── 03_generate_qc_template.py
│   ├── 04_compute_rfmi.py
│   ├── 05_summarize_rfmi.py
│   └── 06_validate_public_demo.py
└── docs/
    ├── README.md
    ├── methods_rfmi.md
    ├── reproducibility.md
    ├── figures/
    │   ├── rfmi_six_part_overview.png
    │   ├── demo_synthetic_input.jpg
    │   ├── demo_full_face_overlay.jpg
    │   ├── demo_eye_zoom_overlay.jpg
    │   ├── demo_rfmi_lines_overlay.jpg
    │   ├── demo_rfmi_subject_table.png
    │   └── demo_rfmi_summary_table.png
    └── tables/
        ├── demo_qc_score_codebook.csv
        ├── demo_qc_template.csv
        ├── demo_rfmi_subject_indices.csv
        └── demo_rfmi_summary.csv
```

Generated folders such as `outputs_manifest/`, `outputs_landmarks/`, `outputs_overlay/`, `outputs_qc/`, `outputs_features/`, `outputs_stats/`, `models/`, and `logs/` are created when the notebook is run. They are not committed to the repository.

## How to Run

Use Python 3.13.9 in a clean environment with the pinned packages in `requirements.txt`. This is the computational environment used to generate the study outputs reported in the accompanying manuscript. On minimal Linux systems, MediaPipe/OpenCV may also require runtime libraries such as `libegl1`, `libgl1`, `libgles2`, and `libglib2.0-0`; see [`docs/reproducibility.md`](docs/reproducibility.md) for platform notes and model-download alternatives.

### Option 1: Jupyter notebook

Open:

```text
notebooks/BIBE_RFMI_Image_to_Indices_Demo.ipynb
```

Then run the notebook from top to bottom. The notebook is the recommended entry point because it displays the code, explanation, and output for each part.

The notebook automatically detects the repository root in common launch situations. If automatic detection fails, set `ROOT_OVERRIDE` in the first code cell to the local repository folder.

### Option 2: command line

From the repository root:

```bash
python scripts/01_prepare_project.py --root . --open-image example_data/images/SYN_open.jpg --child-id SYN
python scripts/02_detect_and_overlay.py --root .
python scripts/03_generate_qc_template.py --root .
python scripts/04_compute_rfmi.py --root .
python scripts/05_summarize_rfmi.py --root .
python scripts/06_validate_public_demo.py --root .
```

## Installation

Create a Python 3.13.9 environment and install the required packages:

```bash
python -m pip install -r requirements.txt
```

The locked direct dependencies are MediaPipe 0.10.35, Pillow 12.0.0, pandas 2.3.3, NumPy 2.3.3, Matplotlib 3.10.7, openpyxl 3.1.5, and Jupyter 1.1.1. The notebook prints and checks these versions before running the public demo. Set `INSTALL = True` only when packages are not already installed in the active Jupyter environment.

On Windows systems without long-path support, create the virtual environment in a short location such as `C:\venvs\rfmi`; installing the full Jupyter dependency set inside a deeply nested repository path can exceed the legacy path-length limit.

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

- 33-133 eye-region aperture index;
- 263-362 eye-region aperture index;
- mean eye aperture index;
- eye aperture asymmetry index;
- nose-width/face-width index;
- mouth-width/face-width index;
- jaw-width/face-width index;
- selected MediaPipe eye-state auxiliary scores.

The single-eye-region variables are named by MediaPipe landmark index groups rather than anatomical left/right eye labels. This avoids ambiguity caused by camera mirroring, software image flips, and viewer perspective.

All geometric RFMI values are computed from MediaPipe landmark coordinates. The RFMI formulas are study-defined features; they are not official MediaPipe medical measurements. The formulas, landmark indices, and interpretation limits are documented in [`docs/methods_rfmi.md`](docs/methods_rfmi.md).

## Blinded Manual Quality Control

The repository creates a blank QC template from the generated overlay files. The template is intended to help researchers review whether landmark overlays align with visible facial regions before using RFMI values in a study dataset.

The public demo does not contain real human ratings. For real child image studies, QC scoring should be performed under the study's ethics approval and data-protection plan.

## Data and Ethics

The included demonstration image is synthetic and AI-generated. It does not depict a real participant. Real child facial images and participant metadata should only be processed under appropriate ethics approval, consent, privacy protection, and data-governance procedures. The demo outputs are not clinical, diagnostic, or population-level study estimates.

## Citation

If you use this repository, please cite the repository using `CITATION.cff` and cite MediaPipe Face Landmarker according to the official MediaPipe documentation. For manuscripts, also report that the public demo uses one synthetic image and that RFMI variables are study-defined relative image indices.

## License

The code in this repository is released under the MIT License. See `LICENSE` for details.
